import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx
from google.genai import errors as genai_errors
from groq import APITimeoutError, AuthenticationError, RateLimitError

from app.rag.llm_provider import LLMConfigurationError, LLMProvider
from app.rag.pipeline import RAGPipeline
from app.rag.prompts import VOICE_SYSTEM_PROMPT
from app.rag.voice import normalize_dac_pronunciation, sanitize_voice_answer


MESSAGES = [
    {"role": "system", "content": "Answer briefly."},
    {"role": "user", "content": "Question"},
]


def status_error(error_class, status_code):
    request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    response = httpx.Response(status_code, request=request)
    return error_class("provider error", response=response, body={"error": {}})


def groq_completion(text):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=text))]
    )


def groq_stream_chunk(text):
    return SimpleNamespace(
        choices=[SimpleNamespace(delta=SimpleNamespace(content=text))]
    )


class LLMProviderTests(unittest.TestCase):
    def provider_with_fakes(self):
        provider = LLMProvider(groq_api_key="groq", gemini_api_key="gemini")
        provider._groq_client = MagicMock()
        provider._gemini_client = MagicMock()
        return provider

    def test_groq_success_does_not_call_gemini(self):
        provider = self.provider_with_fakes()
        provider._groq_client.chat.completions.create.return_value = groq_completion(
            "groq answer"
        )

        answer = provider.complete(MESSAGES)

        self.assertEqual(answer, "groq answer")
        provider._gemini_client.models.generate_content.assert_not_called()

    def test_rate_limit_falls_back_to_gemini(self):
        provider = self.provider_with_fakes()
        provider._groq_client.chat.completions.create.side_effect = status_error(
            RateLimitError, 429
        )
        provider._gemini_client.models.generate_content.return_value = SimpleNamespace(
            text="gemini answer"
        )

        answer = provider.complete(MESSAGES)

        self.assertEqual(answer, "gemini answer")

    def test_timeout_falls_back_to_gemini(self):
        provider = self.provider_with_fakes()
        request = httpx.Request("POST", "https://api.groq.com")
        provider._groq_client.chat.completions.create.side_effect = APITimeoutError(
            request=request
        )
        provider._gemini_client.models.generate_content.return_value = SimpleNamespace(
            text="gemini answer"
        )

        self.assertEqual(provider.complete(MESSAGES), "gemini answer")

    def test_authentication_error_does_not_fallback(self):
        provider = self.provider_with_fakes()
        provider._groq_client.chat.completions.create.side_effect = status_error(
            AuthenticationError, 401
        )

        with self.assertRaises(AuthenticationError):
            provider.complete(MESSAGES)
        provider._gemini_client.models.generate_content.assert_not_called()

    def test_missing_groq_key_uses_gemini_directly(self):
        provider = LLMProvider(groq_api_key="", gemini_api_key="gemini")
        provider._gemini_client = MagicMock()
        provider._gemini_client.models.generate_content.return_value = SimpleNamespace(
            text="gemini direct"
        )

        self.assertEqual(provider.complete(MESSAGES), "gemini direct")

    def test_missing_both_keys_is_a_configuration_error(self):
        provider = LLMProvider(groq_api_key="", gemini_api_key="")

        with self.assertRaises(LLMConfigurationError):
            provider.complete(MESSAGES)

    @patch("app.rag.llm_provider.genai.Client")
    def test_gemini_sdk_hidden_retries_are_disabled(self, client_class):
        provider = LLMProvider(groq_api_key="", gemini_api_key="gemini")

        _ = provider.gemini_client

        http_options = client_class.call_args.kwargs["http_options"]
        self.assertEqual(http_options.retry_options.attempts, 1)

    @patch("app.rag.llm_provider.time.sleep")
    def test_gemini_server_error_retries_once(self, sleep):
        provider = LLMProvider(groq_api_key="", gemini_api_key="gemini")
        provider._gemini_client = MagicMock()
        provider._gemini_client.models.generate_content.side_effect = [
            genai_errors.ServerError(503, {"error": {"message": "busy"}}),
            SimpleNamespace(text="gemini recovered"),
        ]

        self.assertEqual(provider.complete(MESSAGES), "gemini recovered")
        self.assertEqual(provider._gemini_client.models.generate_content.call_count, 2)
        sleep.assert_called_once()

    @patch("app.rag.llm_provider.time.sleep")
    def test_gemini_rate_limit_does_not_retry(self, sleep):
        provider = LLMProvider(groq_api_key="", gemini_api_key="gemini")
        provider._gemini_client = MagicMock()
        provider._gemini_client.models.generate_content.side_effect = (
            genai_errors.ClientError(429, {"error": {"message": "quota"}})
        )

        with self.assertRaises(genai_errors.ClientError):
            provider.complete(MESSAGES)
        provider._gemini_client.models.generate_content.assert_called_once()
        sleep.assert_not_called()

    def test_stream_falls_back_before_first_token(self):
        provider = self.provider_with_fakes()
        provider._groq_client.chat.completions.create.side_effect = status_error(
            RateLimitError, 429
        )
        provider._gemini_client.models.generate_content_stream.return_value = [
            SimpleNamespace(text="gemini "),
            SimpleNamespace(text="stream"),
        ]

        self.assertEqual(list(provider.stream(MESSAGES)), ["gemini ", "stream"])

    def test_stream_does_not_mix_providers_after_first_token(self):
        provider = self.provider_with_fakes()
        request = httpx.Request("POST", "https://api.groq.com")

        def broken_stream():
            yield groq_stream_chunk("partial")
            raise APITimeoutError(request=request)

        provider._groq_client.chat.completions.create.return_value = broken_stream()

        stream = provider.stream(MESSAGES)
        self.assertEqual(next(stream), "partial")
        with self.assertRaises(APITimeoutError):
            next(stream)
        provider._gemini_client.models.generate_content_stream.assert_not_called()

    def test_gemini_message_conversion_preserves_system_and_history(self):
        system, contents = LLMProvider._to_gemini_contents(
            [
                {"role": "system", "content": "persona"},
                {"role": "user", "content": "first"},
                {"role": "assistant", "content": "answer"},
                {"role": "user", "content": "second"},
            ]
        )

        self.assertEqual(system, "persona")
        self.assertEqual([content.role for content in contents], ["user", "model", "user"])


