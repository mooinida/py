# app/routes/get_menus.py
# ✅ 수정: 'app' 패키지 기준으로 절대 임포트
from app.bring_to_server import get_menu_texts
from fastapi import APIRouter
router = APIRouter()

@router.get("/restaurant/{place_id}/menus")
async def get_menu(user_id: str, place_id:int):
    menus =await get_menu_texts(user_id, place_id)
    return {"menus":menus}
