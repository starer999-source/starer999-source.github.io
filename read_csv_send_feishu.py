import pandas as pd
import requests

# ===================== 配置区（你改这里就得）=====================
# 1. CSV 文件路径
CSV_FILE = "a股实时行情.csv"

# 2. 你要的4只股票（带前缀完整代码，同CSV里的）
target_codes = [
    "sh600000",   # 浦发银行
    "sh601328",   # 
    "sh601818",   #
    "sz300568"    # 
]

# 3. 飞书机器人 Webhook
# -------- 你的飞书机器人Webhook --------
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/f252038d-9a55-4d93-9fb9-432340e552c0"

def main():
    # 1 读取CSV
    df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")

    # 2 筛选指定股票
    df_target = df[df["代码"].isin(target_codes)][["代码", "名称", "最新价"]]

    # 3 构造飞书表格文字
    lines = ["📊 自选股票实时行情"]
    lines.append("| 代码 | 名称 | 最新价 |")
    lines.append("|------|------|--------|")

    for idx, row in df_target.iterrows():
        lines.append(f"| {row['代码']} | {row['名称']} | {row['最新价']} |")

    content_text = "\n".join(lines)
    print(content_text)

    # 4 发送到飞书
    res = requests.post(
        FEISHU_WEBHOOK,
        json={
            "msg_type": "text",
            "content": {"text": content_text}
        }
    )
    print("飞书发送结果：", res.json())

if __name__ == "__main__":
    main()