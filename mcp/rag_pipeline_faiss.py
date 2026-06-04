import argparse
import os
import pickle
import textwrap
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np
from dotenv import load_dotenv
from groq import Groq
from sklearn.feature_extraction.text import TfidfVectorizer


ROOT = Path(__file__).parent
DOCS_DIR = ROOT.parent / "data"
INDEX_DIR = ROOT / ".rag_index"
INDEX_FILE = INDEX_DIR / "index.pkl"
SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}


@dataclass
class Chunk:
    source: str
    text: str


def read_txt_like(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def read_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def read_docx(path: Path) -> str:
    from docx import Document

    document = Document(str(path))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def read_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return read_txt_like(path)
    if suffix == ".pdf":
        return read_pdf(path)
    if suffix == ".docx":
        return read_docx(path)
    raise ValueError(f"Unsupported file type: {path}")


def iter_documents() -> list[Path]:
    DOCS_DIR.mkdir(exist_ok=True)
    return sorted(
        path
        for path in DOCS_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def chunk_text(text: str, source: str, chunk_size: int = 900, overlap: int = 150) -> list[Chunk]:
    cleaned = " ".join(text.split())
    if not cleaned:
        return []

    chunks = []
    start = 0
    while start < len(cleaned):
        end = start + chunk_size
        chunks.append(Chunk(source=source, text=cleaned[start:end]))
        start = max(end - overlap, start + 1)
    return chunks


def ingest() -> None:
    documents = iter_documents()
    if not documents:
        print("Chua co tai lieu nao trong thu muc docs/. Hay them .txt, .md, .pdf hoac .docx.")
        return

    chunks: list[Chunk] = []
    for path in documents:
        text = read_document(path)
        chunks.extend(chunk_text(text, source=str(path.relative_to(ROOT))))

    if not chunks:
        print("Khong doc duoc noi dung tu cac tai lieu trong docs/.")
        return

    vectorizer = TfidfVectorizer(strip_accents="unicode", lowercase=True, norm="l2")
    matrix = vectorizer.fit_transform(chunk.text for chunk in chunks)
    dense_matrix = matrix.astype(np.float32).toarray()

    faiss_index = faiss.IndexFlatIP(dense_matrix.shape[1])
    faiss_index.add(dense_matrix)

    INDEX_DIR.mkdir(exist_ok=True)
    with INDEX_FILE.open("wb") as file:
        pickle.dump(
            {
                "chunks": [chunk.__dict__ for chunk in chunks],
                "vectorizer": vectorizer,
                "faiss_index": faiss_index,
            },
            file,
        )

    print(f"Da tao FAISS index: {len(chunks)} chunks tu {len(documents)} tai lieu.")


def load_index():
    if not INDEX_FILE.exists():
        raise FileNotFoundError("Chua co index. Hay chay: python rag_pipeline.py ingest")
    with INDEX_FILE.open("rb") as file:
        index = pickle.load(file)

    index["chunks"] = [
        chunk if isinstance(chunk, Chunk) else Chunk(**chunk)
        for chunk in index.get("chunks", [])
    ]
    return index


def retrieve(question: str, top_k: int = 4) -> list[tuple[Chunk, float]]:
    index = load_index()
    query_vector = index["vectorizer"].transform([question]).astype(np.float32).toarray()
    scores, indices = index["faiss_index"].search(query_vector, top_k)
    return [
        (index["chunks"][chunk_index], float(score))
        for chunk_index, score in zip(indices[0], scores[0])
        if chunk_index >= 0 and score > 0
    ]


def build_prompt(question: str, contexts: list[tuple[Chunk, float]]) -> str:
    context_text = "\n\n".join(
        f"[Nguon: {chunk.source} | score={score:.3f}]\n{chunk.text}"
        for chunk, score in contexts
    )
    return f"""
Ban la tro ly RAG. Chi tra loi dua tren ngu canh ben duoi.
Neu ngu canh khong du thong tin, hay noi ro la khong tim thay trong tai lieu.
Tra loi bang tieng Viet, ngan gon, co trich nguon file khi phu hop.

Ngu canh:
{context_text}

Cau hoi: {question}
""".strip()


def ask(question: str, top_k: int = 4) -> str:
    load_dotenv(ROOT.parent / ".env")
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    if not api_key:
        raise ValueError("Thieu GROQ_API_KEY trong file .env")

    contexts = retrieve(question, top_k=top_k)
    if not contexts:
        return "Khong tim thay ngu canh lien quan trong tai lieu."

    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Ban la tro ly RAG tra loi dua tren tai lieu duoc cung cap.",
            },
            {"role": "user", "content": build_prompt(question, contexts)},
        ],
        temperature=0.2,
    )
    return completion.choices[0].message.content or ""


def chat() -> None:
    print("Mini RAG chat. Go 'exit' de thoat.")
    while True:
        question = input("\nBan: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue
        print("\nRAG:")
        print(textwrap.fill(ask(question), width=100))


def main() -> None:
    parser = argparse.ArgumentParser(description="Mini RAG pipeline dung docs/ va Groq API.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("ingest", help="Doc tai lieu trong docs/ va tao index.")

    ask_parser = subparsers.add_parser("ask", help="Hoi mot cau dua tren index.")
    ask_parser.add_argument("question", help="Cau hoi can hoi.")
    ask_parser.add_argument("--top-k", type=int, default=4, help="So chunk lay ra lam ngu canh.")

    subparsers.add_parser("chat", help="Hoi dap lien tuc trong terminal.")

    args = parser.parse_args()
    if args.command == "ingest":
        ingest()
    elif args.command == "ask":
        print(ask(args.question, top_k=args.top_k))
    elif args.command == "chat":
        chat()


if __name__ == "__main__":
    main()
