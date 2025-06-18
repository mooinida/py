# app/data/save_data.py
import os
import requests
import sys
# ✅ 수정: 이 sys.path.append 줄은 Uvicorn의 --app-dir ./app 사용 시 불필요하거나 충돌을 일으킬 수 있으므로 제거합니다.
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from dotenv import load_dotenv
from multiprocessing import Pool
# ✅ 수정: 같은 디렉토리 내의 모듈은 상대 경로 임포트
from .process_restaurant import process_restaurant
import json

# ✅ .env 파일 로드 (이 스크립트는 /home/ubuntu/py/app/data 에 있고, .env는 /home/ubuntu/py/app 에 있으므로
# 두 단계 위로 가서 .env를 찾아 로드하도록 경로를 지정합니다.)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")

LAT_START = 37.41992
LAT_END = 37.67961
LNG_START = 126.8059
LNG_END = 127.1683
STEP_LAT = 0.0045
STEP_LNG = 0.0055

def search_restaurants_by_kakaomap(longitude, latitude, radius=500):
    url = "https://dapi.kakao.com/v2/local/search/category.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    
    all_results = []
    for page in range(1, 4):
        params = {
            "category_group_code": "FD6",
            "x": longitude,
            "y": latitude,
            "radius": radius,
            "size": 15,
            "page": page,
            "sort": "distance"
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        if "documents" in data:
            all_results.extend(data["documents"])
            if len(data["documents"]) < 15:
                break
        else:
            break

    return all_results

def generate_coords():
    coords = []
    lat = LAT_START
    while lat <= LAT_END:
        lng = LNG_START
        while lng <= LNG_END:
            coords.append((round(lat, 6), round(lng, 6)))
            lng += STEP_LNG
        lat += STEP_LAT
    return coords

if __name__ == "__main__":
    #coords = generate_coords()

    #all_results = []
    #count = 1
    # for lat, lng in coords:
    #     results = search_restaurants_by_kakaomap(longitude=lng, latitude=lat)
    #     print(count)
    #     count+=1
    #     all_results.extend(results)

    # 중복 제거
    #unique_restaurants = list({int(r["id"]): r for r in all_results}.values())
    #print(f"📌 총 식당 수: {len(unique_restaurants)}")
    # with open("backup_restaurants.jsonl", "w", encoding="utf-8") as f:
    #     for r in unique_restaurants:
    #         f.write(json.dumps(r, ensure_ascii=False) + "\n")
    
    
    with open("backup_restaurants.jsonl", "r", encoding="utf-8") as f:
        unique_restaurants = [json.loads(line.strip()) for line in f]
    total = len(unique_restaurants)
    print(f"📦 처리할 식당 수: {len(unique_restaurants)}")
    
    with Pool(processes=8) as pool:
        for i, result in enumerate(pool.imap_unordered(process_restaurant, unique_restaurants), 1):
             print(f"[{i}/{total}] {result}")
    print("크롤링 완료")
