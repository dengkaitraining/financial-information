-- 建立資料庫
CREATE DATABASE IF NOT EXISTS stock_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE stock_db;

-- 建立技術分析資料表
CREATE TABLE IF NOT EXISTS technical_analysis (
    stock_id VARCHAR(20) NOT NULL COMMENT '股票代號',
    trade_date DATE NOT NULL COMMENT '交易日期',
    
    -- 基本價量
    volume BIGINT COMMENT '成交量',
    open_price DECIMAL(20, 2) COMMENT '開盤價',
    high_price DECIMAL(20, 2) COMMENT '最高價',
    low_price DECIMAL(20, 2) COMMENT '最低價',
    close_price DECIMAL(20, 2) COMMENT '收盤價',
    
    -- KD, J 指標
    k_value DECIMAL(20, 4) COMMENT 'K值',
    d_value DECIMAL(20, 4) COMMENT 'D值',
    j_value DECIMAL(20, 4) COMMENT 'J值',
    
    -- MACD 指標
    macd DECIMAL(20, 4) COMMENT 'MACD',
    macd_signal DECIMAL(20, 4) COMMENT 'MACD Signal',
    
    -- 乖離與威廉指標
    bias DECIMAL(20, 4) COMMENT '乖離率(6日)',
    williams_r DECIMAL(10, 4) COMMENT '威廉指標(14日)',
    bbi DECIMAL(20, 4) COMMENT '多空指標(BBI)',
    
    -- CDP 逆勢操作系統
    cdp DECIMAL(20, 2) COMMENT 'CDP',
    ah DECIMAL(20, 2) COMMENT '最高值(AH)',
    nh DECIMAL(20, 2) COMMENT '近高值(NH)',
    nl DECIMAL(20, 2) COMMENT '近低值(NL)',
    al DECIMAL(20, 2) COMMENT '最低值(AL)',
    
    -- DMI 動向指標
    pdi DECIMAL(20, 4) COMMENT '+DI',
    mdi DECIMAL(20, 4) COMMENT '-DI',
    adx DECIMAL(20, 4) COMMENT 'ADX',
    
    PRIMARY KEY (stock_id, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='個股技術分析資料表';

-- 4. 使用者權限設定
GRANT ALL PRIVILEGES ON `stock_db`.* TO 'user_employee'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON `stock_db`.* TO 'user_stock'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;