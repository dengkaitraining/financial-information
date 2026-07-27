CREATE DATABASE IF NOT EXISTS stock_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE stock_db;

-- 1. 法人逐日買賣超 & 資券餘額
CREATE TABLE IF NOT EXISTS daily_trading_margin (
    stock_id VARCHAR(20) NOT NULL COMMENT '股票代號',
    trade_date DATE NOT NULL COMMENT '交易日期',
    foreign_investor_vol INT DEFAULT 0 COMMENT '外資(張)',
    investment_trust_vol INT DEFAULT 0 COMMENT '投信(張)',
    dealer_vol INT DEFAULT 0 COMMENT '自營商(張)',
    total_institutional_vol INT DEFAULT 0 COMMENT '合計(張)',
    foreign_ratio DECIMAL(10,2) DEFAULT 0.0 COMMENT '外資籌碼(%)',
    price_change_ratio DECIMAL(10,2) DEFAULT 0.0 COMMENT '漲跌幅(%)',
    trading_volume INT DEFAULT 0 COMMENT '成交量',
    margin_balance INT DEFAULT 0 COMMENT '融資餘額',
    short_sale_balance INT DEFAULT 0 COMMENT '融券餘額',
    securities_lending_balance INT DEFAULT 0 COMMENT '借券賣出餘額',
    PRIMARY KEY (stock_id, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. 主力進出 (依券商分點)
CREATE TABLE IF NOT EXISTS major_players_trades (
    stock_id VARCHAR(20) NOT NULL COMMENT '股票代號',
    trade_date DATE NOT NULL COMMENT '交易日期',
    broker_name VARCHAR(50) NOT NULL COMMENT '券商名稱',
    trade_type ENUM('BUY', 'SELL') NOT NULL COMMENT '買超(BUY)/賣超(SELL)',
    buy_vol INT DEFAULT 0 COMMENT '買進',
    sell_vol INT DEFAULT 0 COMMENT '賣出',
    net_vol INT DEFAULT 0 COMMENT '買超/賣超張數',
    PRIMARY KEY (stock_id, trade_date, broker_name, trade_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 大戶籌碼與董監持股
CREATE TABLE IF NOT EXISTS large_shareholders (
    stock_id VARCHAR(20) NOT NULL COMMENT '股票代號',
    record_date DATE NOT NULL COMMENT '年度/日期',
    foreign_ratio DECIMAL(10,2) DEFAULT 0.0 COMMENT '外資籌碼(%)',
    large_holder_ratio DECIMAL(10,2) DEFAULT 0.0 COMMENT '大戶籌碼(%)',
    director_supervisor_ratio DECIMAL(10,2) DEFAULT 0.0 COMMENT '董監持股(%)',
    stock_price DECIMAL(20,2) DEFAULT 0.0 COMMENT '股價',
    PRIMARY KEY (stock_id, record_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. YFinance 國際法人機構籌碼
CREATE TABLE IF NOT EXISTS yfinance_institutional (
    stock_id VARCHAR(20) NOT NULL COMMENT '股票代號',
    holder_name_en VARCHAR(150) NOT NULL COMMENT '持有機構(英文)',
    holder_name_zh VARCHAR(150) NOT NULL COMMENT '持有機構(中文翻譯)',
    shares BIGINT DEFAULT 0 COMMENT '持有股數',
    date_reported DATE NOT NULL COMMENT '報告日期',
    out_ratio DECIMAL(10,4) DEFAULT 0.0 COMMENT '流通在外比例',
    value BIGINT DEFAULT 0 COMMENT '總價值',
    PRIMARY KEY (stock_id, holder_name_en, date_reported)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. 使用者權限設定
GRANT ALL PRIVILEGES ON `stock_db`.* TO 'user_employee'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON `stock_db`.* TO 'user_stock'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;