# 헬채널 자동 추천 웹 대시보드 (Streamlit)
import pandas as pd
import streamlit as st

# 예시 데이터셋 - 향후 크롤링 데이터로 대체 예정
data = [
    {"채널": "중천 Ch.70", "장비": "혼돈 목걸이"},
    {"채널": "마계 Ch.6", "장비": "천재지변 반지"},
    {"채널": "중천 Ch.70", "장비": "혼돈 목걸이"},
    {"채널": "백해 Ch.3", "장비": "보우건"},
    {"채널": "마계 Ch.6", "장비": "혼돈 반지"},
    {"채널": "중천 Ch.63", "장비": "혼돈 반지"},
    {"채널": "중천 Ch.70", "장비": "혼돈 목걸이"},
    {"채널": "마계 Ch.2", "장비": "페어리 반지"},
    {"채널": "중천 Ch.63", "장비": "천재지변 반지"},
]

def get_hot_channels(data):
    df = pd.DataFrame(data)
    channel_counts = df["채널"].value_counts()
    gear_counts = df.groupby("채널")["장비"].apply(list)

    result = pd.DataFrame({
        "득템 수": channel_counts,
        "드랍된 장비 목록": gear_counts
    }).reset_index().rename(columns={"index": "채널"})

    result.sort_values(by="득템 수", ascending=False, inplace=True)
    result.reset_index(drop=True, inplace=True)
    return result

# Streamlit 웹 앱 시작
st.set_page_config(page_title="헬채널 자동 추천", layout="wide")
st.title("🔥 던파 태초 헬채널 자동 추천 시스템")

st.markdown("""
    **실시간 득템 정보를 기반으로 가장 핫한 헬 채널을 추천합니다!!**
    
    > 데이터는 수집된 득템 기록을 바탕으로 분석되며, 향후 자동 크롤링 시스템으로 확장될 예정입니다.
""")

# 결과 출력
result = get_hot_channels(data)
st.dataframe(result, use_container_width=True)

# 핫한 채널 강조 출력
top_channel = result.iloc[0]
st.success(f"🎯 지금 가장 핫한 채널은 **{top_channel['채널']}** 입니다! 드랍 수: {top_channel['득템 수']}개")
