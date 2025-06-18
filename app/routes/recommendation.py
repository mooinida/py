# app/routes/recommendation.py
# ✅ 수정: 'app' 패키지 기준으로 절대 임포트
from app.agent.langGraphRunner import run_recommendation_pipeline
from fastapi import APIRouter
router = APIRouter()

@router.get("/start-recommendation")
async def start_recommendation(user_id: str, user_input:str):
    print("호출완료 "+user_input)
    
    state = {
        "user_id": user_id,
        "user_input":user_input
    }
    result = await run_recommendation_pipeline(state)
    return result
