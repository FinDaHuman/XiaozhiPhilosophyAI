"""
Philosophy Retriever

Wraps ChromaDB similarity search, BM25 keyword search, and MultiQueryRetriever 
to retrieve relevant document chunks for a given question.
"""

import os
from typing import Optional

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_groq import ChatGroq

from app.rag.embeddings import get_embedding_model
from dotenv import load_dotenv

load_dotenv()


CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "philosophy_docs")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
TOP_K = int(os.getenv("TOP_K", "5"))
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


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
                model_name=GROQ_MODEL,
                api_key=api_key
            )
            self._multi_query_retriever = MultiQueryRetriever.from_llm(
                retriever=base_retriever,
                llm=llm
            )
        else:
            self._multi_query_retriever = base_retriever
            
        return self._multi_query_retriever

    def retrieve(self, query: str, top_k: Optional[int] = None) -> list[Document]:
        """
        Retrieve the most relevant document chunks for a query using the advanced pipeline.
        Slides are always re-ranked to the top. Textbook chunks whose content is already
        covered by a retrieved slide chunk are suppressed to prevent duplication.
        """
        raw_docs = self.retriever_pipeline.invoke(query)
        return self._rerank_slide_priority(raw_docs)

    def _rerank_slide_priority(self, docs: list[Document]) -> list[Document]:
        """
        Re-rank retrieved documents so that Slide chunks come first.
        Also deduplicates: if a textbook chunk overlaps >50% with an included
        slide chunk (by shared word tokens), the textbook chunk is dropped.
        """
        slides = []
        textbook = []

        for doc in docs:
            source = doc.metadata.get("source", "")
            # Slides are tagged with source like "Slide 19"
            if source.lower().startswith("slide"):
                slides.append(doc)
            else:
                textbook.append(doc)

        # Build a combined token set from all slide content for overlap check
        slide_tokens = set()
        for slide_doc in slides:
            slide_tokens.update(slide_doc.page_content.lower().split())

        # Keep a textbook chunk only if it adds unique information
        # (less than 50% of its words already appear in slide chunks)
        filtered_textbook = []
        for tb_doc in textbook:
            tb_words = tb_doc.page_content.lower().split()
            if not tb_words:
                continue
            overlap_ratio = sum(1 for w in tb_words if w in slide_tokens) / len(tb_words)
            if overlap_ratio < 0.5:
                filtered_textbook.append(tb_doc)

        # Slides first, then non-overlapping textbook chunks
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
        _ = self.retriever_pipeline  # re-initialize
