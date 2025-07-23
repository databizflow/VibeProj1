import requests
import pandas as pd
import streamlit as st

st.title("국토교통부 실거래가 지도 데이터 조회 데모")

st.markdown("""
- 지도 영역(경도/위도), 연도, 유형을 입력하면 실거래가 데이터를 조회합니다.
- poiType: A(아파트), B(연립/다세대), C(단독/다가구) 등
""")

minX = st.text_input("minX (경도 최소)", "126.9669616")
minY = st.text_input("minY (위도 최소)", "37.5583183")
maxX = st.text_input("maxX (경도 최대)", "126.9903076")
maxY = st.text_input("maxY (위도 최대)", "37.5741701")
srhYear = st.text_input("조회 연도 (예: 2024)", "2024")
poiType = st.text_input("유형 (A:아파트, B:연립/다세대 등)", "A")

if st.button("실거래가 데이터 조회"):
    url = "https://rt.molit.go.kr/pt/gis/getMarker.do"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://rt.molit.go.kr/pt/gis/gis.do?srhThingSecd=A&mobileAt=",
        "Origin": "https://rt.molit.go.kr",
        "X-Requested-With": "XMLHttpRequest",
        # 필요시 쿠키 추가 (예: "Cookie": "WMONID=...; JSESSIONID=...;")
    }
    data = {
        "minX": minX,
        "minY": minY,
        "maxX": maxX,
        "maxY": maxY,
        "srhYear": srhYear,
        "poiType": poiType
    }
    with st.spinner("데이터 요청 중..."):
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            try:
                result = response.json()
                st.success("데이터 수신 성공!")
                # 데이터 구조에 따라 표로 변환
                if isinstance(result, dict):
                    # 주요 데이터가 'data' 또는 'result' 키에 있을 수 있음
                    for key in ['data', 'result', 'markers', 'list']:
                        if key in result:
                            df = pd.DataFrame(result[key])
                            st.dataframe(df)
                            break
                    else:
                        st.write(result)
                elif isinstance(result, list):
                    df = pd.DataFrame(result)
                    st.dataframe(df)
                else:
                    st.write(result)
            except Exception as e:
                st.error(f"JSON 파싱 실패: {e}")
                st.text_area("원본 응답", response.text, height=300)
        else:
            st.error(f"요청 실패: {response.status_code}")
