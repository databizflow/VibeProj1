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
    if resp.status_code == 200 and resp.json()["documents"]:
        doc = resp.json()["documents"][0]
        x = float(doc["x"])
        y = float(doc["y"])
        return x, y
    return None, None

st.title("국토교통부 실거래가 지도 데이터 조회 (지역명 입력)")

address = st.text_input("지역명 (예: 서울 강남구 삼성동)", "서울 강남구 삼성동")
srhYear = st.text_input("조회 연도 (예: 2025)", "2025")
poiType = st.text_input("유형 (A:아파트, B:연립/다세대 등)", "A")

# km 단위 슬라이더
range_km = st.slider("검색 반경(km)", min_value=0.1, max_value=5.0, value=1.0, step=0.1, format="%.1f")
range_deg = range_km / 111  # km를 도 단위로 변환
st.caption(f"실제 검색 범위: ±{range_deg:.4f}도 (약 {range_km:.1f}km)")

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
                        # 각 단지별로 ptDtl.do에서 실거래가 정보 추가
                        recent_prices = []
                        recent_dates = []
                        for idx, row in df.iterrows():
                            detail_url = "https://rt.molit.go.kr/pt/gis/ptDtl.do"
                            detail_data = {
                                "srhThingSecd": "A",
                                "srhDelngSecd": "1",
                                "dtlLi": row["emdCode"],
                                "dtlYear": srhYear,
                                "dtlAmount": "0",
                                "srhAprpnHsmpCode": row["aprpnHsmpCode"]
                            }
                            detail_resp = requests.post(detail_url, headers=headers, data=detail_data)
                            if detail_resp.status_code == 200:
                                detail_json = detail_resp.json()
                                danji_list = detail_json.get("danjiList", [])
                                if danji_list:
                                    latest = danji_list[0]
                                    price = latest.get("thingAmount", "")
                                    date = latest.get("cntrctDe", "")
                                    recent_prices.append(price)
                                    recent_dates.append(date)
                                else:
                                    recent_prices.append("")
                                    recent_dates.append("")
                            else:
                                recent_prices.append("")
                                recent_dates.append("")
                        df["최근거래금액(만원)"] = recent_prices
                        df["최근계약일"] = recent_dates
                        # 컬럼명 한글 매핑
                        col_rename = {
                            "aprpnHsmpCode": "단지코드",
                            "aprpnHsmpNm": "단지명",
                            "signguCode": "시군구코드",
                            "emdCode": "법정동코드",
                            "mnnm": "번지",
                            "slno": "호",
                            "lo": "경도",
                            "la": "위도",
                            "최근거래금액(만원)": "최근거래금액(만원)",
                            "최근계약일": "최근계약일"
                        }
                        df = df.rename(columns=col_rename)
                        st.success(f"총 {len(df)}건의 거래 데이터가 조회되었습니다.")
                        st.dataframe(df)
                        m = folium.Map(location=[y, x], zoom_start=15)
                        for row in df.itertuples():
                            lat = getattr(row, '위도', None)
                            lng = getattr(row, '경도', None)
                            apt_nm = getattr(row, '단지명', '')
                            price = getattr(row, '최근거래금액(만원)', '')
                            date = getattr(row, '최근계약일', '')
                            popup_text = f"{apt_nm}<br>거래금액: {price}만원<br>계약일: {date}"
                            if lat and lng:
                                folium.Marker([float(lat), float(lng)], popup=popup_text).add_to(m)
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
