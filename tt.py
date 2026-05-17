import pandas as pd
from datetime import datetime, timedelta
import requests
import akshare as ak
import time
from requests.exceptions import RequestException

# -------- 你的飞书机器人Webhook --------
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/f252038d-9a55-4d93-9fb9-432340e552c0"

# -------- 配置 --------
stocks = [
    {"name": "广发证券", "code": "000776"},
    {"name": "浦发银行", "code": "600000"},
    {"name": "农业银行", "code": "601288"}
]

# 重试次数配置
MAX_RETRY = 3
RETRY_DELAY = 5  # 重试间隔（秒）
REQUEST_DELAY = 5  # 接口请求间隔（防限流）

# -------- 工具函数 --------
def get_latest_trading_day():
    """获取最新的交易日（解决非交易日无数据问题）"""
    today = datetime.now()
    # 先尝试今天，如果不是交易日则往前推
    for i in range(7):  # 最多往前推7天
        check_date = today - timedelta(days=i)
        check_date_str = check_date.strftime("%Y-%m-%d")
        # 用上证指数判断是否为交易日
        try:
            df = ak.stock_zh_a_hist(symbol="000001", period="daily", adjust="qfq", end_date=check_date_str)
            if not df.empty and check_date_str in df["日期"].values:
                return check_date_str
        except:
            continue
    return today.strftime("%Y-%m-%d")

def get_stock_close_price(stock_code, retry=MAX_RETRY):
    """获取股票收盘价（带重试机制）"""
    for attempt in range(retry):
        try:
            time.sleep(REQUEST_DELAY)  # 防限流
            # 获取历史数据
            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                period="daily",
                adjust="qfq"
            )
            
            # 检查数据是否为空
            if df.empty:
                raise Exception("接口返回空数据")
            
            # 确保日期列存在并排序
            if "日期" not in df.columns:
                raise Exception("数据缺少日期列")
            
            # 按日期排序，取最新的一条
            df = df.sort_values("日期", ascending=False)
            latest_row = df.iloc[0]
            close_price = latest_row["收盘"] if "收盘" in latest_row else latest_row.get("收盘价")
            
            return {
                "交易日期": latest_row["日期"],
                "收盘价": round(float(close_price), 2)
            }
        
        except RequestException as e:
            if attempt < MAX_RETRY - 1:
                print(f"网络请求失败（第{attempt+1}次重试）：{e}")
                time.sleep(RETRY_DELAY)
                continue
            else:
                raise Exception(f"网络请求失败（已重试{MAX_RETRY}次）：{e}")
        except Exception as e:
            if attempt < MAX_RETRY - 1:
                print(f"获取数据失败（第{attempt+1}次重试）：{e}")
                time.sleep(RETRY_DELAY)
                continue
            else:
                raise Exception(f"获取数据失败（已重试{MAX_RETRY}次）：{e}")

def df_to_text_table(df):
    """转成飞书文本表格"""
    latest_date = df["交易日期"].iloc[0] if not df.empty else datetime.now().strftime("%Y-%m-%d")
    lines = [f"📊 每日股票收盘价报表 {latest_date}"]
    lines.append("| 交易日期 | 股票名称 | 代码 | 收市价 |")
    lines.append("|----------|----------|------|--------|")
    for _, row in df.iterrows():
        lines.append(f"| {row['交易日期']} | {row['股票名称']} | {row['代码']} | {row['收市价']:.2f} |")
    return "\n".join(lines)

def send_to_feishu(text):
    """发送消息到飞书"""
    try:
        response = requests.post(
            FEISHU_WEBHOOK,
            json={"msg_type": "text", "content": {"text": text}},
            timeout=10
        )
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ 发送飞书失败：{e}")
        return False

# -------- 主逻辑 --------
if __name__ == "__main__":
    data = []
    today = get_latest_trading_day()
    print(f"📅 当前获取的最新交易日：{today}")

    for s in stocks:
        stock_name = s["name"]
        stock_code = s["code"]
        print(f"\n正在获取：{stock_name}（{stock_code}）...")
        
        try:
            # 获取收盘价
            price_info = get_stock_close_price(stock_code)
            data.append({
                "交易日期": price_info["交易日期"],
                "股票名称": stock_name,
                "代码": stock_code,
                "收市价": price_info["收盘价"]
            })
            print(f"✅ {stock_name} 获取成功：{price_info['收盘价']}元")
        
        except Exception as e:
            print(f"⚠️ {stock_name} 获取失败：{e}")
            continue

    # 处理结果
    if data:
        df_out = pd.DataFrame(data)
        print("\n✅ 数据获取成功：")
        print(df_out)
        
        # 转换为表格并发送飞书
        text_table = df_to_text_table(df_out)
        if send_to_feishu(text_table):
            print("✅ 已发送到飞书！")
    else:
        print("\n❌ 无有效数据")
        # 发送失败通知到飞书
        send_to_feishu(f"❌ {today} 股票数据获取失败，无有效数据")