import akshare as ak
import pandas as pd  # 保存 CSV 需要用到 pandas

# 获取数据
stock_zh_a_spot_df = ak.stock_zh_a_spot()

# 保存为 CSV 文件
stock_zh_a_spot_df.to_csv(
    "a股实时行情.csv",  # 保存的文件名
    index=False,         # 不保存行号
    encoding="utf-8-sig" # 防止中文乱码，Excel 打开也正常
)

print("✅ 数据已保存到 a股实时行情.csv")

