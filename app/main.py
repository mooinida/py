# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ✅ .env 파일 로드 (main.py는 /home/ubuntu/py/app 에 있고, .env는 같은 위치에 있으므로)
import os
from dotenv import load_dotenv
load_dotenv()

# ✅ 수정: 'app' 패키지 기준으로 절대 임포트
from app.routes.token import router as token_router
from app.routes.recommendation import router as recommendation_router
from app.routes.get_menus import router as menu_router
from app.routes.get_reviews import router as review_router

origins = [
    "http://localhost:5173",         # 로컬 테스트
    "http://mooin.shop",             # 프론트 도메인
    "http://mooin.shop:5173",        # 혹시 프론트가 5173에서 테스트 중이라면 이것도 추가
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(token_router)
app.include_router(recommendation_router)
app.include_router(menu_router)
app.include_router(review_router)

@app.get("/")
async def root():
    return {"message": "서버 정상 작동 중!"}
