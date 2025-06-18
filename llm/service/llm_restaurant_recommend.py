from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

# ✅ 환경 변수에서 API 키 로드
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# ✅ Gemini LLM 객체 생성
llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-pro",
    google_api_key=GOOGLE_API_KEY
)

# ✅ 사용자 자연어 입력 → 식당 5~10개 추천

def recommend_restaurants_from_text(user_input: str) -> str:
    """
    사용자의 자연어 요청에 기반하여 LLM이 식당을 추천하도록 함.

    Args:
        user_input (str): 사용자 요청 문장 (ex: "비 오는 날 조용히 술 마실 식당 추천해줘")

    Returns:
        str: 추천 식당 목록 (이름, 주소, 분위기, 대표메뉴 등 포함)
    """
    prompt = PromptTemplate.from_template(
        """
        사용자가 이렇게 말했습니다:
        "{text}"

        위 요청에 어울리는 서울 또는 수도권 내 식당 5~10곳을 추천해 주세요.
        각 식당은 아래 정보를 포함해야 합니다:
        - 이름
        - 주소
        - 대표 메뉴 1~2개
        - 영업시간
        - 가격대 (₩, ₩₩, ₩₩₩ 중 하나)
        - 분위기 (예: 조용함, 활기참, 혼밥 가능, 데이트 적합 등)
        - 나이대 (젊은, 나이대가 높은)
        - 주차장 유무(O , X)

        리스트 형식으로 간결하게 정리해 주세요.
        대답없이 리스트만.
        """
    )

    chain = prompt | llm
    result = chain.invoke({"text": user_input})
    return result.content.strip()

# ✅ 테스트 코드
if __name__ == "__main__":
    user_input = "성신여대역 주변 비 오는 날 조용히 막걸리 마시기 좋은 식당 추천해줘"
    print(recommend_restaurants_from_text(user_input))
