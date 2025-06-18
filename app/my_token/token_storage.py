# app/my_token/token_storage.py
import redis
import requests
import os # .env 파일 로드를 위해 추가
from dotenv import load_dotenv # .env 파일 로드를 위해 추가

# ✅ .env 파일 로드 (이 스크립트는 /home/ubuntu/py/app/my_token 에 있고, .env는 /home/ubuntu/py/app 에 있으므로
# 두 단계 위로 가서 .env를 찾아 로드하도록 경로를 지정합니다.)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

# Redis 연결 정보 (환경 변수로 관리하는 것이 좋음)
REDIS_HOST = os.getenv("REDIS_HOST", "14.63.178.162") # ✅ 환경 변수에서 가져오도록 수정
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379)) # ✅ 환경 변수에서 가져오도록 수정

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)

def save_access_token(user_id: str, access_token: str, expires_in=3600):
    """access token을 Redis에 저장"""
    r.setex(f"access_token:{user_id}", expires_in, access_token)

def get_access_token(user_id: str):
    """Redis에서 access token 조회"""
    return r.get(f"access_token:{user_id}")

def delete_access_token(user_id: str):
    """access token 삭제"""
    r.delete(f"access_token:{user_id}")

def renew_access_token(user_id: str, spring_url: str):
    """
    Spring에게 user_id만 보내서 새로운 access token을 요청
    (refresh token은 Spring이 내부 DB에서 사용)
    """
    response = requests.post(
        f"{spring_url}/api/token",
        json={"userId": user_id}
    )

    if response.status_code == 201:
        new_access_token = response.json().get("accessToken")
        save_access_token(user_id, new_access_token)
        return {"accessToken": new_access_token}
    else:
        return {"error": f"Failed to renew token: {response.text}"}

def get_valid_access_token(user_id: str, refresh_url: str):
    """
    Redis에서 access token을 꺼내고, 없으면 자동으로 갱신
    """
    token = get_access_token(user_id)
    if token:
        return token
    # 없거나 만료되었으면 새로 받기
    refresh_response = requests.post(
    refresh_url,
    json={"user_id": int(user_id)}
)
    if refresh_response.ok:
        new_token = refresh_response.json().get("accessToken")
        r.setex(f"access_token:{user_id}", 3600, new_token)
        return new_token
    return None
