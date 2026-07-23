# 1. 完成將<code>以 python 物件導向的規範改寫，封裝為 class。
# 2. 產生呼叫 class 測試的 CLI 輸入界面，詳細功能<spec>。
<spec>
 1. 提供抓取過去時間(period)的輸入功能，提示輸入方式。
 2. 提供可輸入數個關鍵字(keywords)的功能，至多 4 個關鍵字。
 3. 輸出結果使用 csv 格式儲存在 news 資料夾，檔名以 timestamp 區隔命名。
 4. 使用 console 方式顯示作業過程， 輸出結果使用 txt 格式儲存在 logs 資料夾，檔名以 timestamp 區隔命名。
 5. class 與 cli 分開編寫，並顯示專案架構。
</spec>

<code>
import os
from gnews import GNews
import pandas as pd
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

# 1. 初始化 GNews 設定（設定台灣地區、中文、過去 1 小時的新聞）
google_news = GNews(language='zh-TW', country='TW', period='4h', max_results=100)

# 2. 設定您想追蹤的關鍵字
# 另一種單次呼叫的寫法：字串拼接 OR 語法
combined_keywords = "人工智慧 OR RAG 檢索增強 OR 大型語言模型 OR LLM"

keywords = ["人工智慧", "RAG 檢索增強", "大型語言模型", "LLM"]
combined_keywords = " OR ".join(keywords)
print(f"開始抓取關鍵字：{combined_keywords} 的最新新聞...")

# 3. 撈取新聞
#news_results = google_news.get_news(keyword)
news_results = google_news.get_news(combined_keywords)

# 4. 解析並整理資料
news_list = []
f_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# enumerate() 會在每次迴圈時，同時丟出 index（數字）和 item（內容）。
# 輸出：
# 目前是第 0 筆新聞，標題是：新聞A
# 目前是第 1 筆新聞，標題是：新聞B
# 目前是第 2 筆新聞，標題是：新聞C
for index, item in enumerate(news_results):
    """
    news_list.append({
        "抓取時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "新聞標題": item.get('title'),
        "時間戳記": (datetime.strptime(item.get('published date'), "%a, %d %b %Y %H:%M:%S GMT")).timestamp(),
        "發布時間": item.get('published date'),
        "新聞來源": item.get('publisher', {}).get('title'),
        "文章連結": item.get('url'),
        "說明摘要": item.get('description')
    })
    """
    
    new_item = {}
    n_time_utc = 0
    n_time = 0

    # 1. 移除非標準的 ' GMT' 標籤，並將字串解析為 UTC 時間物件
    n_time_utc = (datetime.strptime(item.get('published date'), "%a, %d %b %Y %H:%M:%S GMT")).replace(tzinfo=timezone.utc)

    # 2. 直接指定轉換為 'Asia/Taipei' 台北時區
    n_time = (n_time_utc.astimezone(ZoneInfo("Asia/Taipei"))).timestamp()

    # [ ] 資料欄位：資料索引
    new_item["index"] = int(n_time*1000)

    # [ ] 資料欄位：新聞標題
    new_item["title"] = str(item.get('title'))

    # [ ] 資料欄位：時間戳記
    new_item["timestamp"] = int(n_time)

    # [ ] 資料欄位：發布時間
    new_item["datetime"] = str(datetime.fromtimestamp(n_time).strftime("%Y-%m-%d %H:%M:%S, %a"))
    
    # [ ] 資料欄位：新聞來源
    new_item["source"] = str(item.get('publisher', {}).get('title'))
    
    # [ ] 資料欄位：文章連結
    new_item["url"] = str(item.get('url'))
    
    # [ ] 資料欄位：說明摘要
    new_item["description"] = str(item.get('description'))
    
    # [ ] 資料欄位：抓取人員"
    new_item["userid"] = str("sys")
    
    # [ ] 資料欄位：抓取時間
    new_item["m_date"] = str(f_time)
    news_list.append(new_item)

# 根據時間戳記「最新到最舊（降冪）」排序
# lambda x: x['時間戳記'] 代表指定用 時間戳記 欄位來比大小
news_list.sort(key=lambda x: x['timestamp'], reverse=False)

# 5. 儲存資料（若 CSV 已存在則附加，不存在則建立新檔）
dt_obj = datetime.fromtimestamp(time.time())
#curr_timestamp = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
curr_timestamp = dt_obj.strftime("%Y-%m-%d-%H-%M-%S")
ms_timestamp = int(time.time() * 1000)

dir_path = (Path(__file__).parent) / "news"

# 檢查是否存在且為資料夾
if dir_path.is_dir():
    print("資料夾存在！")
else:
    # 建立多層資料夾
    os.makedirs(dir_path, exist_ok = True)
    print("資料夾不存在，已自動建立。")

csv_filename = Path(str(dir_path / f"google_news_data_{ms_timestamp}.csv"))
df_new = pd.DataFrame(news_list)

if not df_new.empty:
    if os.path.exists(csv_filename):
        df_existing = pd.read_csv(csv_filename)
        df_combined = pd.concat([df_existing, df_new]).drop_duplicates(subset=['文章連結'])
        df_combined.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    else:
        df_new.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    print(f"成功更新！新增了 {len(df_new)} 筆新聞。")
else:
    print("過去 1 小時內沒有新新聞。")
</code> 


