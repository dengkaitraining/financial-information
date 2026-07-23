# Django on Docker 逐步解說細部資訊 (Walkthrough Reference)

本參考文件詳細記載 **Python Django 5.2 + Vue 3.5 + Apache HTTPD + MariaDB 12.3 (多庫多帳號) + Redis 8.8** 容器化系統架構與各元件之協作細節。

---

## 1. 系統服務架構與轉接對照表

| 服務模組 | 容器名稱 (Container) | 監聽 Port | 反向代理對應路徑 | 服務職責與處理內容 |
| :--- | :--- | :--- | :--- | :--- |
| **Apache HTTPD** | `apache_web` | `80:80` | `/tech-stack/`, `/`, `/admin/`, `/admin/db-manager/`, `/api/` | 統一反向代理進入點、載入自定義設定檔 `httpd-custom.conf` |
| **Vue.js 3.5** | `vue_frontend` | `5173` | `/tech-stack/` 及 `/_hmr` | 提供系統儀表板 (Vite `base: /tech-stack/`)，含 10 分鐘自動連線檢測 |
| **Django 5.2** | `django_backend` | `8000` | `/`, `/admin/`, `/admin/db-manager/`, `/api/status/` | 提供純文字、Unfold、DataTables 管理員與 `employees` 表單管理 |
| **MariaDB 12.3** | `django_db` | `3306:3306` | 由 Backend 內部連線 (`db:3306`) | 包含 `user_stock_db` 與 `db_employee`，提供 `user_stock` 與 `user_employee` 存取 |
| **Redis 8.8** | `django_redis` | `6379:6379` | 由 Backend 內部連線 (`redis:6379`) | 處理 Django 高併發 Session 與快取資料，掛載實體目錄 `./redis_data` |

---

## 2. MariaDB 12.3 多帳號與 DataTables 管理員運作階段表

| 協作階段 | 運作機制與組件 | 詳細說明與功能描述 |
| :--- | :--- | :--- |
| **1. 多帳號連線設定** | `.env` & `init_multi_db.sql` | 建立 `user_stock` (`user_stock_db`) 與 `user_employee` (`db_employee`) 帳號與讀寫權限 |
| **2. ORM 路由分發** | `PrimaryEmployeeRouter` | 將 `employees` App 導向至 `employee_db`，其他 Model 導向至 `default` |
| **3. 員工表與數據種子** | `employees` & `seed_employees` | Migration 建立 `employees` 資料表，`seed_employees` 自動建立 10 筆隨機測試資料 |
| **4. 帳號切換與權限審計** | `db_manager_index` | 支援 `user_stock` 與 `user_employee` 切換，執行 `SHOW DATABASES`, `SHOW TABLES`, `SHOW GRANTS` |
| **5. DataTables CRUD API**| `db_manager_query/crud_api` | 整合 DataTables.net AJAX 實現資料表搜尋、新增 (Insert)、修改 (Update) 與刪除 (Delete) |
| **6. 群組權限防護** | `can_manage_db_tables` 權限 | 僅超級管理員或 `Database Managers` 群組成員可存取，非授權者回傳 HTTP 403 Forbidden |

## 3. 後端手動測試與驗證環境 (backend_ver)

專案內建的 `backend_ver` 模組旨在提供一個獨立、安全的手動測試驗證平台：

1. **進入容器：** 透過 `docker exec -it fin_django_backend bash` / `sh` 直接進入後端容器 Shell。
2. **驗證腳本執行：** 
   - `test_django_env.py`: 觸發 Django System Check，檢測 Model 定義與 System App 初始化是否有潛在錯誤。
   - `test_db_conn.py`: 驗證 DB 路由轉接，比對 `default` 與 `employee_db` 的真實連線帳號與資料庫筆數。
   - `test_redis_conn.py`: 使用 `django_redis` 連線，透過快取讀寫刪除 (Set/Get/Delete) 確保 Redis 機制運作如預期。
3. **整合報告：** 執行 `run_all.py` 會串聯上述三者，自動格式化輸出結果，方便開發人員與系統維運人員在進行系統微調、資料庫移轉或 Host OS 環境變更時快速定位問題。

## 4. 前端手動測試與驗證環境 (frontend_ver)

專案內建的 `frontend_ver` 模組提供前端容器內的獨立驗證：
1. **進入容器：** 透過 `docker exec -it fin_vue_frontend sh` 直接進入前端容器（亦可執行 `./enter_dc.sh`）。
2. **驗證腳本執行：**
   - `test_env.js`: 驗證 Node 執行環境與 Docker 容器內部的環境變數載入狀態。
   - `test_api.js`: 對後端健康檢測 API 端點執行請求，確認前後端容器間的網路通訊及跨容器 API 呼叫功能。
   - `test_web.js`: 模擬外部對網頁代理伺服器的連線，驗證 Apache 反向代理轉接前端 Vite 開發伺服器是否暢通。
3. **整合報告：** 可透過執行 `node frontend_ver/run_all.js` 或是 `./frontend_ver/run_all.sh` 一鍵執行前述所有前端健康檢查。

## 5. 快捷容器進入工具 (enter_dc.sh)

在專案根目錄提供了互動式 CLI 進入腳本 [enter_dc.sh](file:///home/dengkai/projects/financial-information/enter_dc.sh)，開發者在宿主機只需執行 `bash enter_dc.sh` 並輸入容器名稱（如：`fin_django_backend`），即可快速開啟容器內的 CLI 終端，無須記憶冗長的 `docker exec` 語法。

---

## 相關文件連結
- 返回主要技能規範：[SKILL.md](../SKILL.md)
- 準則細部資訊：[rules_detail.md](../rules/rules_detail.md)
- 指定工具細部資訊：[tools.md](../scripts/tools.md)
- 任務計畫紀錄：[01_implementation_plan.md](../task_logs/01_implementation_plan.md)
