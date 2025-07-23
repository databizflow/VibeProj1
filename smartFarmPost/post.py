import streamlit as st
import requests
import pandas as pd

# 1) 기본 설정
service_key = "YOUR_SERVICE_KEY"  # 발급받은 Key 입력
base_url = "http://www.smartfarmkorea.net/Agree_WS/webservices/ProvideRestService"

st.title("🌱 스마트팜 작기별 대시보드")

# 2) 농가 & 작기 선택
st.sidebar.header("선택 항목")
if not st.session_state.get("user_list"):
    # 사용자 목록 가져오기
    resp = requests.get(f"{base_url}/getIdentityDataList/{service_key}")
    users = resp.json()
    st.session_state.user_list = users

user = st.sidebar.selectbox(
    "농가 선택",
    options=[u["userId"] for u in st.session_state.user_list],
)

# 선택된 농가의 작기 목록
resp = requests.get(f"{base_url}/getCroppingSeasonDataList/{service_key}/{user}")
seasons = resp.json()
season_df = pd.DataFrame(seasons)
selected = st.sidebar.selectbox("작기 선택", options=season_df["croppingSerlNo"])
season = season_df[season_df["croppingSerlNo"] == selected].iloc[0]

# 작기 메타 정보 출력
st.subheader(f"{season['croppingSeasonName']} ({season['croppingDate']} ~ {season['croppingEndDate']})")
st.write("📊 재배 정보:", {
    "면적(㎡)": season["calCultivationArea"],
    "재식수량": season["calPlantNum"],
    "기준온도(°C)": season["stndTemp"],
    "기준광량": season["stndSolar"]
})

# 3) 환경 / 제어 / 생육 데이터 조회 함수
def fetch_data(op):
    url = f"{base_url}/{op}/{service_key}/{user}/{selected}"
    res = requests.get(url)
    return pd.DataFrame(res.json())

# 데이터 가져오기
env = fetch_data("getEnvironmentDataList")
ctrl = fetch_data("getControlDataList")
grow = fetch_data("getGrowthDataList")

# 4) 시각화
st.line_chart(env.set_index("measDate")[["temperature","humidity","CO2"]])
st.line_chart(ctrl.set_index("measDate")[["waterOn","lightOn"]])  # 예시 컬럼
st.dataframe(grow)

