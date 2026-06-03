import httpx
import time
import subprocess
import sys
import threading

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def test_api():
    print("🚀 Bắt đầu test API Server...")
    # Bật API server ở chế độ nền
    proc = subprocess.Popen([sys.executable, "-m", "app.main", "api"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    
    try:
        print("Đợi 25s để server khởi động (do thời gian load model/fallback)...")
        time.sleep(25)
        
        print("Gửi câu hỏi: 'Triết học là gì?'")
        response = httpx.post(
            "http://127.0.0.1:8000/chat", 
            json={"message": "Triết học là gì?"}, 
            timeout=45.0
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Trả lời từ API:")
            print("-" * 50)
            print(data.get("answer", ""))
            print("-" * 50)
            print("✅ Test API Thành công!")
        else:
            print(f"❌ Test API Thất bại: {response.text}")
            
    except Exception as e:
        print(f"❌ Lỗi khi test API: {e}")
    finally:
        print("Đóng server...")
        proc.terminate()
        try:
            stdout, stderr = proc.communicate(timeout=5)
            print("=== Server STDOUT ===")
            print(stdout)
            print("=== Server STDERR ===")
            print(stderr)
        except subprocess.TimeoutExpired:
            proc.kill()

if __name__ == "__main__":
    test_api()
