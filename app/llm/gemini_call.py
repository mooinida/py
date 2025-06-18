# app/llm/gemini_call.py
# ✅ 수정: 'app' 패키지 기준으로 절대 임포트
from app.service.prompt import build_review_prompt, build_final_recommendation_prompt
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

# ✅ .env 파일 로드 (이 스크립트는 /home/ubuntu/py/app/llm 에 있고, .env는 /home/ubuntu/py/app 에 있으므로
# 두 단계 위로 가서 .env를 찾아 로드하도록 경로를 지정합니다.)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

JWT_TOKEN = os.getenv("JWT_TOKEN") # .env에서 로드된 JWT_TOKEN 사용

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") # .env에서 로드된 GOOGLE_API_KEY 사용

# llm 인스턴스는 환경 변수가 로드된 후에 초기화되어야 합니다.
llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-pro", google_api_key=GOOGLE_API_KEY, model_kwargs={"streaming": True})

async def call_llm(prompt: str):
    stream = llm.astream(prompt)
    result = ""
    async for chunk in stream:
        if chunk.content:
            result += chunk.content
    return result

async def analyze_restaurant(restaurant: dict) -> dict:
    prompt = build_review_prompt(restaurant)
    response =await call_llm(prompt)
    
    result = {
        "placeId": restaurant["placeId"],
        "name": restaurant["name"],
        "url": restaurant["url"],
        "llmResult": response
    }
    print(result)
    return result
async def run_llm_analysis(data: dict) -> list:
    restaurants = data.get("restaurants", [])
    print("---------------------------------------------")
    print(restaurants)
    if not isinstance(restaurants, list):
        raise ValueError("restaurants는 리스트여야 합니다.")

    tasks = [analyze_restaurant(r) for r in restaurants]
    return await asyncio.gather(*tasks)

async def get_final_recommendation(results: list, input_text:str) -> str:
    """
    전체 흐름: 개별 분석 → 종합 프롬프트 → 최종 추천 생성
    """
    final_prompt = build_final_recommendation_prompt(results, input_text)
    return await call_llm(final_prompt)
