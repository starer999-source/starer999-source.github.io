import requests

def check_stock(code):
    # 東方財富 搜索頁（永遠能用）
    url = f"https://www.eastmoney.com/s?code={code}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        r = requests.get(url, headers=headers, timeout=5)
        html = r.text

        # 把網頁寫入檔案給你看
        with open("result.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("==== 網頁取回成功，已儲存到 result.html =====")

        # 判斷方法：看有沒有「股票名稱」
        if "退" in html or "總計：0" in html or "不存在" in html:
            print(f"❌ {code} = 退市或不存在")
        else:
            print(f"✅ {code} = 正常交易")

    except Exception as e:
        print("錯誤：", e)

if __name__ == "__main__":
    check_stock("600167")