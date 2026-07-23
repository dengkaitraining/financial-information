# Django on Docker 完成後的檢查清單 (Final Inspection)

本文件提供開發者或自動化測試流程於系統完成建置與修補後的最終檢核清單與測試指引。

---

## 1. 服務容器狀態檢核表

| 檢核項目 | 容器名稱 (Container) | 埠號 mapping | 檢驗標準 / 預期狀態 | 測試與驗證結果 |
| :--- | :--- | :--- | :--- | :--- |
| **反向代理網頁伺服器** | `apache_web` | `80:80` | 容器狀態為 `Up`，無 Crash | **通過 (Up)** |
| **Vue 3.5 前端伺服器** | `vue_frontend` | `5173:5173` | 容器狀態為 `Up`，Vite polling 運作 | **通過 (Up)** |
| **Django 5.2 後端伺服器** | `django_backend` | `8000:8000` | 容器狀態為 `Up`，Migration 與 DataTables 管理員正常 | **通過 (Up)** |
| **MariaDB 12.3 資料庫** | `django_db` | `3306:3306` | 容器狀態為 `Up`，包含 `user_stock_db` 與 `db_employee` | **通過 (Up)** |
| **Redis 8.8 快取伺服器** | `django_redis` | `6379:6379` | 容器狀態為 `Up`，持久化於 `./redis_data` | **通過 (Up)** |

---

## 2. URL 路由與連線功能檢核表

| 測試分類 | 測試 URL / 標的 | 檢驗方法 / 指令 | 預期結果 / 判定條件 | 驗證結果 |
| :--- | :--- | :--- | :--- | :--- |
| **根目錄服務檢查** | `http://localhost/` | `curl -s http://localhost/` | 包含文字 `Django + Vue.js Web 資訊系統開發環境` | **通過 (200 OK)** |
| **健康檢測 API** | `http://localhost/api/status/` | `curl -s http://localhost/api/status/` | JSON 返回 `database` 與 `redis` 皆為 `"connected"` | **通過 (200 OK)** |
| **Vue 3.5 儀表板** | `http://localhost/tech-stack/` | `curl -sI http://localhost/tech-stack/` | 回應 HTTP `200 OK` HTML，顯示所有技術圖標 | **通過 (200 OK)** |
| **DataTables 管理員** | `http://localhost/admin/db-manager/` | 存取 `/admin/db-manager/` | 檢查帳號切換 (`user_stock`/`user_employee`)、SHOW DATABASES & DataTables CRUD | **通過 (200 OK/302)** |
| **群組權限管制** | `can_manage_db_tables` 權限 | 測試非授權使用者連線 | 回傳 HTTP 403 Forbidden 拒絕存取 | **通過 (403)** |
| **自動化測試腳本** | `./scripts/test_health.sh` | 執行 `./scripts/test_health.sh` | 顯示 `🎉 所有自動化健康測試均完全通過!` | **通過 (Exit 0)** |
| **後端手動測試** | `python backend_ver/run_all.py` | 進入 `fin_django_backend` 執行驗證 | Django 檢查、DB 雙庫讀寫、Redis 測試、GNews 爬蟲測試皆順利通過 | **通過** |
| **前端手動測試** | `node frontend_ver/run_all.js` | 進入 `fin_vue_frontend` 執行驗證 | Node 環境、API 連線、Apache 網頁健康檢測皆通過 | **通過** |
| **快捷進入工具** | `bash enter_dc.sh` | 於宿主機執行並輸入目標容器名稱 | 順利開啟目標容器 terminal shell | **通過** |
| **環境變數檢查** | `.env` 設定檔 | 檢查 `.env` | `DJANGO_DEBUG=True`、`SHOW_BACKEND_VER=True` 且 `SHOW_FRONTEND_VER=True` | **通過** |

---

## 相關文件連結
- 返回主要技能規範：[SKILL.md](../SKILL.md)
- 準則細部資訊：[rules_detail.md](../rules/rules_detail.md)
- 指定工具細部資訊：[tools.md](../scripts/tools.md)
- 逐步解說細部資訊：[walkthrough_details.md](../references/walkthrough_details.md)
