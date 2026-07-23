# 後端手動測試驗證環境 (`backend_ver`)

本目錄為 `fin_django_backend` 容器提供了 Python 程式與模組手動測試驗證的環境，方便開發者直接進入容器進行各項服務的健康度與整合驗證。

---

## 1. 進入容器方式 (CLI)

請開啟終端機 (bash, sh, 或是 PowerShell/CMD)，透過 Docker CLI 指令進入後端容器：

```bash
# 使用 bash 進入容器 (推薦)
docker exec -it fin_django_backend bash

# 或是使用 sh 進入容器
docker exec -it fin_django_backend sh
```

---

## 2. 執行驗證程式

進入容器後，預設工作目錄為 `/app`。您可以在容器內直譯器中執行以下指令進行手動測試驗證：

### 一鍵執行所有驗證項目
此腳本將自動按順序驗證 Django 系統環境、MariaDB 雙資料庫連線權限、Redis 緩存讀寫：
```bash
python backend_ver/run_all.py
```

### 執行單項驗證腳本
*   **驗證 Django 系統檢查與環境變數：**
    ```bash
    python backend_ver/test_django_env.py
    ```
*   **驗證 MariaDB 雙庫讀寫權限與多庫路由：**
    ```bash
    python backend_ver/test_db_conn.py
    ```
*   **驗證 Redis 快取 Set/Get/Delete 運作：**
    ```bash
    python backend_ver/test_redis_conn.py
    ```

---

## 3. 目錄檔案說明

*   [__init__.py](file:///home/dengkai/projects/financial-information/backend/backend_ver/__init__.py) - 套件初始化檔案。
*   [test_django_env.py](file:///home/dengkai/projects/financial-information/backend/backend_ver/test_django_env.py) - Django 內建系統自我檢查與重要環境變數列印。
*   [test_db_conn.py](file:///home/dengkai/projects/financial-information/backend/backend_ver/test_db_conn.py) - `default` (user_stock_db) 與 `employee_db` (db_employee) 雙連線與權限校驗。
*   [test_redis_conn.py](file:///home/dengkai/projects/financial-information/backend/backend_ver/test_redis_conn.py) - Redis Cache 連線測試與快取 Key-Value 操作。
*   [run_all.py](file:///home/dengkai/projects/financial-information/backend/backend_ver/run_all.py) - 整合執行器，串聯執行上述所有驗證腳本。
