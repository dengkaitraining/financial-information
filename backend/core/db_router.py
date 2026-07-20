# ==============================================================================
# Django 多資料庫路由轉接器 (backend/core/db_router.py)
# 說明：將 employees 應用程式的 Model 讀寫與 Migration 指令自動導向至 employee_db
# ==============================================================================

class PrimaryEmployeeRouter:
    """
    資料庫路由轉接器：導向 employees 模組模型至 employee_db 資料庫
    """
    route_app_labels = {'employees'}

    def db_for_read(self, model, **hints):
        """讀取操作時選擇資料庫"""
        if model._meta.app_label in self.route_app_labels:
            return 'employee_db'
        return 'default'

    def db_for_write(self, model, **hints):
        """寫入操作時選擇資料庫"""
        if model._meta.app_label in self.route_app_labels:
            return 'employee_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """允許同資料庫或相容模型的關聯"""
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """控制各資料庫執行的 Migration 操作"""
        if app_label in self.route_app_labels:
            return db == 'employee_db'
        return db == 'default'


