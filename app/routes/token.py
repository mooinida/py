# app/routes/token.py
# ✅ 수정: 'app' 패키지 기준으로 절대 임포트
from app.my_token.token_storage import save_access_token, get_valid_access_token
from fastapi.responses import RedirectResponse
from fastapi import APIRouter
import jwt
# ✅ .env 파일 로드를 위해 추가 (필요하다면)
import os
from dotenv import load_dotenv

# ✅ .env 파일 로드 (이 스크립트는 /home/ubuntu/py/app/routes 에 있고, .env는 /home/ubuntu/py/app 에 있으므로
# 두 단계 위로 가서 .env를 찾아 로드하도록 경로를 지정합니다.)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

# JWT_SECRET_KEY와 JWT_ALGORITHM은 .env 파일에서 가져오거나 직접 설정 (보안상 .env 권장)
# JWT_SECRET_KEY는 앱의 보안에 매우 중요하므로 절대 공개하지 마십시오.
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "123456789123456789123456789123456789") # ✅ .env에서 가져오도록 수정
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256") # ✅ .env에서 가져오도록 수정

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
