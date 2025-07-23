import requests

proxies_list = [
    "http://104.248.63.17:31583",
    "http://138.197.157.45:3128",
    "http://51.158.123.35:8811",
    # 더 추가 가능
]

url = "http://apis.data.go.kr/1613000/AptTradeInfoService/getTradeAptList"
params = {
    'serviceKey': "GYPT%2BFqRtVQKsjVs5jPi9%2F0U4AjAorf3OYe3pEn6jI4MDx9QgNwtQiN2E6Cn%2Fqytt0RioPGKvWKxZeVuM2RAmA%3D%3D",
    'LAWD_CD': '11110',
    'DEAL_YMD': '202405',
    'numOfRows': 10,
    'pageNo': 1
}

for proxy_url in proxies_list:
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }
    try:
        r = requests.get(url, params=params, proxies=proxies, timeout=5)
        if r.status_code == 200:
            print(f"성공! 프록시: {proxy_url}")
            print(r.text[:500])
            break
        else:
            print(f"프록시 {proxy_url} 실패, 상태 코드: {r.status_code}")
    except Exception as e:
        print(f"프록시 {proxy_url} 연결 실패: {e}")
