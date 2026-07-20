# ==============================================================================
# 核心模組 Django Model與權限宣告 (backend/core/models.py)
# 說明：定義『資料庫與表單管理』進階群組權限 (can_manage_db_tables)
# ==============================================================================

from django.db import models

class DatabaseManagerPermission(models.Model):
    """
    虛擬 Model: 用於宣告資料庫與表單管理功能之群組權限
    """
    class Meta:
        managed = False
        default_permissions = ()
        permissions = [
            ("can_manage_db_tables", "可以管理資料庫與表單資料 (DataTables & 帳號切換)"),
        ]
