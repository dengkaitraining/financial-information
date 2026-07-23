# DATABASE: db_stock_news
資料庫名稱：db_stock_news
描述：儲存新聞資料
操作權限：開放「user_stock」、「tb_gnew_init」使用者可「新增」、「修改」、「刪除」表單內的資料。

## 1. TABLE: tb_gnews_data
表單名稱：tb_gnews_data
描述：儲存 gnews 新聞資料
| 欄位名稱 (Field) | 資料類型 (Type) | 主鍵 (PK) | 外鍵 (FK) | 允許空值 (Null) | 預設值 (Default) | 說明 (Comment) |
|---|---|---|---|---|---|---|
| index | BIGINT UNSIGNED | ✅ | ❌ | ❌ | 資料索引 | 流水號主鍵 |
| language | VARCHAR(10) | ❌ | ❌ | ❌ | 無 | 新聞標題 |
| country | VARCHAR(10) | ❌ | ❌ | ❌ | 無 | 國家/地區 |
| period | VARCHAR(10) | ❌ | ❌ | ❌ | 無 | 相對時間範圍（會被具體日期覆蓋） |
| max_results | INT UNSIGNED | ❌ | ❌ | ❌ | 無 | 唯一使用者名稱 (唯一索引) |