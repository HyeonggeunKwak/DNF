import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import subprocess

# 던파아카라이브 크롤링 함수 및 JSON 저장
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
        print(f"던파아카라이브 접속 실패: {e}")
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

# 실행 예시
data = crawl_dnf_archive_and_save()