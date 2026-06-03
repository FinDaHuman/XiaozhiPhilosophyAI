"""
Philosophy Retriever

Wraps ChromaDB similarity search to retrieve relevant document chunks
for a given question.
"""

import os
from typing import Optional

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()


CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "chroma_db")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "philosophy_docs")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
TOP_K = int(os.getenv("TOP_K", "5"))


class PhilosophyRetriever:
    """
    Retriever that searches the philosophy vector store
    for the most relevant document chunks.
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
        self._embeddings: Optional[GoogleGenerativeAIEmbeddings] = None

    @property
    def embeddings(self) -> GoogleGenerativeAIEmbeddings:
        """Lazy-initialize the embedding model."""
        if self._embeddings is None:
            self._embeddings = GoogleGenerativeAIEmbeddings(
                model=EMBEDDING_MODEL,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
            )
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

    def retrieve(self, query: str, top_k: Optional[int] = None) -> list[Document]:
        """
        Retrieve the top-k most relevant document chunks for a query.
        """
        k = top_k or self.top_k
        results = self.vectorstore.similarity_search(query, k=k)
        return results

    def retrieve_with_scores(
        self, query: str, top_k: Optional[int] = None
    ) -> list[tuple[Document, float]]:
        """
        Retrieve documents with their similarity scores.
        """
        k = top_k or self.top_k
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return results

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
            }
        except Exception as e:
            return {"error": str(e)}

    def reload(self):
        """Force reload the vector store (after re-ingestion)."""
        self._vectorstore = None
        _ = self.vectorstore  # re-initialize
