# app/tools/gpt_tools.py
import os
import sys
# ✅ 수정: sys.path.append는 Uvicorn의 --app-dir ./app 사용 시 불필요하므로 제거합니다.
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import asyncio

# ✅ 수정: 'app' 패키지 기준으로 절대 임포트
from app.service.saveRestaurant_pipeline import (
    get_location_and_context,
    get_location_and_menu,
    get_coordinates_from_location,
    get_location_from_text,
    get_nearby_restaurants_DB,
    findall_restaurants_DB, # findall_restaurants_DB 추가
    filtering_restaurant, # filtering_restaurant 추가
)
# ✅ 수정: 'app' 패키지 기준으로 절대 임포트
from app.bring_to_server import (
    bring_menu_filter_restaurants,
    bring_context_filter_restaurants,
    bring_restaurants_list,
    bring_rating_count
)
# ✅ 수정: 'app' 패키지 기준으로 절대 임포트
from app.llm.gemini_call import run_llm_analysis, get_final_recommendation
from collections import Counter
from typing import TypedDict
from langgraph.graph import StateGraph # StateGraph는 langGraph.py에 있으므로 여기서 제거 (혹시 모르니 유지해도 큰 문제는 없음)

# Define the state structure (langGraphRunner.py에 정의되어 있으므로 여기서는 제거하거나 유지)
# class State(TypedDict):
#     user_id:str
#     user_input: str
#     location: dict
#     menu: dict
#     context: dict
#     candidates: dict
#     restaurant_details: dict
#     restaurant_aiRating: dict
#     result: dict

# LangGraph-compatible tools

async def get_location_tool(user_id:str, input_text: str) -> dict:
    print("locationTool사용")
    location = await get_location_from_text(input_text)
    coords = await get_coordinates_from_location(location)
    if "error" in coords:
        return coords
    restaurants = get_nearby_restaurants_DB(user_id, coords["latitude"], coords["longitude"], radius=500)
    return restaurants


async def get_menu_tool(user_id:str ,input_text: str) -> dict:
    print("getmenuTool사용")
    keywords = await get_location_and_menu(input_text)
    restaurants = bring_menu_filter_restaurants(user_id, keywords)
    return restaurants


async def get_context_tool(user_id:str, input_text: str) -> dict:
    print("getcontextTool사용")
    contexts = await get_location_and_context(input_text)
    restaurants = bring_context_filter_restaurants(user_id, contexts)
    return restaurants

async def extract_all(user_id:str, input_text:str):
    location_task = get_location_tool(user_id, input_text)
    menu_task = get_menu_tool(user_id, input_text)
    context_task = get_context_tool(user_id, input_text)

    location, menu, context = await asyncio.gather(location_task, menu_task, context_task)
    return location, menu, context


def get_restaurant_info(user_id:str, restaurant_ids: dict) -> dict:
    print("교집합:")
    print(restaurant_ids)
    try:
        # ✅ 수정: filtering_restaurant 함수도 saveRestaurant_pipeline에서 가져와 사용합니다.
        restaurants = restaurant_ids.get("restaurants", [])
        data = bring_rating_count(user_id, restaurants)
        filtered_restaurant = filtering_restaurant(data) # 이미 saveRestaurant_pipeline에서 임포트됨
        result = bring_restaurants_list(user_id, filtered_restaurant)
        return result
    except Exception as e:
        return {"error": f"파싱 실패: {str(e)}"}


def intersection_restaurant(location:dict, menu:dict, context:dict):
    """
    여러 리스트에서 2번 이상 등장한 식당 ID만 반환하는 도구.
    """
    print("교집합함수 호출")
    try:
        # set() 에 dict를 바로 넣을 수 없으므로, ID 목록으로 변경해야 함
        location_ids = [r['placeId'] for r in location.get("restaurants", []) if 'placeId' in r]
        menu_ids = [r['placeId'] for r in menu.get("restaurants", []) if 'placeId' in r]
        context_ids = [r['placeId'] for r in context.get("restaurants", []) if 'placeId' in r]

        strategies = [
            ("location_menu_context", set(location_ids) & set(menu_ids) & set(context_ids)),
            ("location_menu", set(location_ids) & set(menu_ids)),
            ("location_context", set(location_ids) & set(context_ids)),
            ("location", set(location_ids))  # fallback: 무조건 사용
        ]

        for key, result_set in strategies:
            if key != "location" and len(result_set) < 3:
                print(f"❌ {key}: {len(result_set)}개 → 패스")
                continue

            print(f"✅ {key} 사용 (총 {len(result_set)}개)")
            return {"restaurants": list(result_set), "source": key}

        print("⚠️ 추천 가능한 식당이 없습니다.")
        return {"restaurants": [], "source": "none"}

    except Exception as e:
        return {"error": str(e)}


async def final_recommend(restaurants_info: dict, input_text:str) -> dict:
    ai_rating = await run_llm_analysis(restaurants_info)
    result = await get_final_recommendation(ai_rating, input_text)
    return {"result":result,
            "aiRating":ai_rating
            }

# graph_builder = StateGraph(State) # langGraphRunner.py에 정의되어 있으므로 여기서 제거
