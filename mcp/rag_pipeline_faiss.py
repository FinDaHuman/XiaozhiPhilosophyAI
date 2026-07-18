import argparse
import os
import pickle
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer


if sys.platform == "win32":
    sys.stderr.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")


ROOT = Path(__file__).parent
REPO_ROOT = ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.rag.llm_provider import DEFAULT_GROQ_MODEL, LLMProvider
from app.rag.source_priority import classify_query_domain, source_domain
from app.rag.voice import finalize_voice_answer


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
        print("Chưa có tài liệu nào trong thư mục data/. Hãy thêm .txt, .md, .pdf hoặc .docx.")
        return

    chunks: list[Chunk] = []
    for path in documents:
        text = read_document(path)
        chunks.extend(chunk_text(text, source=str(path.relative_to(ROOT.parent))))

    if not chunks:
        print("Không đọc được nội dung từ các tài liệu trong data/.")
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

    print(f"Đã tạo FAISS index: {len(chunks)} chunks từ {len(documents)} tài liệu.")


def load_index():
    if not INDEX_FILE.exists():
        raise FileNotFoundError("Chưa có index. Hãy chạy: python rag_pipeline_faiss.py ingest")
    with INDEX_FILE.open("rb") as file:
        index = pickle.load(file)

    index["chunks"] = [
        chunk if isinstance(chunk, Chunk) else Chunk(**chunk)
        for chunk in index.get("chunks", [])
    ]
    return index


def retrieve(question: str, top_k: int = 4) -> list[tuple[Chunk, float]]:
    index = load_index()
    domain = classify_query_domain(question)
    search_query = f"Đông Anh Capital {question}" if domain == "dac" else question
    query_vector = index["vectorizer"].transform([search_query]).astype(np.float32).toarray()
    candidate_count = index["faiss_index"].ntotal
    scores, indices = index["faiss_index"].search(query_vector, candidate_count)
    matches = [
        (index["chunks"][chunk_index], float(score))
        for chunk_index, score in zip(indices[0], scores[0])
        if chunk_index >= 0
        and score > 0
        and source_domain(index["chunks"][chunk_index].source) == domain
    ]
    return matches[:top_k]


def build_prompt(question: str, contexts: list[tuple[Chunk, float]]) -> str:
    context_text = "\n\n".join(
        f"[Nguồn: {chunk.source} | score={score:.3f}]\n{chunk.text}"
        for chunk, score in contexts
    )
    return f"""
Bạn là Lily, robot trợ giảng am hiểu Triết học Mác-Lênin và Kinh tế chính trị Mác-Lênin (cạnh tranh, độc quyền, độc quyền nhà nước, vai trò lịch sử của chủ nghĩa tư bản), đồng thời am hiểu nền tảng phân tích chứng khoán Đông Anh Capital. Chỉ trả lời dựa trên ngữ cảnh bên dưới.
CÂU TRẢ LỜI CỦA BẠN ĐƯỢC ĐỌC THÀNH TIẾNG, vì vậy:
- Trả lời tối đa 2-3 câu văn nói tự nhiên, đi thẳng vào trọng tâm.
- TUYỆT ĐỐI KHÔNG dùng markdown, gạch đầu dòng, ngoặc vuông, ký hiệu hay bảng biểu.
- Trích nguồn theo văn nói: "theo slide 5", "theo slide kinh tế chính trị 5", "theo giáo trình", "theo tài liệu Đông Anh Capital". Chỉ nói "theo slide" khi ngữ cảnh thật sự ghi nguồn Slide; với mọi câu về Đông Anh Capital hoặc Hiro, phải nói "theo tài liệu Đông Anh Capital". Không bao giờ viết kiểu [Slide 5].
- Trong mọi câu trả lời, tên thương hiệu phải viết chính xác "Đông Anh Capital"; website phải viết "Đông Anh Capital chấm com". Không xuất "DongAnh Capital", "DongAnhCapital", "DonganhCapital" hay "donganhcapital.com".
Nếu ngữ cảnh không đủ thông tin, hãy nói ngắn gọn là không tìm thấy trong tài liệu.
Khi người dùng muốn tư vấn sâu về một mã cổ phiếu hoặc quyết định đầu tư cụ thể, hãy giới thiệu họ đến Hiro — AI cố vấn đầu tư tại tab AI Chat trên Đông Anh Capital chấm com.
KHÔNG cam kết hay hứa hẹn lợi nhuận; luôn nhắc rằng tín hiệu chỉ là thông tin tham khảo, đầu tư luôn có rủi ro.

Ngữ cảnh:
{context_text}

Câu hỏi: {question}
""".strip()


def ask(question: str, top_k: int = 4) -> str:
    load_dotenv(ROOT.parent / ".env")
    model = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)

    contexts = retrieve(question, top_k=top_k)
    if not contexts:
        return "Không tìm thấy ngữ cảnh liên quan trong tài liệu."

    answer = LLMProvider().complete(
        [
            {
                "role": "system",
                "content": (
                    "Bạn là Lily — robot trợ giảng Triết học và Kinh tế chính trị Mác-Lênin, "
                    "kiêm am hiểu Đông Anh Capital — trả lời dựa trên tài liệu được cung cấp. "
                    "Câu trả lời được đọc thành tiếng: tối đa 2-3 câu văn nói, không markdown, "
                    "không gạch đầu dòng, không ngoặc vuông; trích nguồn theo văn nói như 'theo slide 5'. "
                    "Tên thương hiệu luôn viết 'Đông Anh Capital'; website viết 'Đông Anh Capital chấm com'."
                ),
            },
            {"role": "user", "content": build_prompt(question, contexts)},
        ],
        groq_model=model,
        temperature=0.2,
        max_tokens=300,
    )
    return finalize_voice_answer(answer, question)


def chat() -> None:
    print("Mini RAG chat. Gõ 'exit' để thoát.")
    while True:
        question = input("\nBạn: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue
        print("\nRAG:")
        print(textwrap.fill(ask(question), width=100))


def main() -> None:
    parser = argparse.ArgumentParser(description="Mini RAG pipeline dùng data/ và Groq API.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("ingest", help="Đọc tài liệu trong data/ và tạo index.")

    ask_parser = subparsers.add_parser("ask", help="Hỏi một câu dựa trên index.")
    ask_parser.add_argument("question", help="Câu hỏi cần hỏi.")
    ask_parser.add_argument("--top-k", type=int, default=4, help="Số chunk lấy ra làm ngữ cảnh.")

    subparsers.add_parser("chat", help="Hỏi đáp liên tục trong terminal.")

    args = parser.parse_args()
    if args.command == "ingest":
        ingest()
    elif args.command == "ask":
        print(ask(args.question, top_k=args.top_k))
    elif args.command == "chat":
        chat()


if __name__ == "__main__":
    main()
