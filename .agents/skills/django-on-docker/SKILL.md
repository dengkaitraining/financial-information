---
name: django-on-docker
description: 提供基於 Docker Compose 容器化技術之 Python Django 5.2 LTS、Vue.js 3.5、MariaDB 12.3 (多帳號隔離/多資料庫/實體目錄掛載)、Redis 8.8 (快取與 Celery Broker/Backend)、Apache HTTPD 路由分流反向代理、與 Celery 背景排程之多容器開發環境建立、管理、維護、單元測試與自動化部署指南。
---

# Django on Docker 容器化 Web 資訊系統開發 Skill

## 1. 角色定位 (Role)
您是 **Django on Docker 容器化系統架構與自動化開發專家**。負責設計與維護包含 Apache HTTPD 反向代理伺服器（分流 `/profile` 戰情室與 `/tech-stack` 系統監控）、MariaDB 12.3 多關聯式資料庫（雙資料庫 `user_stock_db` 與 `db_employee`）、Redis 8.8（快取與 Celery 訊息代理）、Celery 背景異步任務執行器與 Celery Beat 定期任務調度器、Django 5.2 LTS (搭載 Django Unfold 美觀後台與單元測試套件) 與 Vue 3.5 (搭載 TypeScript 與 Tailwind CSS v4.3 效能引擎) 之多容器開發環境，確保系統具備高可用性、非同步處理效能、資料庫遷移完整性與跨平台一鍵自動化部署之能力。

### 技術堆疊與服務組件對照表

| 組件名稱 | 技術堆疊與版本 | 服務角色與用途 | 使用時機與存取點 |
| :--- | :--- | :--- | :--- |
| **`init-dir`** | Alpine Linux + Shell | 目錄建立與 Host OS 自動權限修復 | 容器編排優先執行，修復完成即退出 |
| **`web`** | Apache HTTPD 2.4-alpine | 反向代理網頁伺服器，統一 Port 80 進入點，分流路由 | 處理 `/profile/`, `/tech-stack/`, `/`, `/admin/`, `/api/` |
| **`backend`** | Python 3.12 + Django 5.2 LTS | 後端網頁框架、Unfold 美觀後台、REST API 與單元測試 | 提供健康 API、股票更新 API 與單元測試 |
| **`celery-worker`**| Celery 5.6.3 | 背景非同步任務執行器。負責 yfinance / GNews 爬取、翻譯與技術分析落庫。 | 異步執行耗時爬蟲與資料翻譯處理 |
| **`celery-beat`**  | django-celery-beat 2.6.0 | 定期排程調度器。配合 Unfold 設定，每 4 小時自動執行更新任務。 | Unfold 後台圖形化管理與定時觸發 |
| **`backend_ver`** | Python 3.12 + 軟連結與隱藏資料夾 | 後端程式手動測試驗證環境，藉由 `SHOW_BACKEND_VER` 參數控制顯示與隱蔽 | 開發測試環境（`True`）下進入 `fin_django_backend` 執行 `python backend_ver/run_all.py` |
| **`frontend_ver`** | Node/JS + 軟連結與隱藏資料夾 | 前端環境手動測試驗證環境，藉由 `SHOW_FRONTEND_VER` 參數控制顯示與隱蔽 | 開發測試環境（`True`）下進入 `fin_vue_frontend` 執行 `node frontend_ver/run_all.js` |
| **`frontend`** | Vue 3.5 + TS + Tailwind v4.3 | 前端 SPA 開發伺服器 (Vite base: `/tech-stack/`, hmr: `false`) | 造訪 `http://localhost/tech-stack/` 監控或 `http://localhost/profile/` 戰情室 |
| **`db`** | MariaDB 12.3 | 多關聯式 SQL 資料庫 (`user_stock_db`, `db_employee`) | 提供 `user_stock` 與 `user_employee` 多帳號權限管理，掛載 `./db_data` |
| **`redis`** | Redis 8.8 | 快取與 Session 高併發記憶體資料庫 (掛載 `./redis_data`) | 處理 Django 高併發快取、Celery 任務佇列與訊息代理 |

---

## 2. 準則 (Rules)
* **無侵入性路由分流**：將路由解耦（`/profile/` 與 `/tech-stack/`），前端藉由檢測 `window.location.pathname` 動態展示不同 UI 面板，並於 Apache 配置對應代理，避免前端資源路徑衝突。
* **非同步高耗時處理**：凡涉及大批量外部請求（如 GNews RSS、yfinance）的 API 均必須採用 Celery 異步背景執行 + 前端 3 秒定時輪詢之設計，禁止在 HTTP 同步連線中等待，防範 502 Proxy Timeout 錯誤。
* **資料庫遷移版控**：所有新 Model 定義必須完全併入 Django migrations（`makemigrations` 與 `migrate`），禁止使用手動原生 SQL 建表，保障 MariaDB Schema 資料庫版本控制一致性。
* **HMR 相容性與重刷消除**：反向代理下若存在 Base URL 與頁面網址不匹配，需將 `vite.config.ts` 中的 `server.hmr` 設為 `false` 停用熱重載，以杜絕 HMR WebSocket 斷線引起之無限重新整理 (Infinite Page Refresh) 循環。
* **日期與資料清洗**：在爬蟲寫入資料庫前，必須對上市日期、成立日期等字串進行格式清洗（將 `YYYY/MM/DD` 斜線格式自動置換為 `YYYY-MM-DD` 橫線格式），以完全相容 Django DateField。
* **時區完全台灣時間化 (UTC+8)**：
  - 容器系統時區 (TZ) 配置 `Asia/Taipei`，Celery 設定 `CELERY_ENABLE_UTC = False`，新聞發布時間轉為台北時間，前台 views 使用 `timezone.localtime` 輸出。
* **防封鎖休眠間隔規範**：
  - Scraper 內部的每一個網路擷取方法（Profile、Calendar、News）後面必須停留 5 秒延遲。
  - Celery Beat 定期排程更新時，每個個股更新循環末尾必須 sleep 10 秒。
* **落庫狀態完整校驗防止渲染 Race Condition**：
  - 輪詢 API 不得以單純 profile 存在判斷 boolean，必須引入 `profile` 和 `TechnicalAnalysis` 的存在性聯合校驗。
  - 前端輪詢成功後必須主動發起一次純查詢（再次抓取）以解決 TA 資料落庫差造成的圖表無法顯示痛點。
* 準則細部資訊與規範說明，請參閱相對路徑文件：
  [rules_detail.md](./rules/rules_detail.md)

---

## 3. 指定工具 (Tools)
指定工具的詳細資訊與指令範例，已儲存於相對路徑文件：
[tools.md](./scripts/tools.md)

---

## 4. 逐步解說 (Walkthrough)
逐步解說項目的實作細節、系統架構時序圖與運作流程，已儲存於相對路徑文件：
[walkthrough_details.md](./references/walkthrough_details.md)

---

## 5. 完成後的檢查 (Final Inspection)
完成後的檢核項目、單元測試步驟與驗證基準，已儲存於相對路徑文件：
[inspection_checklist.md](./inspections/inspection_checklist.md)

---

## 6. 任務日誌紀錄 (Task Logs)
- [01_implementation_plan.md](./task_logs/01_implementation_plan.md)
- [02_task_list.md](./task_logs/02_task_list.md)
- [03_walkthrough.md](./task_logs/03_walkthrough.md)
