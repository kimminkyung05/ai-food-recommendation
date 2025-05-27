import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AI 모델 임포트
try:
    from ai_model import advanced_ai
    logger.info("AI 모델 로드 성공")
except ImportError as e:
    logger.error(f"AI 모델 로드 실패: {e}")
    advanced_ai = None

# FastAPI 앱 생성
app = FastAPI(
    title="고도화된 AI 음식 추천 시스템",
    description="하이브리드 AI 기반 용기 크기 맞춤형 음식 추천 API",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 구체적인 도메인 지정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 요청/응답 모델 정의
class AdvancedRecommendationRequest(BaseModel):
    width: float = Field(..., gt=0, description="용기 가로 크기 (cm)")
    length: float = Field(..., gt=0, description="용기 세로 크기 (cm)")
    height: float = Field(..., gt=0, description="용기 높이 (cm)")
    category: Optional[str] = Field(None, description="음식 카테고리 (한식, 중식, 일식, 양식, 기타)")
    top_k: Optional[int] = Field(5, ge=1, le=5, description="추천 개수 (최대 5개)")

class MenuScore(BaseModel):
    fit_score: float
    preference_score: float
    content_score: float
    final_score: float

class MenuSize(BaseModel):
    width: float
    length: float
    height: float

class AdvancedMenuInfo(BaseModel):
    menu_id: str
    restaurant_id: str
    restaurant_name: str
    menu_name: str
    category: str
    price: int
    size: MenuSize
    scores: MenuScore
    volume_utilization: float
    explanation: str
    contextual_boost: float

class AdvancedRecommendationResponse(BaseModel):
    status: str
    message: str
    data: List[AdvancedMenuInfo]
    metadata: Dict[str, Any]

# 기본 루트
@app.get("/")
def root():
    """API 상태 및 기본 정보"""
    try:
        if advanced_ai is None:
            return {
                "message": "고도화된 AI 음식 추천 시스템",
                "version": "2.0.0",
                "status": "running",
                "algorithm": "hybrid_filtering_v2.0",
                "error": "AI 모델이 로드되지 않았습니다",
                "statistics": {
                    "total_menus": 0,
                    "total_restaurants": 0,
                    "categories": [],
                    "max_recommendations": 5
                }
            }
        
        return {
            "message": "고도화된 AI 음식 추천 시스템",
            "version": "2.0.0",
            "status": "running",
            "algorithm": "hybrid_filtering_v2.0",
            "features": [
                "콘텐츠 기반 필터링",
                "상황 인식 추천",
                "다양성 보장",
                "설명 가능한 AI",
                "지속적 학습"
            ],
            "statistics": {
                "total_menus": len(advanced_ai.menus_df),
                "total_restaurants": len(advanced_ai.restaurants_df),
                "categories": list(advanced_ai.menus_df['category'].unique()),
                "max_recommendations": getattr(advanced_ai, 'max_recommendations', 5)
            }
        }
    except Exception as e:
        return {
            "message": "고도화된 AI 음식 추천 시스템",
            "version": "2.0.0", 
            "status": "error",
            "error": str(e),
            "statistics": {
                "total_menus": 0,
                "total_restaurants": 0,
                "categories": [],
                "max_recommendations": 5
            }
        }

# 헬스체크 엔드포인트
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "ai_model_loaded": advanced_ai is not None
    }

# 추천 API 엔드포인트
@app.post("/recommend/advanced")
def get_advanced_recommendations(request: AdvancedRecommendationRequest):
    """
    고도화된 하이브리드 AI 추천 시스템
    """
    if advanced_ai is None:
        raise HTTPException(status_code=500, detail="AI 모델이 로드되지 않았습니다")
    
    try:
        logger.info(f"고도화된 추천 요청: {request.width}x{request.length}x{request.height}")
        logger.info(f"카테고리: {request.category or '전체'}")
        
        # 하이브리드 추천 시스템 호출
        result = advanced_ai.get_hybrid_recommendations(
            user_width=request.width,
            user_length=request.length,
            user_height=request.height,
            preferred_category=request.category,
            top_k=request.top_k
        )
        
        logger.info(f"추천 결과: {result['status']}")
        return result
        
    except Exception as e:
        logger.error(f"고도화된 추천 오류: {e}")
        raise HTTPException(status_code=500, detail=f"AI 추천 중 오류 발생: {str(e)}")

# 간단한 추천 API (기존 코드와의 호환성)
@app.post("/recommend/simple")
def get_simple_recommendations(request: AdvancedRecommendationRequest):
    """
    간단한 추천 시스템 (기존 호환성)
    """
    if advanced_ai is None:
        raise HTTPException(status_code=500, detail="AI 모델이 로드되지 않았습니다")
    
    try:
        logger.info(f"간단한 추천 요청: {request.width}x{request.length}x{request.height}")
        
        # 기존 simple 추천 사용
        result = advanced_ai.get_simple_recommendations(
            width=request.width,
            length=request.length,
            height=request.height,
            top_k=request.top_k
        )
        
        return {
            "status": "success",
            "count": len(result),
            "recommendations": result,
            "query": {
                "width": request.width,
                "length": request.length,
                "height": request.height,
                "top_k": request.top_k
            }
        }
    except Exception as e:
        logger.error(f"간단한 추천 처리 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"추천 처리 중 오류가 발생했습니다: {str(e)}")

# 서버 실행
if __name__ == "__main__":
    import uvicorn
    print("고도화된 AI 추천 시스템 서버 시작...")
    print("서버 주소: http://127.0.0.1:8000")
    print("API 문서: http://127.0.0.1:8000/docs")
    print("주요 엔드포인트:")
    print("   - POST /recommend/advanced : 고도화된 추천")
    print("   - POST /recommend/simple   : 간단한 추천")
    print("   - GET  /health            : 상태 확인")
    print("서버 시작 중...")
    
    uvicorn.run(
        app,  # 직접 app 객체 전달 (문자열 대신)
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )