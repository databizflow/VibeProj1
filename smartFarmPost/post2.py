import streamlit as st
import requests
import pandas as pd

# API KEY
API_KEY = "e45ee433e75a4d5fa7ebf04859741db0"

# Streamlit 앱 제목
st.title("스마트팜 품목별 빅데이터 비교")

# 사용자 입력
crop1 = st.selectbox("비교할 작물 1 선택", ["토마토", "상추", "딸기"])
crop2 = st.selectbox("비교할 작물 2 선택", ["토마토", "상추", "딸기"])

def get_crop_data(crop):
    url = "https://smartfarm.data.go.kr/openapi/cropBigdata.do"  # 예시, 실제 URL로 변경 필요
    params = {
        "serviceKey": API_KEY,
        "cropName": crop,
        "returnType": "json"
    }
    res = requests.get(url, params=params)
    if res.status_code == 200:
        return res.json()
    else:
        st.error("API 요청 실패")
        return None

# 데이터 불러오기
data1 = get_crop_data(crop1)
data2 = get_crop_data(crop2)

# 비교 결과 표시
if data1 and data2:
    st.subheader(f"{crop1} vs {crop2} 비교")
    # 예시 항목: 재배 면적, 수확량 등
    st.write("예: 수확량 비교")
    st.metric(label=crop1, value=data1["yield"])
    st.metric(label=crop2, value=data2["yield"])
