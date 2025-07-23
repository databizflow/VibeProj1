import streamlit as st
import requests
import pandas as pd

st.title("🌱 스마트팜 생산성 향상 모델 조회")

API_KEY = "GYPT+FqRtVQKsjVs5jPi9/0U4AjAorf3OYe3pEn6jI4MDx9QgNwtQiN2E6Cn/qytt0RioPGKvWKxZeVuM2RAmA=="

# 작물/기능 분리 구조로 재구성
CROP_FUNC_OPTIONS = {
    "완숙토마토": ["일사량별", "생육상태별", "농가 일자별"],
    "딸기": ["일사량별", "생육상태별", "농가 일자별"],
    "파프리카": ["일사량별", "생육상태별", "농가 일자별"]
}
CROP_FUNC_TO_KEY = {
    ("완숙토마토", "일사량별"): "완숙토마토-일사량별",
    ("완숙토마토", "생육상태별"): "완숙토마토-생육상태별",
    ("완숙토마토", "농가 일자별"): "완숙토마토-농가 일자별",
    ("딸기", "일사량별"): "딸기-일사량별",
    ("딸기", "생육상태별"): "딸기-생육상태별",
    ("딸기", "농가 일자별"): "딸기-농가 일자별",
    ("파프리카", "일사량별"): "파프리카-일사량별",
    ("파프리카", "생육상태별"): "파프리카-생육상태별",
    ("파프리카", "농가 일자별"): "파프리카-농가 일자별"
}

# 명세서 기반 모든 작물/기능/엔드포인트/파라미터 정의
CROP_OPTIONS = {
    # 완숙토마토
    "완숙토마토-일사량별": {
        "endpoint": "http://apis.data.go.kr/1390000/SmartFarmModel/tmtsolarqst",
        "params": [
            ("시설유형코드", ["FS_BD(비닐)", "FS_UY(유리)"]),
            ("생육단계코드", ["1(생육초기)", "21(생육중기9~10월)", "22(생육중기11~12월)", "23(생육중기1~2월)", "24(생육중기3~6월)", "3(생육말기7~8월)"])
        ]
    },
    "완숙토마토-생육상태별": {
        "endpoint": "http://apis.data.go.kr/1390000/SmartFarmModel/tmtgrwtrqst",
        "params": [
            ("시설유형코드", ["FS_BD(비닐)", "FS_UY(유리)"]),
            ("생육단계코드", ["1(생육초기)", "21(생육중기9~10월)", "22(생육중기11~12월)", "23(생육중기1~2월)", "24(생육중기3~6월)", "3(생육말기7~8월)"])
        ]
    },
    "완숙토마토-농가 일자별": {
        "endpoint": "http://apis.data.go.kr/1390000/SmartFarmModel/tmtdayrqst",
        "params": [
            ("농가코드", []),
            ("주차", [])
        ]
    },
    # 딸기
    "딸기-일사량별": {
        "endpoint": "http://apis.data.go.kr/1390000/SmartFarmModel/stbsolarqst",
        "params": [
            ("시설유형코드", ["FS_CI(연동)", "FS_SI(단동)"]),
            ("생육단계코드", ["1(1화방 출뢰기)", "2(1화방 첫 수확기)", "3(생육중기12월)", "4(생육중기1월)", "5(생육중기2월)", "6(생육중기3월)", "7(생육말기4~5월)"])
        ]
    },
    "딸기-생육상태별": {
        "endpoint": "http://apis.data.go.kr/1390000/SmartFarmModel/stbgrwtrqst",
        "params": [
            ("시설유형코드", ["FS_CI(연동)", "FS_SI(단동)"]),
            ("생육단계코드", ["1(1화방 출뢰기)", "2(1화방 첫 수확기)", "3(생육중기12월)", "4(생육중기1월)", "5(생육중기2월)", "6(생육중기3월)", "7(생육말기4~5월)"])
        ]
    },
    "딸기-농가 일자별": {
        "endpoint": "http://apis.data.go.kr/1390000/SmartFarmModel/stbdayrqst",
        "params": [
            ("농가코드", []),
            ("주차", [])
        ]
    },
    # 파프리카
    "파프리카-일사량별": {
        "endpoint": "http://apis.data.go.kr/1390000/SmartFarmModel/ppksolarqst",
        "params": [
            ("시설유형코드", ["FS_P(여름-평창)", "FS_C(여름-철원)", "FS_W(겨울)"]),
            ("생육단계코드", ["1(생육초기)", "2(생육중기4월)", "3(생육중기5~6월)", "4(생육중기6~7월)", "5(생육중기8월)", "6(생육중기9월)", "7(생육말기10월~)"])
        ]
    },
    "파프리카-생육상태별": {
        "endpoint": "http://apis.data.go.kr/1390000/SmartFarmModel/ppkgrwtrqst",
        "params": [
            ("시설유형코드", ["FS_P(여름-평창)", "FS_C(여름-철원)", "FS_W(겨울)"]),
            ("생육단계코드", ["1(생육초기)", "2(생육중기4월)", "3(생육중기5~6월)", "4(생육중기6~7월)", "5(생육중기8월)", "6(생육중기9월)", "7(생육말기10월~)"])
        ]
    },
    "파프리카-농가 일자별": {
        "endpoint": "http://apis.data.go.kr/1390000/SmartFarmModel/ppkdayrqst",
        "params": [
            ("농가코드", []),
            ("주차", [])
        ]
    }
}

