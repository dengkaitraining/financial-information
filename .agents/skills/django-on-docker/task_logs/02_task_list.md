# Django 5.2 + Vue.js 3.5 開發環境任務清單 (Task List)

本檔案記錄本專案已完成之多資料庫設定、實體目錄掛載、Host OS 自動判斷、員工表單建置、Unfold 後台開展、單元測試套件與跨平台自動化部署作業。

---

## 1. 任務執行與完成對照表

| 分類 | 任務說明 | 影響對象 / 檔案 | 完成狀態 |
| :--- | :--- | :--- | :--- |
| **init-dir 服務** | 新增 `init-dir` 服務與 `scripts/init_dir.sh` 自動判斷 Host OS 權限修復 | `docker-compose.yaml`, `scripts/init_dir.sh` | **[x] 已完成** |
| **多連線設定** | 配置 `.env` 之 `user_stock` (`user_stock_db`) 與 `user_employee` (`db_employee`) 憑證 | [.env](../../../../.env) | **[x] 已完成** |
| **實體目錄掛載** | `docker-compose.yaml` 中 `django_db` volumes 指向實體目錄 `./db_data` | `docker-compose.yaml` | **[x] 已完成** |
| **OS 自動判斷** | `entrypoint.sh` 自動判斷 Windows/Linux/Mac 宿主機並選擇適配模式 | `backend/entrypoint.sh` | **[x] 已完成** |
| **多庫初始化** | 建立 `init_multi_db.sql` 建立雙資料庫與設定權限 (含 `test_%` 單元測試權限) | `db_conf/init_multi_db.sql` | **[x] 已完成** |
| **Django Multi-DB**| 設定 `settings.py` 之 `DATABASES` 雙連線與 `PrimaryEmployeeRouter` 路由轉接器 | `settings.py`, `db_router.py` | **[x] 已完成** |
| **單元測試套件** | 建立 Django 5.2 後端 API、多庫路由、Redis 快取與 Employee Model 單元測試 | `core/tests.py`, `employees/tests.py` | **[x] 已完成 (9 Tests OK)** |
| **統一入口部署** | 建立跨平台統一進入點 (Linux, macOS, Git Bash, WSL) 部署與測試腳本 | `scripts/deploy.sh` | **[x] 已完成** |
| **Linux 部署** | 建立 Native Linux (Ubuntu/Debian/RHEL) 專用自動化部署與單元測試腳本 | `scripts/deploy_linux.sh` | **[x] 已完成** |
| **macOS 部署** | 建立 macOS (Apple Silicon / Intel) 專用自動化部署與單元測試腳本 | `scripts/deploy_mac.sh` | **[x] 已完成** |
| **Windows 部署** | 建立 Windows PowerShell 專用自動化部署與單元測試腳本 | `scripts/deploy_windows.ps1` | **[x] 已完成** |
| **手動測試環境 (Python)** | 增加 `backend_ver` 程式手動測試驗證環境，包含一鍵測試與多庫/快取驗證，實體檔案在 `.backend_ver/` 隱藏目錄 | `backend/.backend_ver/` | **[x] 已完成** |
| **環境控制參數 (Python)** | 增加 `SHOW_BACKEND_VER` 控制參數，開發環境顯示 `backend_ver` 軟連結，正式上線隱蔽並刪除 | `.env`, `settings.py`, `entrypoint.sh` | **[x] 已完成** |
| **手動測試環境 (Vue)** | 增加 `frontend_ver` 前端手動測試驗證環境，驗證 Node 環境、API 端點連線與 Apache 代理 | `frontend/.frontend_ver/` | **[x] 已完成** |
| **環境控制參數 (Vue)** | 增加 `SHOW_FRONTEND_VER` 控制參數，開發環境顯示 `frontend_ver` 軟連結，正式上線隱蔽並刪除 | `.env`, `frontend/entrypoint.sh` | **[x] 已完成** |
| **快速進入容器工具** | 增加根目錄 `enter_dc.sh` 互動式 CLI 腳本，方便快速進入各個容器之 shell 端點 | `enter_dc.sh` | **[x] 已完成** |
| **第三方套件整合** | 增加 `gnews` 爬蟲套件與 `pandas` 資料分析套件，並整合進後端手動測試驗證環境 | `backend/requirements.txt` | **[x] 已完成** |
| **全專案註解** | 補齊全數程式與服務設定檔之詳細繁體中文註解 | 全專案代碼與設定檔 | **[x] 已完成** |
| **Skill 與 README** | 更新 `README.md` (含跨平台部署指令) 與 Skill 規範 | `README.md`, `skills/` | **[x] 已完成** |

---

## 2. 任務項目清單 (Checklist)

- [x] 建立全局環境變數設定檔 (`.env`)，包含 `user_stock` 與 `user_employee` 資料庫連線憑證
- [x] 配置 `docker-compose.yaml` 中 `django_db` 服務 storage 指向專案內實體目錄 `./db_data:/var/lib/mysql`
- [x] 在 `backend/entrypoint.sh` 加入 Host OS 自動判斷 (Windows, Linux, macOS) 並調配適配動作
- [x] 建立 MariaDB 多資料庫初始化腳本 (`db_conf/init_multi_db.sql`) 並授權全域測試權限
- [x] 設定 Django `settings.py` 之多資料庫連線 (`default` 與 `employee_db`)
- [x] 實作 Django 多資料庫路由轉接器 ([backend/core/db_router.py](../../../../backend/core/db_router.py))
- [x] 建立 Django 後端單元測試套件 (`core/tests.py` & `employees/tests.py`)，驗證 API 狀態、路由、快取與員工 Model 操作
- [x] 建立跨平台部署與測試腳本 (`deploy.sh`, `deploy_linux.sh`, `deploy_mac.sh`, `deploy_windows.ps1`)
- [x] 測試並確認 9 個 Django 單元測試在容器中 100% 成功執行
- [x] 執行自動化測試腳本 [../../../scripts/test_health.sh](../../../scripts/test_health.sh) 並測試通過
- [x] 輸出專案文件至 `./task_logs/` (`01_implementation_plan.md`, `02_task_list.md`, `03_walkthrough.md`)
- [x] 建立 `backend_ver` 後端手動測試驗證環境與一鍵整合測試執行器 (`run_all.py`)
- [x] 整合 `SHOW_BACKEND_VER` 控制參數，驗證正式上線隱蔽與開發環境顯示功能
- [x] 建立 `frontend_ver` 前端手動測試驗證環境與一鍵整合測試執行器 (`run_all.js`, `run_all.sh`)
- [x] 整合 `SHOW_FRONTEND_VER` 控制參數，驗證前端正式上線隱蔽與開發環境顯示功能
- [x] 建立 `enter_dc.sh` 快速容器進入工具並測試其可行性
- [x] 整合 `gnews` 與 `pandas` 第三方套件至後端環境，並完成相關爬蟲測試腳本之放置
- [x] 建立與維護最新版 [README.md](../../../../README.md) (含跨平台部署指令、Mermaid 架構圖與說明)

---

## 相關文件連結
- 主要技能規範：[SKILL.md](../SKILL.md)
- 實作計畫紀錄：[01_implementation_plan.md](./01_implementation_plan.md)
- 逐步解說紀錄：[03_walkthrough.md](./03_walkthrough.md)
