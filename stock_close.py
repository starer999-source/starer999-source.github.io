import pandas as pd
from datetime import datetime
import requests

# -------- 你的飞书机器人Webhook --------
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/f252038d-9a55-4d93-9fb9-432340e552c0"

import akshare as ak
import pandas as pd
import time
import requests
from datetime import datetime

# -------- 配置 --------

stocks = [
    {"name": "广发证券", "code": "000776"},
    {"name": "浦发银行", "code": "600000"},
    {"name": "农业银行", "code": "601288"}
]

# -------- 1. 批量获取数据 --------
today = datetime.now().strftime("%Y-%m-%d")
data = []

for s in stocks:
    try:
        print(f"正在获取：{s['name']}...")
        time.sleep(1.5)  # 防限流
        df = ak.stock_zh_a_hist(symbol=s["code"], period="daily", adjust="qfq")
        close_price = df.iloc[-1]["收盘"]  # 取最新收盘价
        data.append({
            "日期": today,
            "股票名称": s["name"],
            "代码": s["code"],
            "收市价": round(close_price, 2)
        })
    except Exception as e:
        print(f"⚠️ {s['name']} 获取失败：{e}")

# -------- 2. 转成飞书文本表格 --------
def df_to_text_table(df):
    lines = [f"📊 每日股票收盘价报表 {today}"]
    lines.append("| 日期 | 股票名称 | 代码 | 收市价 |")
    lines.append("|------|----------|------|--------|")
    for _, row in df.iterrows():
        lines.append(f"| {row['日期']} | {row['股票名称']} | {row['代码']} | {row['收市价']:.2f} |")
    return "\n".join(lines)

# -------- 3. 发送到飞书 --------
if data:
    df_out = pd.DataFrame(data)
    print("✅ 数据获取成功：")
    print(df_out)
    text_table = df_to_text_table(df_out)
    requests.post(FEISHU_WEBHOOK, json={"msg_type": "text", "content": {"text": text_table}})
    print("✅ 已发送到飞书！")
else:
    print("❌ 无数据")