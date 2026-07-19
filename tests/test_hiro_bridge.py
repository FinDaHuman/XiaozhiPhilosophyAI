import os
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException

from app.api.routes import ChatRequest, HistoryTurn, chat_hiro


class HiroBridgeTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_token_fails_without_calling_upstream(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(HTTPException) as raised:
                await chat_hiro(ChatRequest(message="Xin chào", history=[]))
        self.assertEqual(raised.exception.status_code, 503)

    async def test_history_and_secret_are_forwarded_server_side(self):
        upstream = SimpleNamespace(
            status_code=200,
            json=lambda: {"reply": "Câu trả lời từ Hiro"},
        )
        session = MagicMock()
        session.post = AsyncMock(return_value=upstream)
        client_context = MagicMock()
        client_context.__aenter__ = AsyncMock(return_value=session)
        client_context.__aexit__ = AsyncMock(return_value=None)

        with (
            patch.dict(
                os.environ,
                {
                    "DAC_HIRO_INTERNAL_TOKEN": "shared-secret",
                    "DAC_HIRO_API_URL": "https://example.test/internal/hiro",
                },
                clear=True,
            ),
            patch("app.api.routes.httpx.AsyncClient", return_value=client_context),
        ):
            response = await chat_hiro(
                ChatRequest(
                    message="Câu mới",
                    history=[HistoryTurn(question="Câu cũ", answer="Trả lời cũ")],
                )
            )

        self.assertEqual(response.answer, "Câu trả lời từ Hiro")
        _, kwargs = session.post.call_args
        self.assertEqual(kwargs["headers"], {"x-hiro-token": "shared-secret"})
        self.assertEqual(
            kwargs["json"]["messages"],
            [
                {"role": "user", "content": "Câu cũ"},
                {"role": "assistant", "content": "Trả lời cũ"},
                {"role": "user", "content": "Câu mới"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
