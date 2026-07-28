# Django on Docker 常用指令與指定工具指南 (tools.md)

本文件整理了在此 Django on Docker 容器化技術堆疊中，管理、開發、遷移、與測試背景排程服務所使用的常用指令與指定工具。

---

## 🐳 1. Docker Compose 容器管理

### 服務啟動與關閉
```bash
# 原生一鍵自動偵測部署與測試
./scripts/deploy.sh

# 啟動所有容器服務 (背景運行)
docker compose up -d

# 強制重建並啟動所有容器服務
docker compose up -d --build

# 停止並刪除所有容器、Bridge 網路與掛載目錄
docker compose down

# 停止所有容器服務但不刪除
docker compose stop
```

### 檢視容器狀態與日誌
```bash
# 檢視所有運行中的服務容器與狀態
docker compose ps

# 檢視後端 Django 容器即時日誌
docker compose logs -f fin-backend

# 檢視背景 Celery Worker 容器即時日誌
docker compose logs -f fin-celery-worker

# 檢視定期排程 Celery Beat 容器即時日誌
docker compose logs -f fin-celery-beat
```

---

## 📦 2. Django 5.2 數據庫遷移與管理

所有 Models 欄位變更或新增時，均必須採用 Django 內建遷移版控工具：

```bash
# 1. 針對特定股票 stock_db app 產生資料庫遷移檔
docker compose exec fin-backend python manage.py makemigrations stock_db

# 2. 套用遷移至 MariaDB 資料庫 (應用遷移)
docker compose exec fin-backend python manage.py migrate

# 3. 進入 Django shell 互動式終端
docker compose exec fin-backend python manage.py shell

# 4. 生成 10 筆測試員工主資料 (seed 指令)
docker compose exec fin-backend python manage.py seed_employees
```

---

## 🧪 3. 單元測試與健康度檢查

在提交程式碼前，必須執行全套單元測試與健康檢查，以保證服務功能完整：

```bash
# 1. 執行後端 stock_db 模組全套單元測試 (含 ORM 欄位約束、外鍵聯合唯一約束、批次 upsert 邏輯)
docker compose exec fin-backend python manage.py test stock_db

# 2. 執行線上服務自動化健康檢測 (檢測 URL、API、連線變數)
./scripts/test_health.sh
```

---

## 🛠️ 4. 快捷 CLI 進入與手動驗證環境

### 進入容器
```bash
# 使用互動式腳本快速進入指定容器的 shell
bash enter_dc.sh
```

### 執行手動驗證模組
```bash
# 進入 Django 後端容器並執行一鍵整合手動驗證 (資料庫/快取連線)
docker compose exec fin-backend python backend_ver/run_all.py

# 進入 Vue 前端容器並執行一鍵整合手動驗證 (Node環境/API響應/Apache轉接)
docker compose exec fin-frontend node frontend_ver/run_all.js
```
