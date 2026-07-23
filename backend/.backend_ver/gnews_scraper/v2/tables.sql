-- 表單名稱：tb_wwwnews_data
-- 描述：儲存網路文章爬蟲新聞資料
-- 操作權限：開放「user_stock」、「tb_gnew_init」使用者可「新增」、「修改」、「刪除」表單內的資料。
CREATE TABLE IF NOT EXISTS tb_wwwnews_data (
    index INT AUTO_INCREMENT PRIMARY KEY COMMENT '自動遞增主鍵/資料索引',
    from VARCHAR(500) NOT NULL COMMENT '網路新聞來源',
    title VARCHAR(500) NOT NULL COMMENT '新聞完整標題',
    timestamp DATETIME COMMENT '新聞原始發布時間(已轉為標準時間格式)',
    datetime VARCHAR(50) NOT NULL COMMENT '新聞原始發布時間(自訂時間格式)',
    source VARCHAR(50) NULL COMMENT '新聞來源',
    url VARCHAR(1000) UNIQUE COMMENT '新聞原始連結(唯一值，防止重覆寫入)',
    description TEXT COMMENT '新聞內容簡述或摘要',
    userid VARCHAR(30) COMMENT '抓取人員',
    m_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '抓取時間'
) 
ENGINE=InnoDB 
DEFAULT CHARSET=utf8mb4 
COLLATE=utf8mb4_unicode_ci
COMMENT='網路文章爬蟲資料儲存表';

-- 表單名稱：tb_keywords_data
-- 描述：儲存關鍵字資訊，用於 GNews 抓取新聞的關鍵字
-- 操作權限：開放「user_stock」、「tb_gnew_init」使用者可「新增」、「修改」、「刪除」表單內的資料。
CREATE TABLE IF NOT EXISTS tb_keywords_data (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自動遞增主鍵/資料索引',
    stock_code VARCHAR(20) NULL COMMENT '股票代碼(如: 2330, AAPL)',
    keywords TEXT COMMENT '新聞關鍵字資訊',
    userid VARCHAR(30) COMMENT '抓取人員',
    m_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '抓取時間'
) 
ENGINE=InnoDB 
DEFAULT CHARSET=utf8mb4 
COLLATE=utf8mb4_unicode_ci
COMMENT='儲存關鍵字資訊';