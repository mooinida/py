from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.token import router as token_router
from .routes.recommendation import router as recommendation_router
from .routes.get_menus import router as menu_router
from .routes.get_reviews import router as review_router
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
