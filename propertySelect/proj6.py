import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import io
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
import tempfile
import os

# 한글 폰트 적용 (최상단에서 한 번만)
font_path = "NanumGothic.ttf"
font_manager.fontManager.addfont(font_path)  # 폰트 직접 등록
font_name = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams['font.family'] = font_name
rc('font', family=font_name)

# 한글 폰트 경로 (프로젝트 폴더에 NanumGothic.ttf 파일이 있어야 함)
FONT_PATH = "NanumGothic.ttf"

# Streamlit UI
st.title("부동산 리포트 자동화 SaaS 데모")

region = st.text_input("지역명 (예: 서울 강남구)", "")
min_budget = st.number_input("최소 예산 (만원)", min_value=0)
max_budget = st.number_input("최대 예산 (만원)", min_value=0)
email = st.text_input("결과 받을 이메일 주소", "")

if st.button("리포트 생성 및 이메일 발송"):

    if not region or min_budget == 0 or max_budget == 0 or not email:
        st.error("모든 필드를 입력해주세요!")
    else:
        with st.spinner("데이터 수집 중..."):
            # 예시 데이터 생성
            data = {
                "아파트명": ["A아파트", "B아파트", "C아파트"],
                "평형(㎡)": [84, 59, 114],
                "거래금액(만원)": [90000, 70000, 110000],
                "거래일": ["2025-06-01", "2025-06-10", "2025-06-15"]
            }
            df = pd.DataFrame(data)
            # 예산 필터링
            df_filtered = df[(df["거래금액(만원)"] >= min_budget) & (df["거래금액(만원)"] <= max_budget)]

        st.success(f"{len(df_filtered)}건의 거래 데이터가 필터링되었습니다.")

        # 분석 및 시각화
        st.subheader("평형별 거래금액 평균")
        avg_prices = df_filtered.groupby("평형(㎡)")["거래금액(만원)"].mean()

        fig, ax = plt.subplots()
        ax.set_title("평형별 거래금액 평균")  # 한글 제목
        ax.set_ylabel("평균 거래금액 (만원)")  # 한글 y축
        avg_prices.plot(kind="bar", ax=ax)
        st.pyplot(fig)

        # PDF 생성 (fpdf2 + 한글폰트)
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font('NanumGothic', '', FONT_PATH)  # uni=True 생략
        pdf.set_font('NanumGothic', '', 16)
        pdf.cell(0, 10, f"{region} 부동산 거래 리포트", ln=1, align="C")
        pdf.ln(10)

        pdf.set_font("NanumGothic", size=12)
        pdf.cell(0, 10, f"총 거래 건수: {len(df_filtered)}", ln=1)
        pdf.cell(0, 10, f"예산 범위: {min_budget}만원 ~ {max_budget}만원", ln=1)
        pdf.ln(10)

        # matplotlib 차트를 메모리에 이미지로 저장 후 PDF에 삽입
        img_buf = io.BytesIO()
        fig.savefig(img_buf, format='PNG')
        img_buf.seek(0)

        pdf.image(img_buf, x=10, y=60, w=pdf.w - 20)
        
        # 임시 파일로 저장 (이메일 첨부 위해)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            pdf.output(tmpfile.name)
            pdf_path = tmpfile.name

        st.success("PDF 리포트가 생성되었습니다.")

        # 이메일 전송
        st.info("이메일 전송 중...")
        try:
            msg = EmailMessage()
            msg["Subject"] = f"{region} 부동산 리포트"
            msg["From"] = "abcfgf777@gmail.com"  # 본인 이메일
            msg["To"] = "abcfgf777@gmail.com"
            msg.set_content(f"{region} 부동산 거래 리포트를 첨부합니다.")

            with open(pdf_path, "rb") as f:
                pdf_data = f.read()
            msg.add_attachment(pdf_data, maintype="application", subtype="pdf", filename=f"{region}_real_estate_report.pdf")

            # Gmail SMTP 예시
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login("abcfgf777@gmail.com", "dtmp yxsh yqoq glad")  # 앱 비밀번호 사용 권장
                smtp.send_message(msg)

            st.success("이메일이 성공적으로 전송되었습니다!")
        except Exception as e:
            st.error(f"이메일 전송 실패: {e}")
        finally:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)