-- 1. 使用 MODIFY COLUMN（不改欄位名稱）
ALTER TABLE `表名` MODIFY COLUMN `欄位名` 新資料型態 [其他屬性/限制] COMMENT '新的欄位批註';
-- 2. 使用 CHANGE COLUMN（可同時更改欄位名稱）
ALTER TABLE `表名` 
CHANGE COLUMN `舊欄位名` `新欄位名` 新資料型態 [其他屬性/限制] COMMENT '新的欄位批註';



-- 
-- 1. 暫時關閉外鍵檢查（預防萬一）
SET FOREIGN_KEY_CHECKS = 0;

-- 2. 刪除該欄位的外鍵約束（請將 fk_company_news_url 替換為步驟 1 查到的名稱）
ALTER TABLE `company_news` DROP UNIQUE INDEX `company_news_stock_id_url_664f1c37_uniq`;
ALTER TABLE `company_news` DROP FOREIGN KEY `company_news_stock_id_f883d1ed_fk_company_profile_stock_id`;

-- 3. 執行你原本的修改指令
ALTER TABLE `company_news` MODIFY COLUMN `url` TEXT NOT NULL COLLATE 'utf8mb4_unicode_ci' COMMENT '新聞網址';

-- 4. 重新建立外鍵約束（注意：如果改成了 TEXT，這步可能會因為資料庫不支援而失敗。若是此
ALTER TABLE `company_news` ADD UNIQUE INDEX `company_news_stock_id_url_664f1c37_uniq` (`stock_id`, `url`) USING BTREE;
ALTER TABLE `company_news` ADD CONSTRAINT `company_news_stock_id_f883d1ed_fk_company_profile_stock_id` FOREIGN KEY (`stock_id`) REFERENCES `company_profile` (`stock_id`) ON UPDATE RESTRICT ON DELETE RESTRICT;

-- 5. 重新開啟外鍵檢查
SET FOREIGN_KEY_CHECKS = 1;