USE `tw_stock_analysis`;

-- 建立參數設定表單 (Parameter Settings Table)
CREATE TABLE IF NOT EXISTS `parameter_settings` (
    `id` INT AUTO_INCREMENT COMMENT '主鍵',
    `language` VARCHAR(10) NOT NULL COMMENT '語系地區',
    `country` VARCHAR(10) NOT NULL COMMENT '地區',
    `period` VARCHAR(10) NOT NULL COMMENT '過去區間的新聞',
    `max_results` INT NOT NULL COMMENT '單次抓取量',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT '參數設定表單 (Parameter Settings Table)';

-- 建立新聞資料表單 (News Data Table)
CREATE TABLE IF NOT EXISTS `news_data` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT COMMENT '主鍵',
    `title` TEXT NOT NULL COMMENT '新聞標題',
    `published_date` VARCHAR(100) COMMENT '發布時間',
    `publisher` VARCHAR(100) COMMENT '新聞來源',
    `url` TEXT NOT NULL COMMENT '文章連結',
    `description` TEXT COMMENT '說明摘要',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `unique_url` (`url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT '建立新聞資料表單 (News Data Table)';

-- 將 url 欄位型態更改為 VARCHAR(768) 以支援建立索引，並加上唯一 (UNIQUE) 限制
-- ALTER TABLE news_data MODIFY url VARCHAR(768) NOT NULL COMMENT '文章連結';
-- ALTER TABLE news_data ADD UNIQUE INDEX idx_unique_url (url);

GRANT ALL PRIVILEGES ON `tw_stock_analysis`.* TO 'user_employee'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON `tw_stock_analysis`.* TO 'user_stock'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON `user_stock_db`.* TO 'user_employee'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON `user_stock_db`.* TO 'user_stock'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON `db_employee`.* TO 'user_employee'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON `db_employee`.* TO 'user_stock'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;