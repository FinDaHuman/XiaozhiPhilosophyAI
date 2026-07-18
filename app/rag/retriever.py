"""
Philosophy Retriever

Wraps ChromaDB similarity search, BM25 keyword search, and MultiQueryRetriever 
to retrieve relevant document chunks for a given question.
"""

import logging
import os
from typing import Optional

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_classic.retrievers import EnsembleRetriever, MultiQueryRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_groq import ChatGroq

from app.rag.embeddings import get_embedding_model
from app.rag.source_priority import DAC_SOURCE, classify_query_domain, source_domain
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "philosophy_docs")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
TOP_K = int(os.getenv("TOP_K", "5"))
GROQ_QUERY_MODEL = os.getenv("GROQ_QUERY_MODEL", "llama-3.1-8b-instant")


class PhilosophyRetriever:
    """
    Advanced Retriever that combines Vector Search, BM25 Keyword Search,
    and MultiQuery expansion for maximum retrieval accuracy.
    """

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: Optional[str] = None,
        top_k: Optional[int] = None,
    ):
        self.persist_directory = persist_directory or CHROMA_PERSIST_DIR
        self.collection_name = collection_name or CHROMA_COLLECTION
        self.top_k = top_k or TOP_K
        self._vectorstore: Optional[Chroma] = None
        self._embeddings = None
        
        # Advanced Retrievers
        self._bm25_retriever: Optional[BM25Retriever] = None
        self._ensemble_retriever: Optional[EnsembleRetriever] = None
        self._multi_query_retriever: Optional[MultiQueryRetriever] = None
        self._base_retriever = None

    @property
    def embeddings(self):
        """Lazy-initialize the embedding model."""
        if self._embeddings is None:
            self._embeddings = get_embedding_model()
        return self._embeddings

    @property
    def vectorstore(self) -> Chroma:
        """Lazy-initialize the vector store."""
        if self._vectorstore is None:
            self._vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
            )
        return self._vectorstore
        
    @property
    def retriever_pipeline(self):
        """Lazy-initialize the full retrieval pipeline."""
        if self._multi_query_retriever is not None:
            return self._multi_query_retriever

        # 1. Base Vector Retriever
        vector_retriever = self.vectorstore.as_retriever(search_kwargs={"k": self.top_k})
        
        # 2. Build BM25 Retriever from Chroma documents
        try:
            # We load all documents from Chroma to build the BM25 index in memory
            # This is fast for <10,000 documents
            all_docs_dict = self.vectorstore.get()
            docs = []
            for i in range(len(all_docs_dict["ids"])):
                docs.append(Document(
                    page_content=all_docs_dict["documents"][i],
                    metadata=all_docs_dict["metadatas"][i]
                ))
            if docs:
                self._bm25_retriever = BM25Retriever.from_documents(docs)
                self._bm25_retriever.k = self.top_k
            else:
                self._bm25_retriever = None
        except Exception as e:
            print(f"Warning: Failed to build BM25 index: {e}")
            self._bm25_retriever = None

        # 3. Ensemble (Hybrid Search)
        if self._bm25_retriever:
            self._ensemble_retriever = EnsembleRetriever(
                retrievers=[vector_retriever, self._bm25_retriever],
                weights=[0.6, 0.4] # Give slightly more weight to semantic search
            )
            base_retriever = self._ensemble_retriever
        else:
            base_retriever = vector_retriever

        # 4. MultiQuery Expansion
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            llm = ChatGroq(
                temperature=0,
                model_name=GROQ_QUERY_MODEL,
                api_key=api_key,
                max_retries=0,
                request_timeout=12,
            )
            self._multi_query_retriever = MultiQueryRetriever.from_llm(
                retriever=base_retriever,
                llm=llm
            )
        else:
            self._multi_query_retriever = base_retriever

        self._base_retriever = base_retriever
        return self._multi_query_retriever

    def retrieve(self, query: str, top_k: Optional[int] = None) -> list[Document]:
        """
        Retrieve relevant chunks from exactly one presentation domain.

        Đông Anh Capital is the default and is filtered at the vector-store
        level. Course slides/textbooks are considered only for explicit
        MLN111 or KTCT questions.
        """
        limit = top_k or getattr(self, "top_k", TOP_K)
        domain = classify_query_domain(query)
        if domain == "dac":
            return self.vectorstore.similarity_search(
                f"Đông Anh Capital {query}",
                k=limit,
                filter={"source": DAC_SOURCE},
            )

        pipeline = self.retriever_pipeline
        try:
            raw_docs = pipeline.invoke(query)
        except Exception as exc:
            if self._base_retriever is None or pipeline is self._base_retriever:
                raise
            logger.warning(
                "MultiQuery retrieval failed with %s; using vector+BM25 base retrieval",
                type(exc).__name__,
            )
            raw_docs = self._base_retriever.invoke(query)
        return self._rerank_source_priority(raw_docs, query=query)[:limit]

    def _rerank_source_priority(self, docs: list[Document], query: str) -> list[Document]:
        """
        Keep only the explicitly selected course domain. Within that domain,
        slides precede textbook chunks and substantially duplicated textbook
        text is dropped.
        """
        unique_docs = []
        seen = set()
        for doc in docs:
            key = (doc.metadata.get("source", ""), doc.page_content)
            if key not in seen:
                seen.add(key)
                unique_docs.append(doc)

        groups = {
            "dac": [],
            "ktct_slide": [],
            "mln_slide": [],
            "ktct_textbook": [],
            "mln_textbook": [],
            "other": [],
        }
        for doc in unique_docs:
            source = doc.metadata.get("source", "")
            domain = source_domain(source)
            if domain == "dac":
                groups["dac"].append(doc)
            elif domain == "ktct" and source.casefold().startswith("slide ktct"):
                groups["ktct_slide"].append(doc)
            elif domain == "mln111" and source.casefold().startswith("slide"):
                groups["mln_slide"].append(doc)
            elif domain == "ktct":
                groups["ktct_textbook"].append(doc)
            elif domain == "mln111":
                groups["mln_textbook"].append(doc)
            else:
                groups["other"].append(doc)

        domain = classify_query_domain(query)
        if domain == "ktct":
            return self._slides_then_unique_textbook(
                groups["ktct_slide"], groups["ktct_textbook"]
            )

        if domain == "mln111":
            return self._slides_then_unique_textbook(
                groups["mln_slide"], groups["mln_textbook"]
            )

        return groups["dac"]

    @staticmethod
    def _slides_then_unique_textbook(
        slides: list[Document], textbook: list[Document]
    ) -> list[Document]:
        """Put slides first and drop textbook chunks mostly duplicated by them."""
        slide_tokens = set()
        for slide_doc in slides:
            slide_tokens.update(slide_doc.page_content.lower().split())

        filtered_textbook = []
        for textbook_doc in textbook:
            words = textbook_doc.page_content.lower().split()
            if not words:
                continue
            overlap_ratio = sum(1 for word in words if word in slide_tokens) / len(words)
            if overlap_ratio < 0.5:
                filtered_textbook.append(textbook_doc)

        return slides + filtered_textbook

    def get_collection_stats(self) -> dict:
        """Get stats about the current vector store collection."""
        try:
            collection = self.vectorstore._collection
            count = collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": self.persist_directory,
                "embedding_model": EMBEDDING_MODEL,
                "hybrid_search": self._bm25_retriever is not None,
                "multi_query": isinstance(self._multi_query_retriever, MultiQueryRetriever)
            }
        except Exception as e:
            return {"error": str(e)}

    def reload(self):
        """Force reload the vector store and rebuild BM25 (after re-ingestion)."""
        self._vectorstore = None
        self._bm25_retriever = None
        self._ensemble_retriever = None
        self._multi_query_retriever = None
        self._base_retriever = None
        _ = self.retriever_pipeline  # re-initialize
