import time
from datetime import datetime

# 方法 A：使用 time 模組（最常用）
current_ts = time.time()
print("方法 A：使用 time 模組（最常用）")
print(f"目前時間戳記 (秒): {current_ts}")          # 輸出如: 1784612340.123
print(f"目前時間戳記 (整數秒): {int(current_ts)}\n")  # 輸出如: 1784612340

# 方法 B：使用 datetime 模組
current_ts_dt = datetime.now().timestamp()
print("方法 B：使用 datetime 模組")
print(f"datetime 取得的時間戳記: {current_ts_dt}\n")

ts = 1784612340  # 範例時間戳記

# 轉換為 datetime 物件
dt_object = datetime.fromtimestamp(ts)

# 格式化為您想要的字串（%Y: 年, %m: 月, %d: 日, %H: 時, %M: 分, %S: 秒）
formatted_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
print("格式化為您想要的字串（%Y: 年, %m: 月, %d: 日, %H: 時, %M: 分, %S: 秒）")
print(f"轉換後的本地時間: {formatted_time}\n")  # 輸出: 2026-07-21 13:39:00

time_str = "2026-07-21 13:39:00"

# 先將字串解析 (strptime) 為 datetime 物件
dt_object = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

# 再轉換 (timestamp) 為秒數
ts = dt_object.timestamp()
print("先將字串解析 (strptime) 為 datetime 物件，再轉換 (timestamp) 為秒數。")
print(f"字串轉回的時間戳記: {int(ts)}\n")  # 輸出: 1784612340

# 乘以 1000 並轉為整數，即為 13 位數時間戳記
ms_timestamp = int(time.time() * 1000)
print("乘以 1000 並轉為整數，即為 13 位數時間戳記")
print(f"13位數毫秒時間戳記: {ms_timestamp}\n")