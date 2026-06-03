import httpx
import time
import subprocess
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def test_api():
    print("🚀 Bắt đầu test API Server với test_questions.txt...")
    proc = subprocess.Popen([sys.executable, "-m", "app.main", "api"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    
    try:
        print("Đợi 25s để server khởi động (do thời gian load model/fallback)...")
        time.sleep(25)
        
        # Đọc 3 câu hỏi đầu tiên
        with open("../test_questions.txt", "r", encoding="utf-8") as f:
            questions = [line.strip() for line in f.readlines() if line.strip()]
            
        test_q = questions[:3] 
        
        for q in test_q:
            print(f"\n❓ Câu hỏi: '{q}'")
            response = httpx.post(
                "http://127.0.0.1:8000/chat", 
                json={"message": q}, 
                timeout=45.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print("💡 Trả lời:")
                print(data.get("answer", ""))
            else:
                print(f"❌ Lỗi API: {response.text}")
            print("-" * 60)
            
        print("\n✅ Test hoàn tất!")
            
    except Exception as e:
        print(f"❌ Lỗi khi test API: {e}")
    finally:
        print("Đóng server...")
        proc.terminate()
        try:
            proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

if __name__ == "__main__":
    test_api()
