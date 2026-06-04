import os
from typing import List
from langchain_community.embeddings import HuggingFaceEmbeddings

class E5Embeddings(HuggingFaceEmbeddings):
    """Wrapper for E5 models to prepend passage/query prefixes."""
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return super().embed_documents([f"passage: {t}" for t in texts])

    def embed_query(self, text: str) -> List[float]:
        return super().embed_query(f"query: {text}")

def get_embedding_model():
    model_name = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")
    is_e5 = "e5" in model_name.lower()
    
    try:
        if is_e5:
            return E5Embeddings(model_name=model_name)
        else:
            return HuggingFaceEmbeddings(model_name=model_name)
    except Exception as e:
        print(f"⚠️ Failed to load primary model {model_name}. Fallback to all-MiniLM-L6-v2. Error: {e}")
        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
