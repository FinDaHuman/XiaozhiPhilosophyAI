import unittest
from unittest.mock import MagicMock, PropertyMock, patch

from langchain_core.documents import Document

from app.rag.retriever import PhilosophyRetriever
from app.rag.source_priority import classify_query_domain, source_domain


class RetrieverFallbackTests(unittest.TestCase):
    def test_domain_markers_accept_accented_and_unaccented_vietnamese(self):
        self.assertEqual(classify_query_domain("Độc quyền nhà nước"), "ktct")
        self.assertEqual(classify_query_domain("Doc quyen nha nuoc"), "ktct")
        self.assertEqual(classify_query_domain("Mâu thuẫn biện chứng"), "mln111")
        self.assertEqual(classify_query_domain("Mau thuan bien chung"), "mln111")
        self.assertEqual(classify_query_domain("Đông Anh Capital"), "dac")
        self.assertEqual(classify_query_domain("Dong Anh Capital"), "dac")

    def test_real_chroma_and_faiss_source_paths_are_classified(self):
        self.assertEqual(source_domain("DongAnhCapital_KnowledgeBase.md"), "dac")
        self.assertEqual(source_domain("data/DongAnhCapital_KnowledgeBase.md"), "dac")
        self.assertEqual(source_domain("Slide KTCT 3"), "ktct")
        self.assertEqual(source_domain("data/Slide_KTCT_OCR.md"), "ktct")
        self.assertEqual(source_domain("Slide 5"), "mln111")
        self.assertEqual(source_domain("data/Slide_OCR.md"), "mln111")

    def test_multiquery_failure_uses_base_retriever(self):
        retriever = PhilosophyRetriever.__new__(PhilosophyRetriever)
        multiquery = MagicMock()
        multiquery.invoke.side_effect = RuntimeError("provider unavailable")
        base = MagicMock()
        expected = Document(
            page_content="Độc quyền fallback context",
            metadata={"source": "Slide KTCT 3"},
        )
        base.invoke.return_value = [expected]
        retriever._base_retriever = base

        with patch.object(
            PhilosophyRetriever,
            "retriever_pipeline",
            new_callable=PropertyMock,
            return_value=multiquery,
        ):
            result = retriever.retrieve("Độc quyền là gì?")

        self.assertEqual(result, [expected])
        base.invoke.assert_called_once_with("Độc quyền là gì?")

    def test_dac_query_filters_unrelated_slides_and_honors_top_k(self):
        retriever = PhilosophyRetriever.__new__(PhilosophyRetriever)
        vectorstore = MagicMock()
        dac_one = Document(
            page_content="Giới thiệu nền tảng",
            metadata={"source": "DongAnhCapital_KnowledgeBase.md"},
        )
        dac_two = Document(
            page_content="Hiro là cố vấn AI",
            metadata={"source": "DongAnhCapital_KnowledgeBase.md"},
        )
        vectorstore.similarity_search.return_value = [dac_one]
        retriever._vectorstore = vectorstore

        result = retriever.retrieve("Giới thiệu về Đông Anh Capital", top_k=1)

        self.assertEqual(result, [dac_one])
        vectorstore.similarity_search.assert_called_once_with(
            "Đông Anh Capital Giới thiệu về Đông Anh Capital",
            k=1,
            filter={"source": "DongAnhCapital_KnowledgeBase.md"},
        )

    def test_course_query_keeps_slide_priority(self):
        retriever = PhilosophyRetriever.__new__(PhilosophyRetriever)
        pipeline = MagicMock()
        textbook = Document(
            page_content="Giáo trình nói về mâu thuẫn biện chứng.",
            metadata={"source": "GiaoTrinh.docx"},
        )
        slide = Document(
            page_content="Slide giải thích mặt đối lập.",
            metadata={"source": "Slide 5"},
        )
        pipeline.invoke.return_value = [textbook, slide]
        retriever._base_retriever = pipeline

        with patch.object(
            PhilosophyRetriever,
            "retriever_pipeline",
            new_callable=PropertyMock,
            return_value=pipeline,
        ):
            result = retriever.retrieve("Mâu thuẫn biện chứng là gì?", top_k=2)

        self.assertEqual(result[0], slide)

    def test_ktct_query_excludes_legacy_mln111_material(self):
        retriever = PhilosophyRetriever.__new__(PhilosophyRetriever)
        pipeline = MagicMock()
        ktct_slide = Document(
            page_content="Đặc điểm kinh tế của độc quyền.",
            metadata={"source": "Slide KTCT 3"},
        )
        old_mln_slide = Document(
            page_content="Khái niệm triết học cũ.",
            metadata={"source": "Slide 3"},
        )
        dac = Document(
            page_content="Nền tảng chứng khoán.",
            metadata={"source": "DongAnhCapital_KnowledgeBase.md"},
        )
        pipeline.invoke.return_value = [old_mln_slide, dac, ktct_slide]
        retriever._base_retriever = pipeline

        with patch.object(
            PhilosophyRetriever,
            "retriever_pipeline",
            new_callable=PropertyMock,
            return_value=pipeline,
        ):
            result = retriever.retrieve("Độc quyền nhà nước là gì?", top_k=3)

        self.assertEqual(result, [ktct_slide])

    def test_course_query_never_falls_back_to_dac_context(self):
        retriever = PhilosophyRetriever.__new__(PhilosophyRetriever)
        pipeline = MagicMock()
        dac = Document(
            page_content="Nền tảng chứng khoán.",
            metadata={"source": "DongAnhCapital_KnowledgeBase.md"},
        )
        pipeline.invoke.return_value = [dac]
        retriever._base_retriever = pipeline

        with patch.object(
            PhilosophyRetriever,
            "retriever_pipeline",
            new_callable=PropertyMock,
            return_value=pipeline,
        ):
            result = retriever.retrieve("Độc quyền nhà nước là gì?")

        self.assertEqual(result, [])

    def test_ambiguous_presentation_query_retrieves_only_dac(self):
        retriever = PhilosophyRetriever.__new__(PhilosophyRetriever)
        vectorstore = MagicMock()
        dac = Document(
            page_content="Nội dung dự án trọng điểm.",
            metadata={"source": "DongAnhCapital_KnowledgeBase.md"},
        )
        vectorstore.similarity_search.return_value = [dac]
        retriever._vectorstore = vectorstore

        result = retriever.retrieve("Giới thiệu phần trọng điểm", top_k=3)

        self.assertEqual(result, [dac])
        self.assertEqual(
            vectorstore.similarity_search.call_args.kwargs["filter"],
            {"source": "DongAnhCapital_KnowledgeBase.md"},
        )


if __name__ == "__main__":
    unittest.main()
