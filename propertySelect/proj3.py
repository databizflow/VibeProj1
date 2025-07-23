from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Edge WebDriver 경로 (본인 경로로 정확히 설정)
edge_driver_path = r"D:\Windows_user\Downloads\edgedriver_win32\msedgedriver.exe"

options = Options()
options.add_argument("start-maximized")  # 창 최대화

service = EdgeService(executable_path=edge_driver_path)
driver = webdriver.Edge(service=service, options=options)

driver.get("https://rt.molit.go.kr/pt/gis/gis.do?srhThingSecd=A&mobileAt=")

wait = WebDriverWait(driver, 15)

# iframe이 로드될 때까지 기다리기
iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#ifrm")))

# iframe으로 전환
driver.switch_to.frame(iframe)

# iframe 안에서 원하는 요소 기다리기
sido_select_elem = wait.until(EC.presence_of_element_located((By.ID, "SIDO_NM")))

# 시/도 선택 (서울특별시)
sido_select = Select(sido_select_elem)
sido_select.select_by_visible_text("서울특별시")
time.sleep(1)

# 구 선택 (종로구)
gungu_select = Select(driver.find_element(By.ID, "GUNGU_NM"))
gungu_select.select_by_visible_text("종로구")
time.sleep(1)

# 거래년도 선택 (2024)
year_select = Select(driver.find_element(By.ID, "DEAL_YMD1"))
year_select.select_by_visible_text("2024")
time.sleep(0.5)

# 거래월 선택 (5월)
month_select = Select(driver.find_element(By.ID, "DEAL_YMD2"))
month_select.select_by_visible_text("05")
time.sleep(0.5)

# 주택유형 선택 (아파트)
house_type_select = Select(driver.find_element(By.ID, "HKIND"))
house_type_select.select_by_visible_text("아파트")
time.sleep(0.5)

# 검색 버튼 클릭
search_button = driver.find_element(By.ID, "btn_search")
search_button.click()

time.sleep(5)  # 결과 기다리기

# 결과 테이블 파싱
table = driver.find_element(By.ID, "resultTable")
rows = table.find_elements(By.TAG_NAME, "tr")

data = []
for row in rows[1:]:  # 헤더 제외
    cols = row.find_elements(By.TAG_NAME, "td")
    data.append([col.text for col in cols])

# 메인 문서로 돌아오기
driver.switch_to.default_content()

driver.quit()

# 데이터프레임 만들기 및 저장
columns = ["번호", "아파트명", "주소", "거래금액", "계약일", "전용면적", "층", "건축년도", "도로명"]
df = pd.DataFrame(data, columns=columns)
df.to_excel("apt_trade_data.xlsx", index=False, encoding="utf-8-sig")

print("크롤링 및 엑셀 저장 완료")
