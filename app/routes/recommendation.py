from agent.langGraphRunner import run_recommendation_pipeline
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