import unittest
from unittest.mock import MagicMock, PropertyMock, patch

from langchain_core.documents import Document

from app.rag.retriever import PhilosophyRetriever


class RetrieverFallbackTests(unittest.TestCase):
    def test_multiquery_failure_uses_base_retriever(self):
        retriever = PhilosophyRetriever.__new__(PhilosophyRetriever)
        multiquery = MagicMock()
        multiquery.invoke.side_effect = RuntimeError("provider unavailable")
        base = MagicMock()
        expected = Document(
            page_content="DongAnh Capital fallback context",
            metadata={"source": "DongAnhCapital_KnowledgeBase.md"},
        )
        base.invoke.return_value = [expected]
        retriever._base_retriever = base

        with patch.object(
            PhilosophyRetriever,
            "retriever_pipeline",
            new_callable=PropertyMock,
            return_value=multiquery,
        ):
            result = retriever.retrieve("DongAnh Capital là gì?")

        self.assertEqual(result, [expected])
        base.invoke.assert_called_once_with("DongAnh Capital là gì?")


if __name__ == "__main__":
    unittest.main()
