import os
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv

load_dotenv()

from app.rag.retriever import PhilosophyRetriever
def measure_tokens(text: str) -> int:
    # Rough estimation for tokens without installing tiktoken
    return len(text) // 4

def main():
    retriever = PhilosophyRetriever()
    
    print("=" * 60)
    print(f"Current Config:")
    print(f"CHUNK_SIZE: {os.getenv('CHUNK_SIZE')}")
    print(f"CHUNK_OVERLAP: {os.getenv('CHUNK_OVERLAP')}")
    print(f"TOP_K: {os.getenv('TOP_K')}")
    print("=" * 60)
    
    queries = [
        "Nguyên nhân là gì?",
        "Phân biệt nguyên nhân chủ yếu và nguyên nhân thứ yếu.",
        "Chủ nghĩa siêu hình cận đại là gì?"
    ]
    
    for q in queries:
        print(f"\nQUERY: '{q}'")
        print("-" * 60)
        docs = retriever.retrieve(q)
        
        total_chars = 0
        total_tokens = 0
        
        for i, doc in enumerate(docs, 1):
            content = doc.page_content
            source = doc.metadata.get('source', 'Unknown')
            chars = len(content)
            tokens = measure_tokens(content)
            
            total_chars += chars
            total_tokens += tokens
            
            print(f"Chunk {i} | Source: {source} | Chars: {chars} | Tokens: ~{tokens}")
            print(f"Preview: {content[:150]}...")
            print("-" * 30)
            
        print(f"TOTAL CONTEXT SIZE for this query: {total_chars} characters, ~{total_tokens} tokens.")
        print("=" * 60)

if __name__ == "__main__":
    main()
