# Django 5.2 + Vue.js 3.5 開發環境逐步解說與驗證報告 (Walkthrough)

本報告記載 **Python Django 5.2 + Vue 3.5 + Apache HTTPD + MariaDB 12.3 (多庫多帳號/實體目錄掛載) + Redis 8.8** 容器化環境與 Host OS 自動判斷、單元測試、跨平台部署作業之完整測試驗證結果。

---

## 1. 服務連線與自動化測試結果對照表

已透過 `docker exec django_backend python manage.py test` 與跨平台部署腳本測試驗證全數運作正常：

| 測試分類 | 測試網址 / 腳本 | 預期回應 / 測試數 | 實測驗證結果 |
| :--- | :--- | :--- | :--- |
| **Django 單元測試** | `docker exec django_backend python manage.py test` | 9 個單元測試案例 (包含端點、多庫路由、快取與員工 Model) | **全數通過 (Ran 9 tests in 0.101s OK)** |
| **統一部署進入點** | `./scripts/deploy.sh` | 自動辨識宿主機 OS 並自動分流執行對應腳本 | **成功 (Exit 0)** |
| **Linux 專用部署** | `./scripts/deploy_linux.sh` | 賦權、Docker 構建、單元測試全數 OK 並驗證 API | **成功 (Exit 0)** |
| **macOS 專用部署** | `./scripts/deploy_mac.sh` | 晶片架構辨識、APFS 掛載、單元測試 OK 並驗證 API | **成功 (Exit 0)** |
| **Windows 專用部署** | `powershell -ExecutionPolicy Bypass -File ./scripts/deploy_windows.ps1` | Docker 構建、自動啟動、單元測試全數 OK 並驗證 API | **成功 (Exit 0)** |
| **自動化健康檢測** | `./scripts/test_health.sh` | 顯示 `🎉 所有自動化健康測試均完全通過!` | **成功 (Exit 0)** |

---

## 2. 宿主機 OS 自動判斷與 MariaDB 實體目錄掛載運作階段表

| 協作階段 | 運作機制與組件 | 詳細說明與功能描述 |
| :--- | :--- | :--- |
| **1. 目錄權限初始化** | `init-dir` (`scripts/init_dir.sh`) | 自動判斷 Host OS (Win/Linux/Mac) 並執行專屬目錄建立與權限修復 (Completed Successfully 退出 Exit 0) |
| **2. 實體目錄掛載** | `docker-compose.yaml` | `django_db` 服務 volume 掛載指向 host 實體目錄 `./db_data:/var/lib/mysql` |
| **3. NTFS / APFS 相容** | `my_custom.cnf` | 配置 `innodb_file_per_table = 0` 與 `innodb_use_native_aio = 0` 解決 Windows/macOS Tablespace 錯誤 |
| **4. OS 自動判斷** | `backend/entrypoint.sh` | 自動辨識 Windows (WSL2)、macOS (LinuxKit) 或 Native Linux 並執行適配遷移 |
| **5. ORM 路由分發** | `PrimaryEmployeeRouter` | 將 `employees` App 導向至 `employee_db`，其他 Model 導向至 `default` |
| **6. 員工表與數據種子** | `employees` & `seed_employees` | Migration 建立 `employees` 資料表，`seed_employees` 自動建立 10 筆隨機測試資料 |
| **7. 全套單元測試** | `core/tests.py` & `employees/tests.py` | 涵蓋端點回應、雙資料庫 ORM 隔離、Redis 寫入與種子指令校驗 |

---

## 3. 專案全檔案相對路徑連結索引

### A. 全局與環境變數設定檔
- **[.env](../../../../.env)**：全局變數，包含 `user_stock` 與 `user_employee` 憑證。
- **[docker-compose.yaml](../../../../docker-compose.yaml)**：6 大服務編排檔，包含 `init-dir` 自動初始化與實體目錄 `./db_data`。

### B. 跨平台單元測試與部署腳本
- **[scripts/init_dir.sh](../../../../scripts/init_dir.sh)**：自動初始化目錄與跨 OS 權限修復腳本 (init-dir 服務專用)。
- **[scripts/deploy.sh](../../../../scripts/deploy.sh)**：跨平台統一自動辨識 OS 與引導入口腳本 (Linux, macOS, Git Bash, WSL)。
- **[scripts/deploy_linux.sh](../../../../scripts/deploy_linux.sh)**：Linux 平台專用 (Ubuntu / Debian / RHEL) 部署與測試腳本。
- **[scripts/deploy_mac.sh](../../../../scripts/deploy_mac.sh)**：macOS 平台專用 (Apple Silicon / Intel) 部署與測試腳本。
- **[scripts/deploy_windows.ps1](../../../../scripts/deploy_windows.ps1)**：Windows 平台專用 (PowerShell) 部署與測試腳本。
- **[scripts/test_health.sh](../../../../scripts/test_health.sh)**：線上健康檢測腳本。

### C. Django 單元測試套件
- **[backend/core/tests.py](../../../../backend/core/tests.py)**：API 端點、多庫路由與 Redis 快取單元測試。
- **[backend/employees/tests.py](../../../../backend/employees/tests.py)**：員工 Model CRUD 與 `seed_employees` 指令單元測試。

---

## 4. 系統存取資訊

- **Vue.js 儀表板 (每10分鐘自動檢測)**：[http://localhost/tech-stack/](http://localhost/tech-stack/)
- **啟用純文字回應**：[http://localhost/](http://localhost/)
- **Django Unfold 後台管理介面**：[http://localhost/admin/](http://localhost/admin/) (預設帳號：`admin`)
- **健康檢查 JSON API**：[http://localhost/api/status/](http://localhost/api/status/)
- **自動化測試腳本**：[../../../scripts/test_health.sh](../../../scripts/test_health.sh)
