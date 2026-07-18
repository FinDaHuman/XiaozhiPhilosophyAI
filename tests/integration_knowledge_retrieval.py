"""Offline verification for DongAnh Capital knowledge retrieval."""

import os
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# MultiQuery would consume Groq quota. The base vector+BM25 retriever is the
# behavior we want to validate here, so keep this integration test fully local.
os.environ["GROQ_API_KEY"] = ""

from app.rag.retriever import PhilosophyRetriever


CASES = [
    (
        "Lily ơi, giới thiệu về donganhcapital.com đi.",
        r"nền tảng phân tích chứng khoán|trí tuệ nhân tạo",
    ),
    ("DongAnh Capital có phải là quỹ đầu tư không?", r"không phải là quỹ đầu tư"),
    ("Website donganhcapital.com có những tab chính nào?", r"Dashboard.*AI Analyst|AI Chat"),
    ("Tab Dashboard của DongAnh Capital cho xem gì?", r"226 mã|bản đồ nhiệt"),
    ("Tin tức trên DongAnh Capital có gì đặc biệt?", r"CafeF|gắn nhãn cảm xúc"),
    ("Tín hiệu AI của DongAnh Capital hoạt động thế nào?", r"ba mô hình|15 giờ 02"),
    ("Mô hình Breakout của DongAnh Capital làm gì?", r"Breakout|đột phá giá"),
    ("Mô hình LTR của DongAnh Capital là gì?", r"Learning to Rank|học xếp hạng"),
    ("Mô hình BCD của DongAnh Capital là gì?", r"BCD|bắt đáy"),
    ("Dùng DongAnh Capital có mất phí không?", r"Free|miễn phí"),
    (
        "DongAnh Capital có cam kết lợi nhuận không?",
        r"không.*cam kết|không phải lời khuyên",
    ),
    ("Muốn được tư vấn sâu về một mã cổ phiếu thì hỏi ai?", r"Hiro"),
]


def main() -> int:
    retriever = PhilosophyRetriever()
    failures = []

    for index, (question, expected) in enumerate(CASES, 1):
        docs = retriever.retrieve(question)
        context = "\n".join(doc.page_content for doc in docs)
        passed = bool(docs) and re.search(
            expected,
            context,
            flags=re.IGNORECASE | re.DOTALL,
        )
        print(f"KB_Q{index}={'PASS' if passed else 'FAIL'} docs={len(docs)}")
        if not passed:
            failures.append(index)

    if failures:
        print(f"KNOWLEDGE_RETRIEVAL=FAIL questions={failures}")
        return 1

    print(f"KNOWLEDGE_RETRIEVAL={len(CASES)}/{len(CASES)}_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
