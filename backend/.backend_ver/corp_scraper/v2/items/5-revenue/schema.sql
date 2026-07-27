CREATE DATABASE IF NOT EXISTS stock_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE stock_db;

-- 1. 月營收 (Monthly Revenue)
CREATE TABLE IF NOT EXISTS monthly_revenue (
    stock_id VARCHAR(20) NOT NULL,
    period_date DATE NOT NULL,
    current_revenue BIGINT COMMENT '當月營收(仟元)',
    mom_percent FLOAT COMMENT '月增率%',
    last_year_revenue BIGINT COMMENT '去年同月營收(仟元)',
    yoy_percent FLOAT COMMENT '年增率%',
    acc_revenue BIGINT COMMENT '當月累計營收(仟元)',
    last_year_acc_revenue BIGINT COMMENT '去年累計營收(仟元)',
    acc_yoy_percent FLOAT COMMENT '累計年增率%',
    PRIMARY KEY (stock_id, period_date)
);

-- 2. 單季每股盈餘 (Quarterly EPS)
CREATE TABLE IF NOT EXISTS quarterly_eps (
    stock_id VARCHAR(20) NOT NULL,
    period_date DATE NOT NULL,
    eps FLOAT COMMENT '每股盈餘',
    qoq_percent FLOAT COMMENT '季增率%',
    yoy_percent FLOAT COMMENT '年增率%',
    quarter_avg_price FLOAT COMMENT '季均價',
    PRIMARY KEY (stock_id, period_date)
);

-- 3. 損益表 (Income Statement)
CREATE TABLE IF NOT EXISTS income_statement (
    stock_id VARCHAR(20) NOT NULL,
    period_date DATE NOT NULL,
    revenue BIGINT COMMENT '營業收入',
    gross_profit BIGINT COMMENT '營業毛利',
    operating_expense BIGINT COMMENT '營業費用',
    operating_income BIGINT COMMENT '營業利益',
    net_income BIGINT COMMENT '稅後淨利',
    PRIMARY KEY (stock_id, period_date)
);

-- 4. 資產負債表 (Balance Sheet)
CREATE TABLE IF NOT EXISTS balance_sheet (
    stock_id VARCHAR(20) NOT NULL,
    period_date DATE NOT NULL,
    total_assets BIGINT COMMENT '總資產',
    total_liabilities BIGINT COMMENT '總負債',
    stockholders_equity BIGINT COMMENT '股東權益（淨值）',
    current_assets BIGINT COMMENT '流動資產',
    current_liabilities BIGINT COMMENT '流動負債',
    PRIMARY KEY (stock_id, period_date)
);

-- 5. 現金流量表 (Cash Flow)
CREATE TABLE IF NOT EXISTS cash_flow (
    stock_id VARCHAR(20) NOT NULL,
    period_date DATE NOT NULL,
    operating_cf BIGINT COMMENT '營業現金流',
    investing_cf BIGINT COMMENT '投資現金流',
    financing_cf BIGINT COMMENT '融資現金流',
    free_cf BIGINT COMMENT '自由現金流',
    net_cf BIGINT COMMENT '淨現金流',
    PRIMARY KEY (stock_id, period_date)
);

-- 4. 使用者權限設定
GRANT ALL PRIVILEGES ON `stock_db`.* TO 'user_employee'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON `stock_db`.* TO 'user_stock'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;