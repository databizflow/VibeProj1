import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
import tempfile
import os

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
            data = {
                "아파트명": ["A아파트", "B아파트", "C아파트"],
                "평형(㎡)": [84, 59, 114],
                "거래금액(만원)": [90000, 70000, 110000],
                "거래일": ["2025-06-01", "2025-06-10", "2025-06-15"]
            }
            df = pd.DataFrame(data)
            df_filtered = df[(df["거래금액(만원)"] >= min_budget) & (df["거래금액(만원)"] <= max_budget)]

        st.success(f"{len(df_filtered)}건의 거래 데이터가 필터링되었습니다.")

        st.subheader("평형별 거래금액 평균")
        avg_prices = df_filtered.groupby("평형(㎡)")["거래금액(만원)"].mean()
        fig, ax = plt.subplots()
        avg_prices.plot(kind="bar", ax=ax)
        ax.set_ylabel("평균 거래금액 (만원)")
        st.pyplot(fig)

        # PDF 생성
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=16)
        pdf.cell(200, 10, txt=f"{region} 부동산 거래 리포트", ln=1, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=f"총 거래 건수: {len(df_filtered)}", ln=1)
        pdf.cell(200, 10, txt=f"예산 범위: {min_budget}만원 ~ {max_budget}만원", ln=1)
        pdf.ln(10)

        # 임시 파일에 차트 저장 후 PDF에 삽입
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            fig.savefig(tmpfile.name)
            tmp_img_path = tmpfile.name

        pdf.image(tmp_img_path, x=10, y=60, w=pdf.w - 20)
        os.remove(tmp_img_path)

        # PDF를 메모리 저장
        pdf_output = pdf.output(dest='S').encode('latin1')
        pdf_bytes = io.BytesIO(pdf_output)

        st.success("PDF 리포트가 생성되었습니다.")

        # 이메일 전송
        st.info("이메일 전송 중...")
        try:
            msg = EmailMessage()
            msg["Subject"] = f"{region} 부동산 리포트"
            msg["From"] = "your_email@gmail.com"  # 본인 이메일
            msg["To"] = email
            msg.set_content(f"{region} 부동산 거래 리포트를 첨부합니다.")
            msg.add_attachment(pdf_bytes.getvalue(), maintype="application", subtype="pdf", filename=f"{region}_real_estate_report.pdf")

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login("your_email@gmail.com", "your_app_password")
                smtp.send_message(msg)

            st.success("이메일이 성공적으로 전송되었습니다!")
        except Exception as e:
            st.error(f"이메일 전송 실패: {e}")