# 한글 컬럼명 매핑(대표 예시, 필요시 확장)
COLUMN_KOR_MAP = {
    "frmhsCode": "농가코드",
    "week": "주차",
    "accmltSolradQy": "누적일사량",
    "opairTp": "외기온도",
    "odrOuttrn": "생산량",
    "deAvrgTp": "일평균온도",
    "dtimeAvrgTp": "주간평균온도",
    "nightAvrgTp": "야간평균온도",
    "dawnTp": "새벽온도",
    "dtimeAvrgHd": "주간평균습도",
    "remndrCo2": "잔존 Co2",
    "suplyCunt": "급액횟수",
    "suplyEc": "급액EC",
    "suplyPh": "급액pH",
    "otmSuplyQy": "1회 급액량",
    "deSuplyQy": "1일 급액량",
    "datetm": "일자",
    "grwtLt": "생장길이",
    "stemThck": "줄기굵기",
    "fcluHg": "화방높이",
    "plln": "초장",
    "flgYld": "엽수",
    "crownDnt": "관부직경",
    "day1s": "1화방 출뢰일수",
    "week4": "첫 수확 평균일수",
    "fyerOuttrn": "연간수량",
    "yldRate": "작기 내 수량비율",
    "grtm": "배지온도",
    "ndeNo": "착과마디-개화마디"
}

def to_numeric_col(col):
    def parse_val(v):
        try:
            v = str(v).replace(",", "").strip()
            if v == "" or v.lower() == "none":
                return None
            if "~" in v:
                a, b = v.split("~")
                return (float(a) + float(b)) / 2
            return float(v)
        except:
            return None
    return col.apply(parse_val)

# 작물, 기능 분리 선택
crop = st.selectbox("작물", list(CROP_FUNC_OPTIONS.keys()))
func = st.selectbox("기능", CROP_FUNC_OPTIONS[crop])
crop_func = CROP_FUNC_TO_KEY[(crop, func)]
BASE_URL = CROP_OPTIONS[crop_func]["endpoint"]
params_dict = {}
for param_name, options in CROP_OPTIONS[crop_func]["params"]:
    if options:  # 선택지가 있는 경우
        val = st.selectbox(param_name, options)
        params_dict[param_name] = val.split("(")[0]
    else:  # 직접 입력
        val = st.text_input(param_name)
        params_dict[param_name] = val

