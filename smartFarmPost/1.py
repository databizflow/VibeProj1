import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta

# 다른 모듈들 import
try:
    from post import *  # post.py의 함수들 사용
except ImportError:
    pass

try:
    from post3 import CROP_OPTIONS, COLUMN_KOR_MAP, to_numeric_col  # post3.py의 데이터 활용
except ImportError:
    CROP_OPTIONS = {}
    COLUMN_KOR_MAP = {}

# 페이지 설정
st.set_page_config(
    page_title="🌱 스마트팜 작물 재배 전략 분석 도구",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)
# 메인 타이틀
st.title("🌱 스마트팜 작물 재배 전략 분석 도구")
st.markdown("**작물 선택부터 수확량 예측까지, 데이터 기반 재배 전략 수립**")

# 사이드바 설정
st.sidebar.header("🎯 재배 목적 선택")
scenario = st.sidebar.radio(
    "시나리오를 선택하세요:",
    ["🌱 신규 농장 계획", "📊 기존 농장 최적화", "🔍 작물 비교 분석"]
)

# 시나리오별 설명
scenario_descriptions = {
    "🌱 신규 농장 계획": "새로운 농장을 계획 중이시군요! 최적의 작물과 시설을 추천해드립니다.",
    "📊 기존 농장 최적화": "기존 농장의 수확량을 늘려보세요! 개선점을 찾아드립니다.",
    "🔍 작물 비교 분석": "어떤 작물이 더 유리할지 비교해보세요! 수익성을 분석합니다."
}

st.info(scenario_descriptions[scenario])

# 재배 조건 설정
st.subheader("📝 재배 조건 설정")

col1, col2, col3, col4 = st.columns(4)

with col1:
    location = st.selectbox(
        "📍 재배 지역",
        ["용인시 처인구", "평창", "철원", "기타 지역"]
    )

with col2:
    season = st.selectbox(
        "🗓️ 재배 시작 시기",
        ["7월 말", "8월 초", "9월", "10월", "11월"]
    )

with col3:
    facility = st.selectbox(
        "🏗️ 시설 유형",
        ["비닐하우스", "유리온실", "연동하우스", "단동하우스"]
    )

with col4:
    # 시나리오별 작물 옵션 조정
    if scenario == "🌱 신규 농장 계획":
        crop_options = ["완숙토마토 (추천)", "딸기", "파프리카"]
    elif scenario == "📊 기존 농장 최적화":
        crop_options = ["완숙토마토", "딸기", "파프리카", "상추"]
    else:  # 작물 비교 분석
        crop_options = ["완숙토마토", "딸기", "파프리카"]
    
    crop = st.selectbox("🌱 주요 작물", crop_options)

