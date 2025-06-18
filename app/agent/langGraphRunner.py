# app/agent/langGraphRunner.py
import os
import sys
import asyncio
from dotenv import load_dotenv # .env 파일 로드를 위해 추가

# ✅ 수정: sys.path.append는 Uvicorn의 --app-dir 옵션을 사용하면 불필요하므로 제거합니다.
# load_dotenv()는 명시적으로 경로를 지정하여 안전하게 로드합니다.
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # 이 줄 제거 또는 주석 처리

# .env 파일 로드 (이 스크립트는 /home/ubuntu/py/app/agent 에 있고, .env는 /home/ubuntu/py/app 에 있으므로
# 한 단계 위로 가서 .env를 찾아 로드하도록 경로를 지정합니다.)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

from langgraph.graph import StateGraph, END
from langchain_core.runnables import Runnable
from typing import TypedDict
from langchain_core.runnables import RunnableLambda

# ✅ 수정: 'app' 패키지 기준으로 절대 임포트
from app.tools.gpt_tools import (
    get_location_tool,
    get_menu_tool,
    get_context_tool,
    intersection_restaurant,
    get_restaurant_info,
    final_recommend,
)

# ✅ 수정: 상태에 user_input 포함
class State(TypedDict):
    user_id:str
    user_input: str
    location: list
    menu: list
    context: list
    candidates: dict          
    restaurant_details: dict  
    restaurant_aiRating: dict
    result: dict
    end:bool

# ✅ 각 노드에서 user_input을 다음 상태로 명시적으로 넘겨줘야 함
async def location_node(state: State) -> dict:
    location = await get_location_tool(state["user_id"],state["user_input"])
    print(location)
    return {
        "location": location,
        "user_input": state["user_input"]
    }

async def menu_node(state: State) -> dict:
    menu = await get_menu_tool(state["user_id"],state["user_input"])
    return {
        "menu": menu,
        "user_input": state["user_input"]
    }

async def context_node(state: State) -> dict:
    context = await get_context_tool(state["user_id"],state["user_input"])
    return {
        "context": context,
        "user_input": state["user_input"]
    }
def next_tool_selector(state: dict) -> str:
    if state.get("end") is True:
        return END
    return "intersection_node"

async def extract_all(state: State) -> dict:
    try:
        location_task = get_location_tool(state["user_id"], state["user_input"])
        menu_task = get_menu_tool(state["user_id"], state["user_input"])
        context_task = get_context_tool(state["user_id"], state["user_input"])

        location, menu, context = await asyncio.gather(location_task, menu_task, context_task, return_exceptions=True)
        if not location.get("restaurants"):
            return {"end": True,
                    "result":"장소명과 함께 다시 입력하여 주세요"
                    }

        return {
            "location": location,
            "menu": menu,
            "context": context
        }
    except Exception as e:
        print(f"❌ extract_all 에러 발생: {e}")
        return {"location": {}, "menu": {}, "context": {}, "error": str(e)}

async def intersection_node(state: State) -> dict:
    candidates = intersection_restaurant(
        state["location"],
        state["menu"],
        state["context"]
    )
    return {"candidates": candidates}

async def detail_node(state: State) -> dict:
    details = get_restaurant_info(state["user_id"],state["candidates"])
    return {"restaurant_details": details}

async def final_node(state: State) -> dict:  
    result = await final_recommend(state["restaurant_details"], state["user_input"])
    return {
        "result": result["result"],
        "restaurant_aiRating": result["aiRating"]
    }

# LangGraph 설정
graph_builder = StateGraph(State)

graph_builder.add_node("location_node", location_node)
graph_builder.add_node("menu_node", menu_node)
graph_builder.add_node("context_node", context_node)
graph_builder.add_node("intersection_node", intersection_node)
graph_builder.add_node("detail_node", detail_node)
graph_builder.add_node("final_node", final_node)
graph_builder.add_node("extract_filters", RunnableLambda(extract_all))

graph_builder.set_entry_point("extract_filters")

graph_builder.add_conditional_edges(
    "extract_filters",
    next_tool_selector 
)
graph_builder.add_edge("intersection_node", "detail_node")
graph_builder.add_edge("detail_node", "final_node")
graph_builder.add_edge("final_node", END)

# 실행 함수
async def run_recommendation_pipeline(state: dict) -> dict:
    graph = graph_builder.compile()
    result = await graph.ainvoke(state)
    return result
