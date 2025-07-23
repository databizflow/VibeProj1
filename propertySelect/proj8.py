import requests
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
import folium

def geocode_kakao(address):
    rest_api_key = "1c9f4a7dee3d780fbd967fc6d1a58e21"
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {rest_api_key}"}
    params = {"query": address}
    resp = requests.get(url, headers=headers, params=params)
    st.write("카카오 API 응답:", resp.status_code, resp.json())  # ← 이 줄 추가
    if resp.status_code == 200 and resp.json()["documents"]:
        doc = resp.json()["documents"][0]
        x = float(doc["x"])
        y = float(doc["y"])
        return x, y
    return None, None

st.title("국토교통부 실거래가 지도 데이터 조회 (지역명 입력)")

address = st.text_input("지역명 (예: 서울 강남구 삼성동)", "서울 강남구 삼성동")
srhYear = st.text_input("조회 연도 (예: 2024)", "2024")
poiType = st.text_input("유형 (A:아파트, B:연립/다세대 등)", "A")
range_deg = st.slider("검색 범위(도 단위, 0.001~0.05)", min_value=0.001, max_value=0.05, value=0.01, step=0.001, format="%.3f")

if st.button("실거래가 데이터 조회"):
    x, y = geocode_kakao(address)
    if x and y:
        minX, maxX = x - range_deg, x + range_deg
        minY, maxY = y - range_deg, y + range_deg
        url = "https://rt.molit.go.kr/pt/gis/getMarker.do"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://rt.molit.go.kr/pt/gis/gis.do?srhThingSecd=A&mobileAt=",
            "Origin": "https://rt.molit.go.kr",
            "X-Requested-With": "XMLHttpRequest",
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
                    markers = None
                    for key in ['data', 'result', 'markers', 'list']:
                        if key in result:
                            markers = result[key]
                            break
                    if markers and isinstance(markers, list) and len(markers) > 0:
                        df = pd.DataFrame(markers)
                        st.success(f"총 {len(df)}건의 거래 데이터가 조회되었습니다.")
                        st.dataframe(df)
                        m = folium.Map(location=[y, x], zoom_start=15)
                        for row in df.itertuples():
                            lat = getattr(row, 'lat', None) or getattr(row, 'LAT', None) or getattr(row, 'y', None)
                            lng = getattr(row, 'lng', None) or getattr(row, 'LNG', None) or getattr(row, 'x', None)
                            if lat and lng:
                                folium.Marker([float(lat), float(lng)], popup=str(getattr(row, 'APT_NM', getattr(row, '단지명', '')))).add_to(m)
                        st.session_state['result_df'] = df  # 결과를 세션에 저장
                        st.session_state['map'] = m         # 지도도 세션에 저장
                    else:
                        st.info("해당 지역/범위 내에 거래 데이터가 없습니다. 범위를 넓혀보세요.")
                except Exception as e:
                    st.error(f"JSON 파싱 실패: {e}")
                    st.text_area("원본 응답", response.text, height=300)
            else:
                st.error(f"요청 실패: {response.status_code}")
    else:
        st.error("지오코딩(좌표 변환)에 실패했습니다. 주소를 확인하세요.")

# 버튼 밖에서 결과를 표시
if 'result_df' in st.session_state and st.session_state['result_df'] is not None:
    st.dataframe(st.session_state['result_df'])
    st_folium(st.session_state['map'], width=700, height=500)
