import requests

def check_yesterday_trade(code):
    print("================================")
    print(f"【查詢】股票：{code}")
    print("================================")

    # 你唯一能成功的网址
    url = f"https://so.eastmoney.com/web/s?keyword={code}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=5)
        html = resp.text

        if "相關結果約0個" in html:
            print("❌ 昨日無法交易（退市/無數據）")
        else:
            print("✅ 昨日可正常交易")

    except:
        print("❌ 查詢失敗")

if __name__ == "__main__":
    # 只查一只
    check_yesterday_trade("600000")