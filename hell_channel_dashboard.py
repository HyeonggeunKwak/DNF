import pandas as pd
import streamlit as st
import requests
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime
import subprocess

# 던파 아카라이브 실시간 득템 정보 크롤링 함수 및 JSON 저장
def crawl_dnf_archive_and_save():
    url = "https://www.dnfarchive.com/board/view/notice"  # 던파 아카라이브 게시판 URL (예시)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        posts = soup.select(".board-list tbody tr")  # 게시글 리스트 부분

        data = []
        for post in posts:
            title = post.select_one(".title a").text.strip()
            link = post.select_one(".title a")["href"]
            
            # 제목에서 채널과 장비 정보를 추출하는 함수
            channel = extract_channel_from_title(title)
            gear = extract_gear_from_title(title)
            
            data.append({"채널": channel, "장비": gear, "출처": "던파아카라이브", "링크": link})

        # JSON 파일로 저장
        json_path = "docs/dnf_archive_drop.json"
        os.makedirs("docs", exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"[자동 저장 완료] {json_path} ({len(data)}건) → {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 자동 git 커밋 및 푸시
        auto_git_push()

        return data
    except Exception as e:
        st.warning(f"던파 아카라이브 접속 실패: {e}")
        return []

# 채널 정보 추출 (예시: 제목에서 '채널 1' 등의 형식으로 추출)
def extract_channel_from_title(title):
    if "채널" in title:
        # 예시: '채널 1', '채널 2' 등
        return title.split("채널")[1].strip()
    return "기타"

# 장비 정보 추출 (예시: 제목에서 '태초'라는 키워드로 장비 추출)
def extract_gear_from_title(title):
    if "태초" in title:
        return "태초 장비"
    return "기타"

# 자동 git 커밋 및 푸시 함수
def auto_git_push():
    try:
        subprocess.run(["git", "add", "docs/dnf_archive_drop.json"], check=True)
        subprocess.run(["git", "commit", "-m", "자동 업데이트: dnf_archive_drop.json"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("[Git Push 완료] dnf_archive_drop.json 업로드 성공!!")
    except subprocess.CalledProcessError as e:
        print(f"[Git 오류] 자동 커밋 또는 푸시 실패: {e}")

# 정적 JSON 파일로부터 데이터 로드
def load_cached_data():
    try:
        url = "https://hyeonggeunkwak.github.io/DNF/dnf_archive_drop.json"
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
    result = pd.DataFrame({
        "득템 수": channel_counts,
        "드랍된 장비 목록": gear_counts,
    }).reset_index().rename(columns={"index": "채널"})

    result.sort_values(by="득템 수", ascending=False, inplace=True)
    result.reset_index(drop=True, inplace=True)
    return result

# Streamlit 웹 앱 시작
st.set_page_config(page_title="헬채널 자동 추천", layout="wide")
st.title("🔥 던파 태초 헬채널 자동 추천 시스템")

st.markdown(""" 
    **실시간 득템 정보를 기반으로 가장 핫한 헬 채널을 추천합니다!!**
    
    > 던파 아카라이브 및 디시파 등에서 태초 득템 데이터를 수집해 자동 추천합니다!!
""")

# 실시간 크롤링 시도
if st.sidebar.button("던파 아카라이브에서 실시간 데이터 크롤링"):
    data = crawl_dnf_archive_and_save()
    if data:
        st.sidebar.success("실시간 데이터 크롤링 및 저장 완료!!")
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