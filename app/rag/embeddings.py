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

    embedding_class = E5Embeddings if is_e5 else HuggingFaceEmbeddings

    # Prefer the local cache so a transient Hugging Face outage cannot switch
    # the query side of an existing Chroma index to a different vector space.
    try:
        return embedding_class(
            model_name=model_name,
            model_kwargs={"local_files_only": True},
        )
    except Exception:
        try:
            return embedding_class(model_name=model_name)
        except Exception as exc:
            raise RuntimeError(
                f"Unable to load embedding model {model_name!r}. Refusing to "
                "fall back to a different model because that would make "
                "queries incompatible with the existing Chroma index."
            ) from exc
