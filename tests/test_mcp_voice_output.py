"""Regression tests for text returned to the XiaoZhi hardware agent."""

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np


MCP_DIR = Path(__file__).resolve().parents[1] / "mcp"
if str(MCP_DIR) not in sys.path:
    sys.path.insert(0, str(MCP_DIR))

import mcp_rag  # noqa: E402
import rag_pipeline_faiss  # noqa: E402


RAW_DAC_PATTERN = re.compile(r"\bdong\s*anh\s*capital\b", re.IGNORECASE)


class MCPVoiceOutputTests(unittest.TestCase):
    def setUp(self):
        self.original_cache = mcp_rag._dac_cache.copy()

    def tearDown(self):
        mcp_rag._dac_cache = self.original_cache

    def assert_spoken_brand_is_safe(self, text: str) -> None:
        self.assertIsNone(RAW_DAC_PATTERN.search(text), text)
        self.assertNotIn("donganhcapital.com", text.lower())

    def test_faiss_voice_pipeline_normalizes_llm_output(self):
        contexts = [
            (rag_pipeline_faiss.Chunk(source="test", text="Nội dung thử."), 1.0)
        ]
        with (
            patch.object(rag_pipeline_faiss, "retrieve", return_value=contexts),
            patch.object(rag_pipeline_faiss.LLMProvider, "complete") as complete,
        ):
            complete.return_value = "Theo [Slide 5], DongAnh Capital tại donganhcapital.com."
            answer = rag_pipeline_faiss.ask("Đông Anh Capital là gì?")

        self.assertEqual(
            answer,
            "Theo tài liệu Đông Anh Capital, Đông Anh Capital tại Đông Anh Capital chấm com.",
        )
        messages = complete.call_args.args[0]
        self.assertIn("CÂU TRẢ LỜI CỦA BẠN ĐƯỢC ĐỌC THÀNH TIẾNG", messages[1]["content"])
        self.assert_spoken_brand_is_safe(answer)

    def test_faiss_ambiguous_query_retrieves_only_dac_chunks(self):
        vectorizer = MagicMock()
        vectorizer.transform.return_value.astype.return_value.toarray.return_value = (
            np.array([[1.0]], dtype=np.float32)
        )
        faiss_index = MagicMock()
        faiss_index.ntotal = 3
        faiss_index.search.return_value = (
            np.array([[0.9, 0.8, 0.7]], dtype=np.float32),
            np.array([[0, 1, 2]], dtype=np.int64),
        )
        index = {
            "vectorizer": vectorizer,
            "faiss_index": faiss_index,
            "chunks": [
                rag_pipeline_faiss.Chunk("data/Slide_KTCT_OCR.md", "Slide cũ"),
                rag_pipeline_faiss.Chunk(
                    "data/DongAnhCapital_KnowledgeBase.md", "Giới thiệu DAC"
                ),
                rag_pipeline_faiss.Chunk("data/Slide_OCR.md", "MLN111 cũ"),
            ],
        }

        with patch.object(rag_pipeline_faiss, "load_index", return_value=index):
            result = rag_pipeline_faiss.retrieve("Giới thiệu phần trọng điểm")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0].text, "Giới thiệu DAC")
        vectorizer.transform.assert_called_once_with(
            ["Đông Anh Capital Giới thiệu phần trọng điểm"]
        )

    def test_rag_answer_rechecks_backend_output_at_mcp_boundary(self):
        with patch.object(
            mcp_rag,
            "_ask_web_backend",
            return_value="Theo DongAnhCapital, xem tại donganhcapital.com.",
        ):
            answer = mcp_rag.rag_answer("Giới thiệu nền tảng")

        self.assertEqual(
            answer,
            "Theo tài liệu Đông Anh Capital, xem tại Đông Anh Capital chấm com.",
        )
        self.assert_spoken_brand_is_safe(answer)

    def test_versioned_disk_cache_is_normalized_when_loaded(self):
        payload = {
            "version": mcp_rag.DAC_CACHE_VERSION,
            "responses": {
                "dac_ai_signals_today": (
                    "Tín hiệu của DongAnh Capital. Xem tại donganhcapital.com."
                )
            },
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / ".dac_cache.json"
            cache_path.write_text(json.dumps(payload), encoding="utf-8")
            with patch.object(mcp_rag, "DAC_CACHE_FILE", cache_path):
                mcp_rag._dac_cache_load()

        cached = mcp_rag._dac_cache_get("dac_ai_signals_today")
        self.assertEqual(
            cached,
            "Tín hiệu của Đông Anh Capital. Xem tại Đông Anh Capital chấm com.",
        )
        self.assert_spoken_brand_is_safe(cached)

    def test_unversioned_ascii_cache_is_rejected(self):
        legacy = {"dac_vnindex": "VNINDEX phien cu."}
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / ".dac_cache.json"
            cache_path.write_text(json.dumps(legacy), encoding="utf-8")
            with patch.object(mcp_rag, "DAC_CACHE_FILE", cache_path):
                mcp_rag._dac_cache_load()

        self.assertEqual(mcp_rag._dac_cache, {})

    def test_stale_fallback_rechecks_legacy_in_memory_cache(self):
        mcp_rag._dac_cache = {
            "dac_vnindex": "Du lieu cua DonganhCapital tai donganhcapital.com."
        }

        answer = mcp_rag._dac_fallback("dac_vnindex")

        self.assertIn("Đông Anh Capital", answer)
        self.assertIn("Đông Anh Capital chấm com", answer)
        self.assert_spoken_brand_is_safe(answer)

    def test_vnindex_tool_returns_voice_safe_text(self):
        rows = [
            {"Date": "2026-07-18", "Close": 1780.0, "Volume": 400_000_000},
            {"Date": "2026-07-19", "Close": 1790.0, "Volume": 450_000_000},
        ]
        with (
            patch.object(mcp_rag, "_dac_get", return_value=rows),
            patch.object(mcp_rag, "_dac_cache_put"),
        ):
            answer = mcp_rag.dac_vnindex()

        self.assertIn("phiên 2026-07-19", answer)
        self.assertIn("tăng 10.00 điểm", answer)
        self.assert_spoken_brand_is_safe(answer)

    def test_ai_signals_tool_returns_canonical_brand_and_domain(self):
        summary = [{"date": "2026-07-19", "signal_count": 1}]
        detail = {
            "signals": [
                {
                    "stock_id": "FPT",
                    "entry_price": 100,
                    "tp_price": 110,
                    "sl_price": 95,
                }
            ]
        }
        with (
            patch.object(mcp_rag, "_dac_get", side_effect=[summary, detail]),
            patch.object(mcp_rag, "_dac_cache_put"),
        ):
            answer = mcp_rag.dac_ai_signals_today()

        self.assertIn("của Đông Anh Capital", answer)
        self.assertIn("Đông Anh Capital chấm com", answer)
        self.assert_spoken_brand_is_safe(answer)

    def test_market_movers_tool_returns_spoken_domain(self):
        rows = [
            {"ticker": "AAA", "value": 4.2, "trading_value": 2_000_000},
            {"ticker": "BBB", "value": -3.1, "trading_value": 3_000_000},
        ]
        with (
            patch.object(mcp_rag, "_dac_get", return_value=rows),
            patch.object(mcp_rag, "_dac_cache_put"),
        ):
            answer = mcp_rag.dac_market_movers()

        self.assertIn("Dữ liệu từ Đông Anh Capital chấm com", answer)
        self.assert_spoken_brand_is_safe(answer)


if __name__ == "__main__":
    unittest.main()
