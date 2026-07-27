-- MariaDB 12.3 Database Schema Script
-- Database: stock_db

CREATE DATABASE IF NOT EXISTS stock_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE stock_db;

-- 1. 公司基本資料表 (company_profile)
CREATE TABLE IF NOT EXISTS company_profile (
    stock_id VARCHAR(20) NOT NULL COMMENT '股票代碼',
    tax_id VARCHAR(20) DEFAULT NULL COMMENT '統一編號',
    company_name VARCHAR(100) NOT NULL COMMENT '公司名稱',
    spokesperson VARCHAR(50) DEFAULT NULL COMMENT '發言人',
    eng_short_name VARCHAR(100) DEFAULT NULL COMMENT '英文簡稱',
    deputy_spokesperson VARCHAR(50) DEFAULT NULL COMMENT '代理發言人',
    establishment_date DATE DEFAULT NULL COMMENT '成立時間',
    phone VARCHAR(30) DEFAULT NULL COMMENT '總機電話',
    listing_date DATE DEFAULT NULL COMMENT '掛牌日期',
    fax VARCHAR(30) DEFAULT NULL COMMENT '傳真號碼',
    industry_category VARCHAR(50) DEFAULT NULL COMMENT '產業類別',
    website VARCHAR(255) DEFAULT NULL COMMENT '公司網站',
    chairman VARCHAR(50) DEFAULT NULL COMMENT '董事長',
    email VARCHAR(100) DEFAULT NULL COMMENT '電子郵件',
    general_manager VARCHAR(50) DEFAULT NULL COMMENT '總經理',
    stock_transfer_agent VARCHAR(100) DEFAULT NULL COMMENT '股務代理',
    capital DECIMAL(20, 2) DEFAULT NULL COMMENT '股本(元)',
    auditor VARCHAR(100) DEFAULT NULL COMMENT '簽證會計師',
    issued_shares BIGINT DEFAULT NULL COMMENT '已發行普通股數',
    address VARCHAR(255) DEFAULT NULL COMMENT '公司地址',
    market_cap_millions DECIMAL(20, 2) DEFAULT NULL COMMENT '市值(百萬)',
    market_type VARCHAR(20) DEFAULT NULL COMMENT '市場別(上市/上櫃/興櫃)',
    insider_holding_ratio DECIMAL(5, 2) DEFAULT NULL COMMENT '董監持股比例(%)',
    group_name VARCHAR(100) DEFAULT NULL COMMENT '所屬集團',
    main_business TEXT DEFAULT NULL COMMENT '主要經營業務',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (stock_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='公司基本資料表';

-- 2. 公司行事曆資料表 (company_calendar)
CREATE TABLE IF NOT EXISTS company_calendar (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    stock_id VARCHAR(20) NOT NULL COMMENT '股票代碼',
    event_type VARCHAR(50) NOT NULL COMMENT '事件類型(股東常會/配股發放日/現金股利發放日)',
    event_date DATE NOT NULL COMMENT '事件日期',
    description TEXT DEFAULT NULL COMMENT '補充說明',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uk_stock_id_event UNIQUE (stock_id, event_type, event_date),
    FOREIGN KEY (stock_id) REFERENCES company_profile(stock_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='公司行事曆資料表';

-- 3. 公司新聞與個股公告資料表 (company_news)
CREATE TABLE IF NOT EXISTS company_news (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    stock_id VARCHAR(20) NOT NULL COMMENT '股票代碼',
    news_type VARCHAR(100) NOT NULL COMMENT '類型(NEWS:新聞 / ANNOUNCEMENT:個股公告)',
    title TEXT NOT NULL COMMENT '新聞/公告標題',
    url TEXT NOT NULL COMMENT '新聞連結 URL',
    publisher VARCHAR(500) DEFAULT NULL COMMENT '發布來源',
    published_date DATETIME DEFAULT NULL COMMENT '發布時間',
    summary LONGTEXT DEFAULT NULL COMMENT '內文摘要',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uk_stock_id_url UNIQUE (stock_id, url),
    FOREIGN KEY (stock_id) REFERENCES company_profile(stock_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='公司新聞與個股公告表';


-- 4. 使用者權限設定
GRANT ALL PRIVILEGES ON `stock_db`.* TO 'user_employee'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON `stock_db`.* TO 'user_stock'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;