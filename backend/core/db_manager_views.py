# ==============================================================================
# 資料庫與表單管理視圖 (backend/core/db_manager_views.py)
# 說明：提供帳號切換、SHOW DATABASES/TABLES 權限檢視、DataTables CRUD API 與群組權限控制
# ==============================================================================

import os
import json
import MySQLdb
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

# 資料庫連線帳戶配置
DB_ACCOUNTS = {
    'user_stock': {
        'name': 'user_stock (可存取 user_stock_db 與 db_employee)',
        'user': os.environ.get('DB_USER', 'user_stock'),
        'password': os.environ.get('DB_PASSWORD', 'user_stock_pass'),
        'default_db': os.environ.get('DB_NAME', 'user_stock_db'),
    },
    'user_employee': {
        'name': 'user_employee (專屬存取 db_employee)',
        'user': os.environ.get('EMPLOYEE_DB_USER', 'user_employee'),
        'password': os.environ.get('EMPLOYEE_DB_PASSWORD', 'user_employee_pass'),
        'default_db': os.environ.get('EMPLOYEE_DB_NAME', 'db_employee'),
    }
}

def check_permission(user):
    """
    檢查使用者是否具備資料庫管理權限 (Superuser 或 core.can_manage_db_tables 權限或在 Database Managers 群組)
    """
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if user.has_perm('core.can_manage_db_tables'):
        return True
    if user.groups.filter(name='Database Managers').exists():
        return True
    return False

def get_connection(account_key, db_name=None):
    """
    根據選定的帳戶與資料庫建立原生 MySQL/MariaDB 連線
    """
    acc = DB_ACCOUNTS.get(account_key, DB_ACCOUNTS['user_stock'])
    host = os.environ.get('DB_HOST', 'db')
    port = int(os.environ.get('DB_PORT', 3306))
    database = db_name if db_name else acc['default_db']
    
    return MySQLdb.connect(
        host=host,
        port=port,
        user=acc['user'],
        passwd=acc['password'],
        db=database,
        charset='utf8mb4'
    )

@login_required
def db_manager_index(request):
    """
    資料庫與表單管理主要視圖頁面
    """
    if not check_permission(request.user):
        return HttpResponseForbidden(
            "<div style='padding:50px; font-family:sans-serif; text-align:center;'>"
            "<h1 style='color:#ef4444;'>🚫 403 Forbidden - 無存取權限</h1>"
            "<p>您未隸屬於 <b>Database Managers (資料庫管理員)</b> 群組且缺乏 <code>can_manage_db_tables</code> 權限。</p>"
            "<a href='/admin/' style='color:#3b82f6;'>返回管理後台主頁</a></div>"
        )

    selected_account = request.GET.get('account', 'user_stock')
    if selected_account not in DB_ACCOUNTS:
        selected_account = 'user_stock'

    databases = []
    tables = []
    grants = []
    selected_db = request.GET.get('db', DB_ACCOUNTS[selected_account]['default_db'])

    try:
        conn = get_connection(selected_account, selected_db)
        cursor = conn.cursor()
        
        # 1. 取得現有資料庫列表 (SHOW DATABASES)
        cursor.execute("SHOW DATABASES;")
        raw_dbs = [row[0] for row in cursor.fetchall()]
        # 過濾系統內建庫
        databases = [d for d in raw_dbs if d not in ('information_schema', 'performance_schema', 'mysql', 'sys')]

        # 2. 取得目前帳戶的操作權限 (SHOW GRANTS)
        cursor.execute("SHOW GRANTS FOR CURRENT_USER();")
        grants = [row[0] for row in cursor.fetchall()]

        # 3. 取得選定資料庫之資料表清單 (SHOW TABLES)
        if selected_db in databases:
            cursor.execute(f"SHOW TABLES FROM `{selected_db}`;")
            tables = [row[0] for row in cursor.fetchall()]
        conn.close()
    except Exception as e:
        grants = [f"連線錯誤: {str(e)}"]

    context = {
        'accounts': DB_ACCOUNTS,
        'selected_account': selected_account,
        'databases': databases,
        'selected_db': selected_db,
        'tables': tables,
        'grants': grants,
    }
    return render(request, 'db_manager.html', context)

@login_required
def db_manager_query_api(request):
    """
    DataTables 資料讀取 API (回傳欄位定義與 JSON 列資料)
    """
    if not check_permission(request.user):
        return JsonResponse({'error': '403 Forbidden'}, status=403)

    account_key = request.GET.get('account', 'user_stock')
    db_name = request.GET.get('db', 'user_stock_db')
    table_name = request.GET.get('table', '')

    if not table_name:
        return JsonResponse({'columns': [], 'data': []})

    try:
        conn = get_connection(account_key, db_name)
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        
        # 取得表單欄位型態
        cursor.execute(f"DESCRIBE `{table_name}`;")
        columns_desc = cursor.fetchall()
        columns = [{'data': col['Field'], 'title': col['Field']} for col in columns_desc]
        pk_field = next((col['Field'] for col in columns_desc if col['Key'] == 'PRI'), columns_desc[0]['Field'] if columns_desc else 'id')

        # 取得資料筆數 LIMIT 500
        cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 500;")
        rows = cursor.fetchall()
        
        # 轉換 date/datetime 為 string
        formatted_rows = []
        for row in rows:
            formatted_row = {}
            for k, v in row.items():
                if v is None:
                    formatted_row[k] = ""
                else:
                    formatted_row[k] = str(v)
            formatted_rows.append(formatted_row)

        conn.close()
        return JsonResponse({
            'columns': columns,
            'data': formatted_rows,
            'pk_field': pk_field
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
def db_manager_crud_api(request):
    """
    DataTables 行新增 / 修改 / 刪除 (CRUD) 操作 API
    """
    if not check_permission(request.user):
        return JsonResponse({'error': '403 Forbidden'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': '僅支援 POST 請求'}, status=400)

    try:
        payload = json.loads(request.body.decode('utf-8'))
        account_key = payload.get('account', 'user_stock')
        db_name = payload.get('db')
        table_name = payload.get('table')
        action = payload.get('action') # insert, update, delete
        row_data = payload.get('data', {})
        pk_field = payload.get('pk_field', 'id')
        pk_value = payload.get('pk_value')

        conn = get_connection(account_key, db_name)
        cursor = conn.cursor()

        if action == 'delete':
            sql = f"DELETE FROM `{table_name}` WHERE `{pk_field}` = %s;"
            cursor.execute(sql, (pk_value,))
            message = f"成功刪除主鍵 {pk_field}={pk_value} 之資料記錄！"

        elif action == 'insert':
            cols = [k for k in row_data.keys() if k != pk_field or row_data[k]]
            vals = [row_data[k] for k in cols]
            cols_sql = ", ".join([f"`{c}`" for c in cols])
            placeholders = ", ".join(["%s"] * len(cols))
            sql = f"INSERT INTO `{table_name}` ({cols_sql}) VALUES ({placeholders});"
            cursor.execute(sql, vals)
            message = "成功新增資料記錄！"

        elif action == 'update':
            cols = [k for k in row_data.keys() if k != pk_field]
            vals = [row_data[k] for k in cols]
            set_sql = ", ".join([f"`{c}` = %s" for c in cols])
            vals.append(pk_value)
            sql = f"UPDATE `{table_name}` SET {set_sql} WHERE `{pk_field}` = %s;"
            cursor.execute(sql, vals)
            message = f"成功更新主鍵 {pk_field}={pk_value} 之資料記錄！"

        conn.commit()
        conn.close()
        return JsonResponse({'status': 'success', 'message': message})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
