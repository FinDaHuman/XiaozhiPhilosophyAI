"""Quota-conscious live Gemini integration harness."""

import argparse
import os
import re
import sys
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Keep the variable present but empty so python-dotenv does not restore Groq.
os.environ["GROQ_API_KEY"] = ""

from app.api.routes import router


CASES = [
    ("Lily ơi, giới thiệu về Đông Anh Capital đi.", r"nền tảng.*chứng khoán|phân tích chứng khoán"),
    ("Đông Anh Capital có phải là quỹ đầu tư không?", r"không phải.*quỹ"),
    ("Website Đông Anh Capital có những tab chính nào?", r"Dashboard|AI Analyst|AI Chat"),
    ("Tab Dashboard của Đông Anh Capital cho xem gì?", r"226|bản đồ nhiệt"),
    ("Tin tức trên Đông Anh Capital có gì đặc biệt?", r"CafeF|cảm xúc"),
    (
        "Tín hiệu AI của Đông Anh Capital hoạt động thế nào?",
        r"ba mô hình|Breakout.*LTR.*BCD|15 giờ 02",
    ),
    ("Mô hình Breakout của Đông Anh Capital làm gì?", r"đột phá|Breakout"),
    ("Mô hình LTR của Đông Anh Capital là gì?", r"Learning to Rank|học xếp hạng"),
    ("Mô hình BCD của Đông Anh Capital là gì?", r"BCD|bắt đáy"),
    ("Dùng Đông Anh Capital có mất phí không?", r"miễn phí|Free"),
    ("Đông Anh Capital có cam kết lợi nhuận không?", r"không.*cam kết|không phải lời khuyên"),
    ("Muốn được tư vấn sâu về một mã cổ phiếu thì hỏi ai?", r"Hiro"),
]
SMOKE_CASE_INDEXES = (0, 5, 11)


def sentence_count(text: str) -> int:
    return len([part for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()])


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run all 12 robot questions instead of the quota-safe smoke subset.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=7.0,
        help="Minimum seconds between Gemini requests (default: 7).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    app = FastAPI()
    app.include_router(router)
    failures = []
    cases = list(enumerate(CASES, 1))
    if not args.full:
        cases = [(index + 1, CASES[index]) for index in SMOKE_CASE_INDEXES]

    with TestClient(app) as client:
        last_request_at: float | None = None

        def quota_safe_post(path, *, json):
            nonlocal last_request_at
            if last_request_at is not None:
                remaining = args.delay - (time.monotonic() - last_request_at)
                if remaining > 0:
                    time.sleep(remaining)
            response = client.post(path, json=json)
            last_request_at = time.monotonic()
            return response

        for index, (question, expected) in cases:
            response = quota_safe_post("/chat/robot", json={"message": question})
            if response.status_code != 200:
                failures.append(f"Q{index}: HTTP {response.status_code} {response.text}")
                continue

            answer = response.json()["answer"]
            content_ok = re.search(expected, answer, flags=re.IGNORECASE) is not None
            format_ok = re.search(r"[\[\]`*]", answer) is None
            length_ok = sentence_count(answer) <= 3
            pronunciation_ok = (
                re.search(r"\bdong\s*anh\s*capital\b", answer, flags=re.IGNORECASE) is None
                and "donganhcapital.com" not in answer.lower()
            )
            ok = content_ok and format_ok and length_ok and pronunciation_ok
            print(
                f"Q{index}: {'PASS' if ok else 'FAIL'} "
                f"sentences={sentence_count(answer)} content={content_ok} "
                f"format={format_ok} pronunciation={pronunciation_ok}"
            )
            print(answer)
            if not ok:
                failures.append(f"Q{index}: output contract failed")

        chat_response = quota_safe_post(
            "/chat",
            json={"message": "DongAnh Capital là gì?", "history": []},
        )
        if chat_response.status_code != 200 or not chat_response.json().get("answer"):
            failures.append(f"/chat failed: {chat_response.status_code} {chat_response.text}")
        else:
            print("/chat: PASS")

        stream_response = quota_safe_post(
            "/chat/stream",
            json={"message": "DongAnh Capital là gì?", "history": []},
        )
        stream_body = stream_response.text
        if (
            stream_response.status_code != 200
            or '"token"' not in stream_body
            or '"done": true' not in stream_body
        ):
            failures.append(
                f"/chat/stream failed: {stream_response.status_code} {stream_body[:500]}"
            )
        else:
            print("/chat/stream: PASS")

    if failures:
        print("\nFAILURES:")
        for failure in failures:
            print("-", failure)
        return 1

    print(
        f"\nSUMMARY: {len(cases)} robot questions + /chat + /chat/stream passed "
        f"({'full' if args.full else 'quota-safe smoke'} mode)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
