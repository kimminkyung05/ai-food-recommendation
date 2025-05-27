from fastapi import FastAPI
import uvicorn

# 간단한 테스트 서버
app = FastAPI(title="테스트 서버")

@app.get("/")
def test_root():
    return {"message": "서버가 정상 작동합니다!", "status": "success"}

@app.get("/test")
def test_endpoint():
    return {"test": "OK", "port": 8000}

if __name__ == "__main__":
    print("🧪 테스트 서버 시작...")
    print("📍 브라우저에서 http://127.0.0.1:8000 접속해보세요")
    print("📍 테스트 페이지: http://127.0.0.1:8000/test")
    print("=" * 50)
    
    try:
        uvicorn.run(
            app,  # 직접 app 객체 전달
            host="127.0.0.1",
            port=8000,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        print("🔧 포트 8001로 재시도...")
        try:
            uvicorn.run(
                app,
                host="127.0.0.1", 
                port=8001,
                log_level="info"
            )
            print("📍 서버 주소: http://127.0.0.1:8001")
        except Exception as e2:
            print(f"❌ 8001 포트도 실패: {e2}")