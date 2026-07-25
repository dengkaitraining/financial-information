-- MariaDB 12.3 DDL Script for Taiwan Stock Analysis System
CREATE DATABASE IF NOT EXISTS `tw_stock_analysis` 
  DEFAULT CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

USE `tw_stock_analysis`;

-- 1. 公司基本面 (Company Profile)
CREATE TABLE IF NOT EXISTS `company_profile` (
    `stock_id` VARCHAR(10) NOT NULL COMMENT '股票代號',
    `company_name` VARCHAR(100) NOT NULL COMMENT '公司名稱',
    `industry_category` VARCHAR(50) DEFAULT NULL COMMENT '產業類別',
    `capital` BIGINT DEFAULT NULL COMMENT '實收資本額(元)',
    `listing_date` DATE DEFAULT NULL COMMENT '上市/上櫃日期',
    `establishment_date` DATE DEFAULT NULL COMMENT '成立日期',
    `description` TEXT DEFAULT NULL COMMENT '公司業務簡介',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`stock_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='公司基本面資料表';

-- 2. 經營營運面 (Monthly Revenue & Growth)
CREATE TABLE IF NOT EXISTS `monthly_revenue` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主鍵',
    `stock_id` VARCHAR(10) NOT NULL COMMENT '股票代號',
    `revenue_year` INT NOT NULL COMMENT '營收年份',
    `revenue_month` INT NOT NULL COMMENT '營收月份',
    `revenue` BIGINT NOT NULL COMMENT '當月營收(元)',
    `mom_growth` DECIMAL(8,4) DEFAULT NULL COMMENT '月增率 (MoM %)',
    `yoy_growth` DECIMAL(8,4) DEFAULT NULL COMMENT '年增率 (YoY %)',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_stock_period` (`stock_id`, `revenue_year`, `revenue_month`),
    CONSTRAINT `fk_revenue_stock` FOREIGN KEY (`stock_id`) REFERENCES `company_profile` (`stock_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='經營營運面資料表';

-- 3. 財務獲利面 (Financial Metrics)
CREATE TABLE IF NOT EXISTS `financial_metrics` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主鍵',
    `stock_id` VARCHAR(10) NOT NULL COMMENT '股票代號',
    `year` INT NOT NULL COMMENT '年份',
    `quarter` INT NOT NULL COMMENT '季度 (1-4)',
    `eps` DECIMAL(8,2) DEFAULT NULL COMMENT '每股盈餘 (EPS)',
    `gross_margin` DECIMAL(8,4) DEFAULT NULL COMMENT '毛利率 (%)',
    `operating_margin` DECIMAL(8,4) DEFAULT NULL COMMENT '營業利益率 (%)',
    `debt_ratio` DECIMAL(8,4) DEFAULT NULL COMMENT '負債比率 (%)',
    `roe` DECIMAL(8,4) DEFAULT NULL COMMENT '股東權益報酬率 (ROE %)',
    `roa` DECIMAL(8,4) DEFAULT NULL COMMENT '資產報酬率 (ROA %)',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_stock_quarter` (`stock_id`, `year`, `quarter`),
    CONSTRAINT `fk_financial_stock` FOREIGN KEY (`stock_id`) REFERENCES `company_profile` (`stock_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='財務獲利面資料表';

-- 4. 估值與籌碼面 (Valuation & Chip)
CREATE TABLE IF NOT EXISTS `valuation_chip` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主鍵',
    `stock_id` VARCHAR(10) NOT NULL COMMENT '股票代號',
    `trade_date` DATE NOT NULL COMMENT '交易日期',
    `pe_ratio` DECIMAL(8,2) DEFAULT NULL COMMENT '本益比 (P/E)',
    `pb_ratio` DECIMAL(8,2) DEFAULT NULL COMMENT '股價淨值比 (P/B)',
    `yield_rate` DECIMAL(8,4) DEFAULT NULL COMMENT '殖利率 (%)',
    `foreign_buy` BIGINT DEFAULT 0 COMMENT '外資買賣超張數/股數',
    `investment_trust_buy` BIGINT DEFAULT 0 COMMENT '投信買賣超張數/股數',
    `dealer_buy` BIGINT DEFAULT 0 COMMENT '自營商買賣超張數/股數',
    `institutional_total_buy` BIGINT DEFAULT 0 COMMENT '三大法人合計買賣超',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_stock_date` (`stock_id`, `trade_date`),
    CONSTRAINT `fk_chip_stock` FOREIGN KEY (`stock_id`) REFERENCES `company_profile` (`stock_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='估值與籌碼面資料表';


GRANT ALL PRIVILEGES ON `tw_stock_analysis`.* TO 'user_employee'@'%';
GRANT ALL PRIVILEGES ON `tw_stock_analysis`.* TO 'user_stock'@'%';

FLUSH PRIVILEGES;