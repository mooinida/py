from my_token.token_storage import save_access_token, get_valid_access_token
from fastapi.responses import RedirectResponse
from fastapi import APIRouter
import jwt
JWT_SECRET_KEY = "123456789123456789123456789123456789"
JWT_ALGORITHM = "HS256"
router = APIRouter()

@router.get("/save-token")
async def save_token_from_redirect(token: str):
    """
    token만 받아 JWT 디코딩 → userId 추출 → Redis에 저장
    """
    try:
        # JWT 디코딩
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = str(payload.get("id"))  # JWT에 들어있는 사용자 ID

        # Redis에 저장
        save_access_token(user_id, token)

        return RedirectResponse(url=f"http://localhost:5173/recommend?user_id={user_id}")

    except jwt.ExpiredSignatureError:
        return {"error": "만료된 토큰입니다"}
    except jwt.InvalidTokenError as e:
        return {"error": f"유효하지 않은 토큰입니다: {str(e)}"}
