# Django 5.2 + Vue.js 3.5 多資料庫與 Unfold 後台實作計畫 (Implementation Plan)

本實作計畫詳細記載基於 Docker Compose 建立之 **Python Django 5.2 (整合 Django Unfold 美觀後台與多資料庫管理)**、**MariaDB 12.3 多連線帳號與權限架構**、**Vue.js 3.5 (整合 TypeScript 與 Tailwind CSS 4.3)**、**Apache HTTPD 反向代理** 與 **Redis 8.8** 完整 Stack 之架構、服務設計、Host OS 自動判斷、實體目錄掛載適配、單元測試套件與跨平台自動化部署作業。

---

## 1. 系統服務組件與多資料庫對照表

| 服務名稱 | 技術堆疊與版本 | 自定義設定檔 / 資料庫 | 職責說明與權限範疇 |
| :--- | :--- | :--- | :--- |
| **`init-dir`** | Alpine Linux (`latest`) | `scripts/init_dir.sh` | 自動判斷 Host OS (Win/Linux/Mac) 建立實體目錄與權限修復 |
| **`web`** | Apache HTTPD `2.4-alpine` | `httpd-custom.conf` | 反向代理網頁伺服器，統一 Port 80 進入點與路由分發 |
| **`db`** | MariaDB `12.3` | `my_custom.cnf`, `init_multi_db.sql` | 包含 `user_stock_db` 與 `db_employee`，實體目錄 `./db_data` 持久化 |
| **`redis`** | Redis `8.8` | `redis.conf` | 提供 Django 快取與 Session 記憶體資料庫，實體目錄 `./redis_data` 持久化 |
| **`backend`** | Python `3.11` + Django `5.2 LTS` | `settings.py`, `db_router.py`, `entrypoint.sh` | 搭載 Unfold 美觀後台、`employees` 模組、Host OS 自動判斷與全套單元測試 |
| **`frontend`** | Node `20` + Vue `3.5` + Tailwind `4.3` | `vite.config.ts` | 系統儀表板 (Vite `base: /tech-stack/`)，含 10 分鐘自動檢測 |

---

## 2. MariaDB 12.3 多帳號與多資料庫 (.env) 協作架構

在 [.env](../../../../.env) 中配置有雙帳號與雙資料庫連線參數，滿足企業多資料庫隔離與跨庫存取需求：

1. **`user_stock_db` (主要資料庫)**：
   - 連線帳號：`user_stock` (`DB_USER`) / 密碼：`user_stock_pass`
   - 權限範疇：具備 `user_stock_db.*` 完整讀寫權限，並經授權可同時讀寫 `db_employee.*` 及全域測試權限。
2. **`db_employee` (員工主資料庫)**：
   - 連線帳號：`user_employee` (`EMPLOYEE_DB_USER`) / 密碼：`user_employee_pass`
   - 權限範疇：具備 `db_employee.*` 專屬讀寫權限。
3. **實體目錄掛載 (`./db_data`)**：
   - `docker-compose.yaml` 中 `django_db` volumes 指向 `./db_data:/var/lib/mysql`。配合 `my_custom.cnf` 設定 `innodb_file_per_table = 0` 與 `innodb_use_native_aio = 0` 防止 Windows NTFS / macOS APFS 實體目錄 Tablespace `errno 194` 重命名錯誤。
4. **Host OS 自動判斷 (`entrypoint.sh`)**：
   - 容器啟動時會透過核心特徵判斷宿主機作業系統 (`windows`, `linux`, `mac`)，自動套用適配的 ORM Schema 遷移與備援機制。

---

## 3. 跨平台自動檢測部署與單元測試作業架構 (Multi-OS Deployment & Testing)

專案提供支援 **Windows**、**Linux** 與 **macOS** 三大作業系統的自動化單元測試與部署腳本：

1. **統一跨平台進入點 (Linux, macOS, Git Bash, WSL)**:
   - `./scripts/deploy.sh`：自動偵測 Host OS 並轉接專屬部署與單元測試。
2. **Linux 平台專用 (Ubuntu / Debian / RHEL)**:
   - `./scripts/deploy_linux.sh`：Linux 原生 Docker Engine 高效能部署模式與自動權限校驗。
3. **macOS 平台專用 (Apple Silicon / Intel)**:
   - `./scripts/deploy_mac.sh`：macOS (Apple Silicon M 系列 / Intel x86_64) 與 APFS 檔案系統掛載適配。
4. **Windows 平台專用 (PowerShell)**:
   - `powershell -ExecutionPolicy Bypass -File ./scripts/deploy_windows.ps1`：Windows 10/11 PowerShell 5.1+ 與 Docker Desktop (WSL2 / NTFS 掛載適配)。
