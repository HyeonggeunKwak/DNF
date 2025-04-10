# 헬채널 자동 추천 웹 대시보드 (Streamlit)
import pandas as pd
import streamlit as st
import requests
import json
import os
from bs4 import BeautifulSoup

# DFGEAR 실시간 득템 정보 크롤링 함수
def crawl_dfgear():
    url = "https://dfgear.kr/bbs/board.php?bo_table=drop"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.select(".tbl_head01 tbody tr")

        data = []
        for row in rows:
            cols = row.select("td")
            if len(cols) >= 3:
                channel = cols[2].text.strip()
                gear = cols[1].text.strip()
                data.append({"채널": channel, "장비": gear, "카테고리": categorize_channel(channel)})

        with open("dfgear_drop.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return data
    except Exception as e:
        st.warning(f"DFGEAR 접속 실패: {e}")
        return []

# 채널 이름에 따라 카테고리 분류
def categorize_channel(name):
    if "벨마이어" in name:
        return "벨마이어 구역"
    elif "지벤" in name:
        return "지벤 구역"
    elif "백해" in name:
        return "백해 구역"
    elif "마계" in name:
        return "마계 구역"
    elif "중천" in name:
        return "중천 구역"
    elif "바하이트" in name:
        return "바하이트 구역"
    else:
        return "기타"

# 정적 JSON 파일로부터 데이터 로드
def load_cached_data():
    try:
        url = "https://yourusername.github.io/dfgear-data/dfgear_drop.json"  # 실제 GitHub Pages 주소로 변경할 것
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.warning(f"정적 데이터 로드 실패: {e}")
        return []

# 득템 상위 채널 정리
def get_hot_channels(data):
    df = pd.DataFrame(data)
    if df.empty:
        return pd.DataFrame()

    channel_counts = df["채널"].value_counts()
    gear_counts = df.groupby("채널")["장비"].apply(list)
    categories = df.drop_duplicates("채널").set_index("채널")["카테고리"]

    result = pd.DataFrame({
        "득템 수": channel_counts,
        "드랍된 장비 목록": gear_counts,
        "카테고리": categories
    }).reset_index().rename(columns={"index": "채널"})

    result.sort_values(by="득템 수", ascending=False, inplace=True)
    result.reset_index(drop=True, inplace=True)
    return result

# Streamlit 웹 앱 시작
st.set_page_config(page_title="헬채널 자동 추천", layout="wide")
st.title("🔥 던파 태초 헬채널 자동 추천 시스템")

st.markdown("""
    **실시간 득템 정보를 기반으로 가장 핫한 헬 채널을 추천합니다!!**

    > DFGEAR, 디시파 인증글, 던파 공식 커뮤니티 등에서 태초 득템 데이터를 수집해 자동 추천합니다!!
    > 본 시스템은 GitHub Pages 또는 실시간 크롤링으로 데이터를 수집합니다!!
""")

# 실시간 크롤링 시도
if st.sidebar.button("DFGEAR에서 실시간 데이터 크롤링"):
    data = crawl_dfgear()
    if data:
        st.sidebar.success("실시간 데이터 크롤링 완료!!")
else:
    # 정적 JSON 데이터 로드
    data = load_cached_data()

# 결과 출력
if data:
    result = get_hot_channels(data)
    st.dataframe(result, use_container_width=True)

    if not result.empty:
        top_channel = result.iloc[0]
        st.success(f"🎯 지금 가장 핫한 채널은 **{top_channel['채널']}** 입니다! 드랍 수: {top_channel['득템 수']}개")
else:
    st.error("데이터를 불러오지 못했습니다. 캐시 파일 경로나 구조를 확인해주세요!!")
