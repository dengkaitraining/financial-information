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

---

## 相關文件連結
- 返回主要技能規範：[SKILL.md](../SKILL.md)
- 準則細部資訊：[rules_detail.md](../rules/rules_detail.md)
- 指定工具細部資訊：[tools.md](../scripts/tools.md)
- 任務計畫紀錄：[01_implementation_plan.md](../task_logs/01_implementation_plan.md)
