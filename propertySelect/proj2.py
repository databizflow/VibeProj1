from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options

# Edge WebDriver 경로 지정 (확실한 전체 경로)
edge_driver_path = "D:\Windows_user\Downloads\edgedriver_win32/msedgedriver.exe"

# 옵션 설정 (창 띄우려면 생략하거나 최소화 X)
options = Options()
# options.add_argument('--headless')  # ❌ 창을 띄우려면 이 줄을 제거

# Service 객체 생성
service = EdgeService(executable_path=edge_driver_path)

# 드라이버 실행
driver = webdriver.Edge(service=service, options=options)

# 테스트용 네이버 접속
driver.get("https://www.naver.com")

# 종료 방지
input("엔터를 누르면 창이 닫힙니다...")
driver.quit()