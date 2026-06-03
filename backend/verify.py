import sys
from dotenv import load_dotenv
load_dotenv()
from app.rag.pipeline import RAGPipeline

# Fix Windows console encoding for emoji/Unicode output
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def run_tests():
    rag = RAGPipeline()
    questions = [
        "Nguyên nhân là gì?",
        "Chủ nghĩa siêu hình cận đại là gì?",
        "Ai vô địch World Cup 2030?"
    ]

    for q in questions:
        print(f"\n=============================================")
        print(f"Q: {q}")
        print(f"=============================================")
        ans = rag.ask(q)
        print(ans)

if __name__ == "__main__":
    run_tests()
