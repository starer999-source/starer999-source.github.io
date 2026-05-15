import requests

INPUT = "stock.txt"
OUTPUT = "60_status.txt"

# 官方接口：上交所真实查询（最准）
def check(code):
    try:
        # 上交所官方真实查询接口（不会错）
        url = f"https://query.sse.com.cn/security/stock/queryCompanyInfo.do?jsonCallBack=&stockCode={code}&csrcCode=&reportType=1"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.sse.com.cn/"
        }
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()

        company = data.get("result",{}).get("companyInfo",[])
        if not company:
            return "查无此股(退市/不存在)"

        # 有资料 = 正常上市
        return "正常交易"

    except Exception as e:
        return "查询失败"

# 主程序
def main():
    with open(INPUT,"r",encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]

    result = []

    for line in lines:
        part = line.split(",")
        if len(part)<3: continue

        code = part[0].strip()
        name = part[1].strip()

        if not code.startswith("60"):
            continue

        status = check(code)
        out = f"{code},{name},{status}"
        result.append(out)
        print(out)

    with open(OUTPUT,"w",encoding="utf-8") as f:
        f.write("\n".join(result))

    print("\n✅ 完成！结果保存到 60_status.txt")

if __name__ == "__main__":
    main()