5. **Django 單元測試套件 (`core/tests.py` & `employees/tests.py`)**:
   - 包含 API 端點狀態、`PrimaryEmployeeRouter` 多庫路由、Redis 快取 Set/Get、`Employee` Model CRUD 與 `seed_employees` 管理指令測試（9 項測試全數通過）。

## 4. 後端手動測試與驗證環境架構 (backend_ver)

專案在後端容器 `fin_django_backend` 內提供了手動測試驗證模組 `backend_ver`，其實體檔案存放在隱藏資料夾 `.backend_ver` 中，並透過軟連結進行公開/隱蔽控制：
1. **進入點**：透過 `docker exec -it fin_django_backend bash` / `sh` 進入容器執行（亦可透過 `enter_dc.sh`）。
2. **驗證指令**：執行 `python backend_ver/run_all.py` 進行一鍵整合測試（軟連結啟用時）。
3. **測試模組**：
   - `test_django_env.py`：驗證系統環境與 System Check。
   - `test_db_conn.py`：驗證多資料庫路由與連線帳密讀寫權限。
   - `test_redis_conn.py`：驗證 Redis Cache API 的 Set/Get/Delete。
   - `gnews_scraper/`：手動新聞爬取測試模組 (包含 gnews 與 pandas 套件之安裝驗證)。
4. **控制參數 (`SHOW_BACKEND_VER`) 目錄控制**：
   - **測試開發環境 (`SHOW_BACKEND_VER=True`)**：容器啟動時自動建立軟連結 `backend_ver -> .backend_ver`，使測試資料夾與內容正常顯現並可供執行。
   - **正式上線環境 (`SHOW_BACKEND_VER=False`)**：容器啟動時自動刪除軟連結 `backend_ver`，徹底隱蔽測試資料夾與內容，防範敏感程式洩漏。

---

## 5. 前端手動測試與驗證環境架構 (frontend_ver)

專案在前端容器 `fin_vue_frontend` 內提供了手動測試驗證模組 `frontend_ver`，其實體檔案存放在隱藏資料夾 `.frontend_ver` 中，並透過軟連結進行公開/隱蔽控制：
1. **進入點**：透過 `docker exec -it fin_vue_frontend sh` 進入容器執行（亦可透過 `enter_dc.sh`）。
2. **驗證指令**：執行 `node frontend_ver/run_all.js` 或是 `sh frontend_ver/run_all.sh` 進行一鍵整合測試。
3. **測試模組**：
   - `test_env.js`：驗證前端 Node 環境與環境變數。
   - `test_api.js`：驗證後端 API 連線與健康回應狀態。
   - `test_web.js`：驗證 Apache HTTPD 反向代理與網頁健康。
4. **控制參數 (`SHOW_FRONTEND_VER`) 目錄控制**：
   - **測試開發環境 (`SHOW_FRONTEND_VER=True`)**：容器啟動時自動建立軟連結 `frontend_ver -> .frontend_ver`，使測試資料夾與內容正常顯現並可供執行。
   - **正式上線環境 (`SHOW_FRONTEND_VER=False`)**：容器啟動時自動刪除軟連結 `frontend_ver`，徹底隱蔽前端測試資料夾與內容，防範敏感腳本外洩。

---

## 6. 互動式快捷進入工具 (enter_dc.sh)

在專案根目錄下建立了 `enter_dc.sh` 互動式 CLI 腳本，簡化開發者進入 Docker 容器的步驟：
- 執行 `bash enter_dc.sh`。
- 輸入目標容器名稱後，腳本會自動選取適合的終端核心（`bash` 優先，失敗則回退使用 `sh`）進入。

---

## 7. URL 路由對照表

| 造訪網址 (URL) | 轉接目標服務 | 預期回應與功能說明 | 權限要求 |
| :--- | :--- | :--- | :--- |
| **`http://localhost/`** | Django Backend (`/`) | 純文字：`Django + Vue.js Web 資訊系統開發環境的服務已啟用。` | 無需權限 |
| **`http://localhost/tech-stack/`** | Vue 3.5 Frontend (`/tech-stack/`) | Vue 3.5 資訊系統儀表板 (含 10 分鐘自動檢測) | 無需權限 |
| **`http://localhost/admin/`** | Django Backend (`/admin/`) | Django Unfold 管理員後台 (包含 `employees` 員工表) | Staff / Admin 權限 |
| **`http://localhost/api/status/`** | Django Backend (`/api/status/`) | 健康檢測 JSON 數據 (MariaDB & Redis 檢測) | 無需權限 |

---

## 相關文件連結
- 主要技能規範：[SKILL.md](../SKILL.md)
- 任務清單紀錄：[02_task_list.md](./02_task_list.md)
- 逐步解說紀錄：[03_walkthrough.md](./03_walkthrough.md)
