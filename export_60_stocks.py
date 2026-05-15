import requests
import pandas as pd
from datetime import datetime

# 今日日期
today = "20260514"
# 输出文件名
output_file = f"60开头股票行情_{today}.csv"

# 东方财富日线接口（不复权）
base_url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"

# 生成60开头股票代码列表（600000-605999）
codes = [f"60{i:04d}" for i in range(0, 6000)]

# 存储数据
data = []

print(f"开始获取 {len(codes)} 只60开头股票行情...")

for code in codes:
    # 跳过退市股（可根据你的stockclean_all过滤）
    # 接口参数
    params = {
        "secid": f"1.{code}",  # 1=沪市
        "ut": "fa5fd1943c7b386f172d6893dbfba10",
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55",
        "klt": "101",  # 日线
        "fqt": "0",    # 不复权
        "beg": today,
        "end": today,
        "smplmt": "1",
        "lmt": "1"
    }
    try:
        resp = requests.get(base_url, params=params, timeout=5)
        resp.raise_for_status()
        res_json = resp.json()
        klines = res_json.get("data", {}).get("klines", [])
        if klines:
            # 解析数据：日期,开盘,收盘,最高,最低,成交量
            line = klines[0].split(",")
            open_price = float(line[1])
            close_price = float(line[2])
            high_price = float(line[3])
            low_price = float(line[4])
            data.append([code, open_price, close_price, high_price, low_price])
    except Exception as e:
        # 跳过无数据/退市股
        continue

# 生成DataFrame
df = pd.DataFrame(data, columns=["代码", "开盘", "收盘", "最高", "最低"])
# 保存CSV
df.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"导出完成！共 {len(df)} 只股票，文件：{output_file}")