if st.button("모델 정보 가져오기"):
    # 파라미터명 영문 변환
    param_map = {
        "시설유형코드": "fcltyTyCode",
        "생육단계코드": "grwhStepCode",
        "농가코드": "frmhsCode",
        "주차": "week"
    }
    api_params = {"serviceKey": API_KEY, "returnType": "json"}
    for k, v in params_dict.items():
        if v:
            api_params[param_map.get(k, k)] = v
    try:
        response = requests.get(BASE_URL, params=api_params)
        if response.status_code == 200:
            data = response.json()
            if 'response' in data:
                data = data['response']
            if 'body' in data and 'items' in data['body']:
                items = data['body']['items']
                if isinstance(items, dict) and 'item' in items:
                    item = items['item']
                    if isinstance(item, dict):
                        item = [item]
                    df = pd.DataFrame(item)
                    if not df.empty:
                        df = df.rename(columns=COLUMN_KOR_MAP)
                        # 평균값을 마지막 행으로 추가 (범위형, 숫자형 모두 처리)
                        avg_row = {}
                        for col in df.columns:
                            if df[col].astype(str).str.contains("~").any():
                                vals = []
                                for v in df[col]:
                                    try:
                                        parts = str(v).replace(",", "").split("~")
                                        if len(parts) == 2:
                                            vals.append((float(parts[0]) + float(parts[1])) / 2)
                                        elif len(parts) == 1:
                                            vals.append(float(parts[0]))
                                    except:
                                        continue
                                avg_row[col] = round(sum(vals) / len(vals), 2) if vals else ""
                            else:
                                try:
                                    vals = pd.to_numeric(df[col], errors='coerce')
                                    if not vals.isnull().all():
                                        avg_row[col] = round(vals.mean(), 2)
                                    else:
                                        avg_row[col] = ""
                                except:
                                    avg_row[col] = ""
                        df_with_avg = pd.concat([df, pd.DataFrame([avg_row])], ignore_index=True)
                        df_with_avg.index = list(df_with_avg.index[:-1]) + ['평균']
                        st.success(f"{len(df)}건의 데이터 (마지막 행: 평균값)")
                        st.dataframe(df_with_avg)
                        # 분석 요약 텍스트 추가 (기존과 동일)
                        st.subheader("분석 요약")
                        summary_texts = []
                        if '생산량' in df.columns:
                            prod = pd.to_numeric(df['생산량'], errors='coerce')
                            avg = prod.mean()
                            mx = prod.max()
                            mn = prod.min()
                            summary_texts.append(f"이 데이터에서 평균 생산량은 {avg:.2f}kg입니다. 가장 높은 생산량은 {mx:.2f}kg, 가장 낮은 생산량은 {mn:.2f}kg로 나타났습니다.")
                        if '생장길이' in df.columns:
                            grow = pd.to_numeric(df['생장길이'], errors='coerce')
                            avg = grow.mean()
                            mx = grow.max()
                            mn = grow.min()
                            summary_texts.append(f"평균 생장길이는 {avg:.2f}cm이며, 최대 {mx:.2f}cm, 최소 {mn:.2f}cm입니다.")
                        if '외기온도' in df.columns:
                            temps = df['외기온도'].astype(str).str.split('~')
                            temp_vals = []
                            for t in temps:
                                try:
                                    if len(t) == 2:
                                        temp_vals.append((float(t[0]) + float(t[1])) / 2)
                                    elif len(t) == 1:
                                        temp_vals.append(float(t[0]))
                                except:
                                    pass
                            if temp_vals:
                                avg = sum(temp_vals) / len(temp_vals)
                                summary_texts.append(f"외기온도의 평균은 {avg:.2f}℃입니다.")
                        for txt in summary_texts:
                            st.info(txt)
                        # 모든 컬럼을 숫자/범위평균으로 변환한 DataFrame 생성
                        numeric_df = pd.DataFrame({col: to_numeric_col(df[col]) for col in df.columns})
                        st.subheader("수치형 변환 데이터 미리보기")
                        st.dataframe(numeric_df)
                        st.write("각 컬럼의 유효값 개수:", numeric_df.count())
                        if len(numeric_df) < 2:
                            st.warning("분석 및 시각화는 데이터가 2건 이상일 때만 가능합니다. 더 많은 데이터를 조회해 주세요.")
                        else:
                            # 최빈값(Mode) 추가
                            st.subheader("최빈값(Mode)")
                            for col in numeric_df.columns:
                                mode = numeric_df[col].mode()
                                if not mode.empty and pd.notnull(mode.iloc[0]):
                                    st.write(f"{col}의 최빈값: {mode.iloc[0]}")
                            # 상관관계 분석
                            st.subheader("상관관계 분석")
                            corr = numeric_df.corr()
                            st.dataframe(corr)
                            # 상관관계 해석 텍스트 추가
                            strong_corrs = []
                            for i, col1 in enumerate(corr.columns):
                                for j, col2 in enumerate(corr.columns):
                                    if j <= i:
                                        continue
                                    val = corr.iloc[i, j]
                                    if abs(val) >= 0.7:
                                        direction = "같은 방향" if val > 0 else "반대 방향"
                                        strength = "매우 강한" if abs(val) > 0.85 else "강한"
                                        strong_corrs.append((col1, col2, val, direction, strength))
                            # 절대값이 가장 큰 상관관계 2개만 출력
                            strong_corrs = sorted(strong_corrs, key=lambda x: abs(x[2]), reverse=True)[:2]
                            if strong_corrs:
                                st.info("\n".join([
                                    f"'{col1}'와(과) '{col2}'는 {strength} {direction}의 상관관계({val:.2f})가 있습니다."
                                    for col1, col2, val, direction, strength in strong_corrs
                                ]))
                            else:
                                st.info("0.7 이상의 강한 상관관계가 발견되지 않았습니다.")
                            # 그래프 시각화
                            st.subheader("그래프 시각화")
                            # 생산량 bar chart
                            if '생산량' in numeric_df.columns:
                                st.bar_chart(numeric_df['생산량'])
                                st.caption("위 그래프는 각 데이터의 ‘생산량(kg)’을 막대그래프로 나타낸 것입니다.")
                            # 생장길이 bar chart
                            if '생장길이' in numeric_df.columns:
                                st.bar_chart(numeric_df['생장길이'])
                                st.caption("위 그래프는 각 데이터의 ‘생장길이(cm)’를 막대그래프로 나타낸 것입니다.")
                            # 외기온도 bar chart
                            if '외기온도' in numeric_df.columns:
                                st.bar_chart(numeric_df['외기온도'])
                                st.caption("위 그래프는 각 데이터의 ‘외기온도(℃)’를 막대그래프로 나타낸 것입니다.")
                            # 산점도(Scatter chart) 예시: 생산량 vs 생장길이
                            if '생산량' in numeric_df.columns and '생장길이' in numeric_df.columns:
                                scatter_df = numeric_df[['생산량', '생장길이']]
                                st.scatter_chart(scatter_df)
                                st.caption("위 산점도는 ‘생산량’과 ‘생장길이’의 관계를 시각화한 것입니다.")
                    else:
                        st.warning("조회 결과가 없습니다.")
                        st.json(data)
                else:
                    st.warning("조회 결과가 없습니다.")
                    st.json(data)
            else:
                st.warning("조회 결과가 없습니다.")
                st.json(data)
        else:
            st.error(f"API 오류: {response.status_code}")
            st.text(response.text)
    except Exception as e:
        st.error(f"요청 실패: {e}")