# 분석 실행 버튼
if st.button("🚀 분석 시작하기", type="primary", use_container_width=True):
    # 작물별 기본 데이터
    crop_data = {
        "완숙토마토": {"yield": 2450, "profit": 8820, "base": 3600},
        "완숙토마토 (추천)": {"yield": 2450, "profit": 8820, "base": 3600},
        "딸기": {"yield": 1890, "profit": 7350, "base": 3000},
        "파프리카": {"yield": 2100, "profit": 6890, "base": 2800},
        "상추": {"yield": 3200, "profit": 4500, "base": 2200}
    }
    
    # 시설별 보정 계수
    facility_multiplier = {
        "비닐하우스": 1.0,
        "유리온실": 1.25,
        "연동하우스": 1.15,
        "단동하우스": 0.95
    }
    
    # 계산된 값
    base_data = crop_data[crop]
    multiplier = facility_multiplier[facility]
    calculated_yield = int(base_data["yield"] * multiplier)
    calculated_profit = int(base_data["profit"] * multiplier)
    
    # 핵심 지표 표시
    st.subheader("📊 핵심 지표")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📈 예상 수확량",
            value=f"{calculated_yield:,}kg",
            delta="전년 대비 +15%"
        )
    
    with col2:
        st.metric(
            label="💰 예상 수익",
            value=f"{calculated_profit:,}만원",
            delta="투자 대비 +28%"
        )
    
    with col3:
        st.metric(
            label="🌡️ 최적 환경 달성률",
            value="92%",
            delta="우수 수준"
        )
    
    with col4:
        st.metric(
            label="⭐ 재배 성공률",
            value="87%",
            delta="높은 성공 가능성"
        )
    
    # 차트 섹션
    st.subheader("📈 분석 차트")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**월별 예상 수확량**")
        # 월별 수확량 데이터
        months = ['8월', '9월', '10월', '11월', '12월', '1월', '2월', '3월']
        yields = [180, 320, 420, 380, 340, 290, 250, 220]
        
        # 시설별 보정 적용
        adjusted_yields = [y * multiplier for y in yields]
        
        chart_data = pd.DataFrame({
            '월': months,
            '수확량(kg)': adjusted_yields
        })
        
        fig = px.line(chart_data, x='월', y='수확량(kg)', 
                     title="월별 예상 수확량 변화",
                     markers=True)
        fig.update_traces(line_color='#10B981', line_width=3)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("**환경 조건 최적화 현황**")
        # 레이더 차트 데이터
        categories = ['온도', '습도', '일사량', 'CO2', '급액량', 'EC']
        current_values = [92, 88, 95, 85, 90, 87]
        optimal_values = [100, 100, 100, 100, 100, 100]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=current_values,
            theta=categories,
            fill='toself',
            name='현재 수준',
            line_color='#3B82F6'
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=optimal_values,
            theta=categories,
            fill='toself',
            name='최적 수준',
            line_color='#EF4444',
            line_dash='dash'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="환경 조건 최적화 현황"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 작물별 수익성 비교
    st.subheader("🔍 작물별 수익성 비교")
    
    comparison_data = {
        "작물": ["완숙토마토", "딸기", "파프리카"],
        "예상수익(만원)": [8820, 7350, 6890],
        "㎡당수익(원)": [3600, 3000, 2800],
        "수익성(%)": [92, 76, 72]
    }
    
    # 시설별 보정 적용
    for i in range(len(comparison_data["예상수익(만원)"])):
        comparison_data["예상수익(만원)"][i] = int(comparison_data["예상수익(만원)"][i] * multiplier)
        comparison_data["㎡당수익(원)"][i] = int(comparison_data["㎡당수익(원)"][i] * multiplier)
    
    df_comparison = pd.DataFrame(comparison_data)
    
    col1, col2, col3 = st.columns(3)
    
    for i, (col, row) in enumerate(zip([col1, col2, col3], df_comparison.itertuples())):
        with col:
            color = ["green", "red", "orange"][i]
            st.markdown(f"""
            <div style="border: 2px solid {color}; border-radius: 10px; padding: 20px; text-align: center; background-color: rgba(255,255,255,0.1);">
                <h4>{row.작물}</h4>
                <h2 style="color: {color};">{row.예상수익:,}만원</h2>
                <p>㎡당 {row.㎡당수익:,}원</p>
                <div style="background-color: lightgray; border-radius: 10px; height: 10px;">
                    <div style="background-color: {color}; height: 10px; border-radius: 10px; width: {row.수익성}%;"></div>
                </div>
                <small>수익성: {row.수익성}%</small>
            </div>
            """, unsafe_allow_html=True)
    
    # 생육 단계별 관리 포인트
    st.subheader("🌱 생육 단계별 관리 포인트")
    
    stages = [
        {
            "stage": "생육 초기 (1-4주)",
            "description": "온도 24-26°C 유지, 습도 70-80%, 일사량 관리 중점",
            "status": "현재 단계",
            "color": "blue"
        },
        {
            "stage": "생육 중기 (5-12주)",
            "description": "수분 관리 강화, EC 2.0-2.5 유지, 화방 관리",
            "status": "다음 단계",
            "color": "gray"
        },
        {
            "stage": "생육 말기 (13주 이후)",
            "description": "수확량 최적화, 품질 관리, 수확 타이밍",
            "status": "예정",
            "color": "gray"
        }
    ]
    
    for i, stage in enumerate(stages, 1):
        if stage["color"] == "blue":
            st.info(f"**{i}. {stage['stage']}** - {stage['description']} ({stage['status']})")
        else:
            st.write(f"**{i}. {stage['stage']}** - {stage['description']} ({stage['status']})")
    
    # 개선 제안
    st.subheader("💡 맞춤형 개선 제안")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("**🎯 즉시 실행 가능**")
        st.write("✅ 야간 온도를 2°C 낮춰 품질 개선")
        st.write("✅ 급액 EC를 2.2로 조정하여 수량 증대")
        st.write("✅ CO2 농도 1000ppm 유지로 광합성 효율 향상")
    
    with col2:
        st.info("**📈 중장기 개선안**")
        st.write("📊 자동 환경제어 시스템 도입 (+12% 수익)")
        st.write("💡 LED 보광등 설치로 연중 생산 (+20% 수량)")
        st.write("🔧 양액 자동화로 인건비 절감 (-15% 비용)")
    
    # 위험 요소 및 대응 방안
    st.subheader("⚠️ 위험 요소 및 대응 방안")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.warning("**기상 위험**")
        st.write("폭염, 한파, 태풍 등 기상 이변")
        st.write("🛡️ 보온/차광막 자동화, 재해보험 가입")
    
    with col2:
        st.error("**병해충 위험**")
        st.write("바이러스, 곰팡이, 해충 발생")
        st.write("🛡️ 방제 시스템, 생물학적 방제제 활용")
    
    with col3:
        st.info("**시장 위험**")
        st.write("가격 변동, 수급 불균형")
        st.write("🛡️ 계약재배, 다품종 재배로 위험 분산")

# 다른 모듈과의 연동 기능
st.sidebar.markdown("---")
st.sidebar.subheader("🔗 추가 기능")

if st.sidebar.button("📊 상세 생산성 모델 조회"):
    st.sidebar.info("post3.py의 생산성 모델 기능을 활용할 수 있습니다.")

if st.sidebar.button("📈 품목별 빅데이터 비교"):
    st.sidebar.info("post2.py의 빅데이터 비교 기능을 활용할 수 있습니다.")

if st.sidebar.button("🌾 작기별 대시보드"):
    st.sidebar.info("post.py의 작기별 분석 기능을 활용할 수 있습니다.")

# 푸터
st.markdown("---")
st.markdown("© 2024 스마트팜 작물 재배 전략 분석 도구. 데이터 기반 농업으로 더 나은 미래를 만들어갑니다.")
