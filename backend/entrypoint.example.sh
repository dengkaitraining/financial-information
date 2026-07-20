#!/bin/sh
# ==============================================================================
# Django 5.2 容器初始化啟動腳本 (backend/entrypoint.sh)
# 說明：自動檢測宿主機 OS (Windows / Linux / Mac)、TCP 3306 輪詢等待、
#      多資料庫與帳號自動建立、跨 OS 遷移模式適配、Superuser & 種子資料產生
# ==============================================================================
set -e
echo "======================================================================"
echo "🚀 啟動 Django 5.2 容器初始化程序 (entrypoint.sh)"
echo "======================================================================"
# 0. 跨平台宿主機作業系統自動檢測 (Host OS Auto-Detection)
# 可透過 .env 內的 HOST_OS 強制覆寫 (windows, linux, mac)，否則自動根據系統核心特徵判斷
HOST_OS_TYPE="${HOST_OS:-auto}"
if [ "$HOST_OS_TYPE" = "auto" ]; then
    if grep -qi "microsoft\|wsl" /proc/version 2>/dev/null; then
        HOST_OS_TYPE="windows"
    elif grep -qi "linuxkit" /proc/version 2>/dev/null; then
        HOST_OS_TYPE="mac"
    else
        HOST_OS_TYPE="linux"
    fi
fi
case "$HOST_OS_TYPE" in
    windows)
        echo "💻 檢測到宿主機作業系統：Windows (WSL2 / Docker Desktop)"
        echo "   👉 啟用 Windows NTFS 實體目錄掛載適配模式 (lower_case_table_names=1 / ./db_data)"
        ;;
    mac)
        echo "🍎 檢測到宿主機作業系統：macOS (Docker Desktop / LinuxKit)"
        echo "   👉 啟用 macOS APFS 實體目錄掛載適配模式"
        ;;
    linux|*)
        echo "🐧 檢測到宿主機作業系統：Native Linux (Ubuntu / Debian / RHEL)"
        echo "   👉 啟用 Native Linux 原生高效能模式"
        ;;
esac
# 1. 等待 MariaDB 數據庫埠號 3306 開啟
echo "1. 等待 MariaDB 3306 埠號連線就緒..."
while ! nc -z ${DB_HOST:-db} ${DB_PORT:-3306}; do
    echo "  MariaDB 資料庫尚未就緒，等待 0.5 秒..."
    sleep 0.5
done
echo "✓ MariaDB 資料庫連線成功！"
# 2. 以 Root 身份防錯初始化 db_employee 與連線帳戶 (user_stock & user_employee)
echo "2. 初始化 MariaDB 多資料庫 (user_stock_db & db_employee) 與多連線帳密..."
python manage.py shell << 'EOF'
import os
import time
import MySQLdb
host = os.environ.get('DB_HOST', 'db')
port = int(os.environ.get('DB_PORT', 3306))
root_pass = os.environ.get('DB_ROOT_PASSWORD', 'db_root_secure_pass')
for attempt in range(10):
    try:
        conn = MySQLdb.connect(host=host, user='root', passwd=root_pass, port=port)
        cursor = conn.cursor()
        # 建立資料庫
        cursor.execute("CREATE DATABASE IF NOT EXISTS `user_stock_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cursor.execute("CREATE DATABASE IF NOT EXISTS `db_employee` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        # 建立 user_employee 並賦予權限
        emp_user = os.environ.get('EMPLOYEE_DB_USER', 'user_employee')
        emp_pass = os.environ.get('EMPLOYEE_DB_PASSWORD', 'user_employee_pass')
        cursor.execute(f"CREATE USER IF NOT EXISTS '{emp_user}'@'%' IDENTIFIED BY '{emp_pass}';")
        cursor.execute(f"GRANT ALL PRIVILEGES ON `db_employee`.* TO '{emp_user}'@'%';")
        cursor.execute(f"GRANT ALL PRIVILEGES ON *.* TO '{emp_user}'@'%';")
        # 建立 user_stock 並賦予權限 (包含存取 db_employee 與單元測試資料庫 test_% 權限)
        # 建立 user_stock 並賦予權限 (包含存取 db_employee 權限)
        stock_user = os.environ.get('DB_USER', 'user_stock')
        stock_pass = os.environ.get('DB_PASSWORD', 'user_stock_pass')
        cursor.execute(f"CREATE USER IF NOT EXISTS '{stock_user}'@'%' IDENTIFIED BY '{stock_pass}';")
        cursor.execute(f"GRANT ALL PRIVILEGES ON `user_stock_db`.* TO '{stock_user}'@'%';")
        cursor.execute(f"GRANT ALL PRIVILEGES ON `db_employee`.* TO '{stock_user}'@'%';")
        cursor.execute(f"GRANT ALL PRIVILEGES ON *.* TO '{stock_user}'@'%';")
        cursor.execute("FLUSH PRIVILEGES;")
        conn.close()
        print("✓ MariaDB 多資料庫 (user_stock_db, db_employee) 與帳號 (user_stock, user_employee) 權限初始化完成！")
        break
    except Exception as e:
        print(f"MariaDB 初始化嘗試 ({attempt+1}/10): {e}")
        time.sleep(1)
EOF
# 3. 根據宿主機作業系統執行適配的 ORM Schema 遷移
echo "3. 執行 Django ORM Schema 遷移 ($HOST_OS_TYPE 模式適配)..."
if [ "$HOST_OS_TYPE" = "windows" ] || [ "$HOST_OS_TYPE" = "mac" ]; then
    echo "   👉 Windows/macOS 實體目錄掛載適配模式 (含 Schema 殘留防護)..."
    python manage.py migrate --database=default --noinput || python manage.py migrate --database=default --fake-initial --noinput || true
    python manage.py migrate --database=employee_db --noinput || python manage.py migrate --database=employee_db --fake-initial --noinput || true
else
    # Native Linux 原生實體目錄掛載模式
    python manage.py migrate --database=default --noinput
    python manage.py migrate --database=employee_db --noinput
fi
# 4. 初始化超級管理員
echo "4. 檢查與自動初始化超級管理員..."
python manage.py shell << 'EOF'
import os
from django.contrib.auth.models import User
from django.utils import timezone
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpassword123')
if not User.objects.filter(username=username).exists():
    user = User(username=username, email=email, is_staff=True, is_superuser=True, last_login=timezone.now())
    user.set_password(password)
    user.save()
    print(f"✓ 已成功創建超級管理員帳號：{username}")
EOF
# 5. 生成 10 筆測試員工主資料 (employees 資料表)
echo "5. 自動產生 10 筆測試員工主資料 (seed_employees)..."
python manage.py seed_employees || true
# 6. 啟動 Django 開發伺服器
echo "6. 啟動 Django 開發伺服器 (runserver 0.0.0.0:8000)..."
exec python manage.py runserver 0.0.0.0:8000