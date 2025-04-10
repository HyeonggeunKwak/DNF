# 헬채널 자동 추천 웹 대시보드 (Streamlit)
import pandas as pd
import streamlit as st
import requests
from bs4 import BeautifulSoup

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
    else:
        return "기타"

# 자동 크롤링 함수 - 예시: DFGEAR 득템 게시판 파싱 (구조에 따라 수정 필요)
def crawl_dfgear():
    url = "https://dfgear.kr/bbs/board.php?bo_table=drop"  # 예시 주소
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        st.warning("DFGEAR에서 데이터를 불러오지 못했습니다!!")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.select(".wr-list tr")

    result = []
    keywords = ["중천", "마계", "백해", "벨마이어", "지벤"]

    for item in items:
        tds = item.select("td")
        if len(tds) < 4:
            continue
        title = tds[1].text.strip()
        for keyword in keywords:
            if keyword in title:
                parts = title.split()
                for part in parts:
                    if "Ch." in part:
                        채널 = f"{keyword} {part}"
                        장비 = parts[-1] if len(parts) > 1 else "미확인"
                        카테고리 = categorize_channel(채널)
                        result.append({"채널": 채널, "장비": 장비, "카테고리": 카테고리})
    return result

def get_hot_channels(data):
    df = pd.DataFrame(data)
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

    > DFGEAR, 디시파 인증글, 던파 공식 커뮤니티 등에서 태초 득템 데이터를 실시간으로 수집해서 자동 추천합니다!!
""")

# 크롤링 데이터 가져오기
data = crawl_dfgear()

# 결과 출력
if data:
    result = get_hot_channels(data)
    st.dataframe(result, use_container_width=True)

    # 핫한 채널 강조 출력
    if not result.empty:
        top_channel = result.iloc[0]
        st.success(f"🎯 지금 가장 핫한 채널은 **{top_channel['채널']}** 입니다! 드랍 수: {top_channel['득템 수']}개")
else:
    st.error("데이터를 불러오지 못했습니다. 사이트 구조가 변경되었을 수 있습니다!!")
