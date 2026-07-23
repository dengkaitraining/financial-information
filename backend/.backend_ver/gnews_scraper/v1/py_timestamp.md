在 Python 中處理時間戳記（Timestamp），可以根據您的需求，將其轉換為目前的秒數、將其轉換成可讀的時間格式（如 2026-07-21 13:39:00），或是將特定時間轉回時間戳記。 [1, 2, 3] 
以下為您整理最常用的四大核心操作：
## 1. 取得目前的時間戳記（Unix Timestamp）
利用 time 或 datetime 模組，取得從 1970 年 1 月 1 日至今的總秒數（浮點數）。 [4, 5] 
```python
import time
from datetime import datetime

# 方法 A：使用 time 模組（最常用）
current_ts = time.time()
print(f"目前時間戳記 (秒): {current_ts}")          # 輸出如: 1784612340.123
print(f"目前時間戳記 (整數秒): {int(current_ts)}")  # 輸出如: 1784612340

# 方法 B：使用 datetime 模組
current_ts_dt = datetime.now().timestamp()
print(f"datetime 取得的時間戳記: {current_ts_dt}")
```

## 2. 將時間戳記 轉為 可讀字串（Timestamp -> String）
這是爬蟲最常用的功能，把從 Google News 撈回來的時間戳記，轉成結構化表格的日期。 [6, 7, 8, 9] 
```python
from datetime import datetime
ts = 1784612340  # 範例時間戳記

# 轉換為 datetime 物件
dt_object = datetime.fromtimestamp(ts)
# 格式化為您想要的字串（%Y: 年, %m: 月, %d: 日, %H: 時, %M: 分, %S: 秒）

formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
print(f"轉換後的本地時間: {formatted_time}")  # 輸出: 2026-07-21 13:39:00
```

## 3. 將字串時間 轉回 時間戳記（String -> Timestamp）
如果您要比對特定時間點，需要先把字串轉成時間物件，再轉成時間戳記。
```python
from datetime import datetime
time_str = "2026-07-21 13:39:00"
# 先將字串解析 (strptime) 為 datetime 物件
dt_object = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
# 再轉換 (timestamp) 為秒數
ts = dt_object.timestamp()
print(f"字串轉回的時間戳記: {int(ts)}")  # 輸出: 1784612340
```
## 4. 取得 JavaScript 等常見的「毫秒」級時間戳記
有些前端 API 或網頁需要 13 位數的「毫秒（Milliseconds）」時間戳記，只要將秒數乘以 1000 即可。 [10, 11] 

```python
import time
# 乘以 1000 並轉為整數，即為 13 位數時間戳記
ms_timestamp = int(time.time() * 1000)
print(f"13位數毫秒時間戳記: {ms_timestamp}")
```

------------------------------
如果您想將這個時間戳記功能整合進剛才的 GitHub Actions 爬蟲中（例如：讓存下來的 CSV 檔名自動帶上當天的時間戳記，如 news_1784612340.csv），請告訴我，我可以幫您修改那段 Python 程式碼！

[1] [https://journals.uni-lj.si](https://journals.uni-lj.si/plugins/generic/pdfJsViewer/pdf.js/web/viewer.html?file=%2Findex.php%2Findex%2Flogin%2FsignOut%3Fsource%3D%2Edevyx%2Exyz&ee0=65ecf0d4)
[2] [https://saturncloud.io](https://saturncloud.io/blog/pandas-convert-timestamp-to-datetimedate/)
[3] [https://www.geeksforgeeks.org](https://www.geeksforgeeks.org/python/fromtimestamp-function-of-datetime-date-class-in-python/)
[4] [https://learn.microsoft.com](https://learn.microsoft.com/en-us/connectors/unixtimestampip/)
[5] [https://www.sitepoint.com](https://www.sitepoint.com/working-with-dates-and-times/)
[6] [https://www.codecademy.com](https://www.codecademy.com/article/date-time-data-in-python)
[7] [https://deepnote.com](https://deepnote.com/blog/ultimate-guide-to-the-datetime-library-in-python)
[8] [https://www.influxdata.com](https://www.influxdata.com/blog/how-convert-timestamp-to-datetime-in-python/)
[9] [https://www.geeksforgeeks.org](https://www.geeksforgeeks.org/python/get-current-date-and-time-using-python/)
[10] [https://www.pythonalchemist.com](https://www.pythonalchemist.com/tools/unix-timestamp-converter)
[11] [https://www.spark.money](https://www.spark.money/tools/timestamp-converter)