class VoiceSanitizerTests(unittest.TestCase):
    def test_backend_voice_pipeline_normalizes_llm_output(self):
        pipeline = RAGPipeline.__new__(RAGPipeline)
        pipeline.llm = MagicMock()
        pipeline.llm.complete.return_value = (
            "Theo [Slide 5], DongAnhCapital là nền tảng AI tại donganhcapital.com."
        )
        pipeline.retriever = MagicMock()
        pipeline.retriever.retrieve.return_value = []
        pipeline._conversation_history = []

        answer = pipeline.ask("Đông Anh Capital là gì?", voice=True)

        self.assertEqual(
            answer,
            "Theo tài liệu Đông Anh Capital, Đông Anh Capital là nền tảng AI tại Đông Anh Capital chấm com.",
        )
        messages = pipeline.llm.complete.call_args.args[0]
        self.assertEqual(messages[0]["content"], VOICE_SYSTEM_PROMPT)

    def test_written_citations_and_markdown_become_spoken_text(self):
        answer = sanitize_voice_answer(
            "**Ý chính:** Theo [DongAnhCapital]. Nguồn [Slide KTCT 12]."
        )

        self.assertEqual(
            answer,
            "Ý chính: theo tài liệu Đông Anh Capital. Nguồn theo slide kinh tế chính trị 12.",
        )
        self.assertNotIn("[", answer)
        self.assertNotIn("**", answer)

    def test_duplicate_spoken_citation_prefix_is_collapsed(self):
        answer = sanitize_voice_answer("Theo theo [DongAnhCapital], nền tảng miễn phí.")

        self.assertEqual(
            answer,
            "Theo tài liệu Đông Anh Capital, nền tảng miễn phí.",
        )

    def test_terminal_citation_is_attached_to_previous_sentence(self):
        answer = sanitize_voice_answer(
            "Hiro trả lời bằng dữ liệu thật. Theo [DongAnhCapital]."
        )

        self.assertEqual(
            answer,
            "Hiro trả lời bằng dữ liệu thật theo tài liệu Đông Anh Capital.",
        )

    def test_all_brand_spellings_become_the_spoken_name(self):
        variants = (
            "DongAnh Capital",
            "Donganh Capital",
            "Dong Anh Capital",
            "DongAnhCapital",
            "DonganhCapital",
            "donganhcapital",
            "ĐôngAnh Capital",
            "Đông Anh Capital",
        )

        for variant in variants:
            with self.subTest(variant=variant):
                self.assertEqual(
                    normalize_dac_pronunciation(variant),
                    "Đông Anh Capital",
                )

    def test_public_domain_becomes_spoken_words(self):
        variants = (
            "donganhcapital.com",
            "DongAnhCapital.com",
            "https://donganhcapital.com",
            "https://www.donganhcapital.com",
            "https://donganhcapital.com/pricing",
        )

        for variant in variants:
            with self.subTest(variant=variant):
                self.assertEqual(
                    sanitize_voice_answer(f"Xem tại {variant}."),
                    "Xem tại Đông Anh Capital chấm com.",
                )

    def test_brand_normalization_is_idempotent(self):
        once = sanitize_voice_answer(
            "Theo [DongAnhCapital], xem tại donganhcapital.com."
        )
        twice = sanitize_voice_answer(once)

        self.assertEqual(
            once,
            "Theo tài liệu Đông Anh Capital, xem tại Đông Anh Capital chấm com.",
        )
        self.assertEqual(twice, once)

    def test_voice_prompt_requires_the_same_spoken_contract(self):
        self.assertIn('luôn viết chính xác "Đông Anh Capital"', VOICE_SYSTEM_PROMPT)
        self.assertIn('viết "Đông Anh Capital chấm com"', VOICE_SYSTEM_PROMPT)

    def test_backend_voice_pipeline_removes_duplicate_dac_citations(self):
        pipeline = RAGPipeline.__new__(RAGPipeline)
        pipeline.llm = MagicMock()
        pipeline.llm.complete.return_value = (
            "Đông Anh Capital không phải quỹ, theo tài liệu Đông Anh Capital, "
            "quyết định thuộc về nhà đầu tư, theo tài liệu Đông Anh Capital."
        )
        pipeline.retriever = MagicMock()
        pipeline.retriever.retrieve.return_value = []
        pipeline._conversation_history = []

        answer = pipeline.ask("Đông Anh Capital có phải quỹ không?", voice=True)

        self.assertEqual(answer.lower().count("theo tài liệu đông anh capital"), 1)
        self.assertNotIn(", .", answer)
        self.assertNotIn(". ,", answer)


if __name__ == "__main__":
    unittest.main()
