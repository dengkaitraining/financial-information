-- ==============================================================================
-- MariaDB 多資料庫與多使用者權限初始化腳本 (db_conf/init_multi_db.sql)
-- 說明：自動建立 user_stock_db 與 db_employee 資料庫，配置 user_stock 與 user_employee 讀寫權限
-- ==============================================================================

-- 1. 建立資料庫
CREATE DATABASE IF NOT EXISTS `user_stock_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS `db_employee` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS `tw_stock_analysis` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. 建立 user_employee 帳號並授權存取 db_employee
CREATE USER IF NOT EXISTS 'user_employee'@'%' IDENTIFIED BY 'user_employee_pass';
GRANT ALL PRIVILEGES ON `db_employee`.* TO 'user_employee'@'%';

-- 3. 建立 user_stock 帳號並授權存取 user_stock_db
CREATE USER IF NOT EXISTS 'user_stock'@'%' IDENTIFIED BY 'user_stock_pass';
GRANT ALL PRIVILEGES ON `user_stock_db`.* TO 'user_stock'@'%';

-- 4. 授權 user_stock 帳號亦可讀寫 db_employee 資料庫與測試資料庫 (test_%)
GRANT ALL PRIVILEGES ON `db_employee`.* TO 'user_stock'@'%';

-- 5. 授權 user_stock 與 user_employee 帳號亦可讀寫 tw_stock_analysis 資料庫
GRANT ALL PRIVILEGES ON `tw_stock_analysis`.* TO 'user_employee'@'%';
GRANT ALL PRIVILEGES ON `tw_stock_analysis`.* TO 'user_stock'@'%';

-- 6. 重新整理權限表
FLUSH PRIVILEGES;
