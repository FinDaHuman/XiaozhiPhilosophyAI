"""Shared Groq-primary, Gemini-fallback text generation provider."""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Iterator, Sequence
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors
from google.genai import types
from groq import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    Groq,
    InternalServerError,
    RateLimitError,
)

load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-lite"
DEFAULT_GROQ_TIMEOUT_SECONDS = 12.0
DEFAULT_GEMINI_SERVER_RETRY_DELAY_SECONDS = 1.0


class LLMConfigurationError(RuntimeError):
    """Raised when neither LLM provider has a configured API key."""


class EmptyProviderResponse(RuntimeError):
    """Raised when a provider succeeds but returns no text."""


def is_transient_groq_error(exc: Exception) -> bool:
    """Return whether a Groq failure is safe to retry through Gemini."""
    if isinstance(
        exc,
        (
            RateLimitError,
            APIConnectionError,
            APITimeoutError,
            InternalServerError,
            EmptyProviderResponse,
        ),
    ):
        return True
    return isinstance(exc, APIStatusError) and exc.status_code >= 500


class LLMProvider:
    """Generate with Groq first and use Gemini for transient Groq failures."""

    def __init__(
        self,
        *,
        groq_api_key: str | None = None,
        gemini_api_key: str | None = None,
        gemini_model: str | None = None,
        groq_timeout_seconds: float | None = None,
    ):
        self.groq_api_key = (
            os.getenv("GROQ_API_KEY") if groq_api_key is None else groq_api_key
        )
        self.gemini_api_key = (
            os.getenv("GEMINI_API_KEY") if gemini_api_key is None else gemini_api_key
        )
        self.gemini_model = gemini_model or os.getenv(
            "GEMINI_MODEL", DEFAULT_GEMINI_MODEL
        )
        self.groq_timeout_seconds = groq_timeout_seconds or float(
            os.getenv("GROQ_TIMEOUT_SECONDS", str(DEFAULT_GROQ_TIMEOUT_SECONDS))
        )
        self._groq_client: Groq | None = None
        self._gemini_client: genai.Client | None = None

    @property
    def groq_client(self) -> Groq:
        if not self.groq_api_key:
            raise LLMConfigurationError("GROQ_API_KEY is not configured")
        if self._groq_client is None:
            self._groq_client = Groq(
                api_key=self.groq_api_key,
                max_retries=0,
                timeout=self.groq_timeout_seconds,
            )
        return self._groq_client

    @property
    def gemini_client(self) -> genai.Client:
        if not self.gemini_api_key:
            raise LLMConfigurationError("GEMINI_API_KEY is not configured")
        if self._gemini_client is None:
            # The SDK defaults to five attempts, including retries for 429.
            # Keep retries under application control so free-tier quota cannot
            # be consumed by hidden retry loops.
            self._gemini_client = genai.Client(
                api_key=self.gemini_api_key,
                http_options=types.HttpOptions(
                    retry_options=types.HttpRetryOptions(attempts=1)
                ),
            )
        return self._gemini_client

    def complete(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        groq_model: str | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.3,
    ) -> str:
        """Return one complete response, falling back before surfacing errors."""
        if self.groq_api_key:
            try:
                return self._complete_groq(
                    messages,
                    model=groq_model or os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL),
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
            except Exception as exc:
                if not self.gemini_api_key or not is_transient_groq_error(exc):
                    raise
                logger.warning(
                    "Groq generation failed with %s; falling back to Gemini model %s",
                    type(exc).__name__,
                    self.gemini_model,
                )

        if self.gemini_api_key:
            return self._complete_gemini(
                messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        raise LLMConfigurationError(
            "No LLM provider is configured; set GROQ_API_KEY or GEMINI_API_KEY"
        )

    def stream(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        groq_model: str | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.3,
    ) -> Iterator[str]:
        """Stream Groq, or Gemini if Groq fails before its first output token."""
        if self.groq_api_key:
            emitted = False
            try:
                stream = self.groq_client.chat.completions.create(
                    model=groq_model or os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL),
                    messages=list(messages),
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                )
                for chunk in stream:
                    text = chunk.choices[0].delta.content
                    if text:
                        emitted = True
                        yield text
                return
            except Exception as exc:
                if emitted or not self.gemini_api_key or not is_transient_groq_error(exc):
                    raise
                logger.warning(
                    "Groq stream failed before its first token with %s; "
                    "falling back to Gemini model %s",
                    type(exc).__name__,
                    self.gemini_model,
                )

        if self.gemini_api_key:
            yield from self._stream_gemini(
                messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return
        raise LLMConfigurationError(
            "No LLM provider is configured; set GROQ_API_KEY or GEMINI_API_KEY"
        )

    def _complete_groq(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        model: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        completion = self.groq_client.chat.completions.create(
            model=model,
            messages=list(messages),
            temperature=temperature,
            max_tokens=max_tokens,
        )
        answer = completion.choices[0].message.content or ""
        if not answer.strip():
            raise EmptyProviderResponse("Groq returned an empty response")
        return answer

    def _complete_gemini(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        max_tokens: int,
        temperature: float,
    ) -> str:
        system_instruction, contents = self._to_gemini_contents(messages)
        for attempt in range(2):
            try:
                response = self.gemini_client.models.generate_content(
                    model=self.gemini_model,
                    contents=contents,
                    config=self._gemini_config(
                        system_instruction,
                        max_tokens=max_tokens,
                        temperature=temperature,
                    ),
                )
                answer = response.text or ""
                if not answer.strip():
                    raise EmptyProviderResponse("Gemini returned an empty response")
                return answer
            except genai_errors.ServerError:
                if attempt == 1:
                    raise
                logger.warning(
                    "Gemini returned a server error; retrying once after a short delay"
                )
                time.sleep(DEFAULT_GEMINI_SERVER_RETRY_DELAY_SECONDS)

        raise AssertionError("unreachable")

    def _stream_gemini(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        max_tokens: int,
        temperature: float,
    ) -> Iterator[str]:
        system_instruction, contents = self._to_gemini_contents(messages)
        for attempt in range(2):
            emitted = False
            try:
                for chunk in self.gemini_client.models.generate_content_stream(
                    model=self.gemini_model,
                    contents=contents,
                    config=self._gemini_config(
                        system_instruction,
                        max_tokens=max_tokens,
                        temperature=temperature,
                    ),
                ):
                    text = chunk.text or ""
                    if text:
                        emitted = True
                        yield text
                if not emitted:
                    raise EmptyProviderResponse("Gemini returned an empty stream")
                return
            except genai_errors.ServerError:
                if emitted or attempt == 1:
                    raise
                logger.warning(
                    "Gemini stream returned a server error before its first token; "
                    "retrying once after a short delay"
                )
                time.sleep(DEFAULT_GEMINI_SERVER_RETRY_DELAY_SECONDS)

    @staticmethod
    def _to_gemini_contents(
        messages: Sequence[dict[str, Any]],
    ) -> tuple[str, list[types.Content]]:
        system_parts: list[str] = []
        contents: list[types.Content] = []
        for message in messages:
            role = str(message.get("role", "user"))
            text = str(message.get("content", ""))
            if role == "system":
                system_parts.append(text)
                continue
            gemini_role = "model" if role == "assistant" else "user"
            contents.append(
                types.Content(
                    role=gemini_role,
                    parts=[types.Part.from_text(text=text)],
                )
            )
        return "\n\n".join(system_parts), contents

    @staticmethod
    def _gemini_config(
        system_instruction: str,
        *,
        max_tokens: int,
        temperature: float,
    ) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            system_instruction=system_instruction or None,
            max_output_tokens=max_tokens,
            temperature=temperature,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )
