import time
import requests

INPUT_FILE = "stock.txt"
OUTPUT_CLEAN = "stockclean_all.txt"
OUTPUT_DELIST = "delisted_60.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def is_stock_active(code):
    # 只查60開頭滬股
    url = f"https://www.eastmoney.com/s?keyword={code}"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=6)
        html = resp.text
        # 退市/無結果關鍵字
        if "退市" in html or "退" in html or "0条" in html or "找不到" in html:
            return False
        return True
    except:
        # 查詢超時當作異常，先標記保留
        return True

def main():
    print("開始批量檢查 60 開頭股票，請稍候...\n")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    clean_list = []
    delist_list = []
    total = 0
    keep_cnt = 0
    delist_cnt = 0

    for line in lines:
        parts = line.split(",")
        if len(parts) < 1:
            clean_list.append(line)
            continue

        code = parts[0].strip()
        total += 1

        # 非60開頭直接保留
        if not code.startswith("60"):
            clean_list.append(line)
            print(f"⏭️  跳過非60開頭：{line}")
            continue

        # 60開頭進行網頁檢查
        active = is_stock_active(code)
        time.sleep(0.25)  # 節流防封

        if active:
            clean_list.append(line)
            keep_cnt += 1
            print(f"✅ 正常保留：{line}")
        else:
            delist_list.append(line)
            delist_cnt += 1
            print(f"❌ 已退市剔除：{line}")

    # 寫入乾淨完整列表
    with open(OUTPUT_CLEAN, "w", encoding="utf-8") as f:
        f.write("\n".join(clean_list))

    # 寫入退市清單
    with open(OUTPUT_DELIST, "w", encoding="utf-8") as f:
        f.write("\n".join(delist_list))

    print("\n==================== 清理完成 ====================")
    print(f"總行數：{total}")
    print(f"60開頭正常保留：{keep_cnt}")
    print(f"60開頭已退市剔除：{delist_cnt}")
    print(f"乾淨完整檔：{OUTPUT_CLEAN}")
    print(f"退市名單檔：{OUTPUT_DELIST}")

if __name__ == "__main__":
    main()