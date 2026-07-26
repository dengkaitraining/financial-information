# django unfold crontab 排程設定
Django Unfold 是一個用於美化 Django Admin 後台的現代化主題（基於 Tailwind CSS），它本身並不包含 Crontab 排程引擎。要實作排程功能，通常需要結合 Django 的排程套件。
以下為您提供兩種在 Django 專案中設定 Crontab 排程最主流的方法。

------------------------------
## 方法一：使用 Django Celery Beat（最推薦，最適合大型專案與後台管理）
此方法可以完美與 Django Unfold 融合，讓您直接在美化後的 Unfold 後台內，用圖形化介面新增、修改或刪除 Crontab 定時任務。
## 1. 安裝必要套件
```python
pip install celery django-celery-beat django-unfold Redis
```
## 2. 修改 settings.py 配置
將 django_celery_beat 加入應用程式列表：
```python
INSTALLED_APPS = [
    "unfold",  # 確保 unfold 在最前面
    # ... 其他 unfold.contrib
    "django.contrib.admin",
    "django_celery_beat",  # 加入此行
    # ... 其他 apps
]
# Celery 配置（以 Redis 作為 Broker 為例）
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
# 指定儲存排程的後端為 Django 資料庫
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
```
## 3. 讓 Unfold 接管 Celery Beat 的 Admin 介面（選填）
在您的 ```admin.py``` 中，可以將 ```django-celery-beat``` 的 Model 改用 Unfold 的樣式呈現：
```python
from django.contrib import admin
from django_celery_beat.admin import PeriodicTaskAdmin, CrontabScheduleAdmin
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from unfold.admin import ModelAdmin

# 先註冊原本的
admin.site.unregister(PeriodicTask)
admin.site.unregister(CrontabSchedule)

# 用 Unfold 的 ModelAdmin 重新註冊
@admin.register(PeriodicTask)class UnfoldPeriodicTaskAdmin(PeriodicTaskAdmin, ModelAdmin):
    pass

@admin.register(CrontabSchedule)class UnfoldCrontabScheduleAdmin(CrontabScheduleAdmin, ModelAdmin):
    pass
```
## 4. 執行遷移與啟動服務
```python
python manage.py migrate
# 啟動 Celery Worker
celery -A 您的專案名稱 worker --loglevel=info
# 啟動 Celery Beat (負責發送排程)
celery -A 您的專案名稱 beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```
隨後進入 Unfold 後台，您就可以看到 Crontabs 與 Periodic tasks 的漂亮管理介面，並直接設定 Linux 標準的 * * * * * 排程。

------------------------------
## 方法二：使用 django-crontab（適合輕量級專案、直接依賴 Linux Cron）
如果您不需要漂亮的後台管理介面，只想單純透過 Python 程式碼把 Django 的任務綁定到 Linux 系統內建的 crontab 服務，可以使用此輕量方法。 [1] 
## 1. 安裝套件
```python
pip install django-crontab
```
## 2. 修改 settings.py 配置
```python
INSTALLED_APPS = [
    # ...
    "django_crontab",
]
# 設定您的 Crontab 排程任務CRONJOBS = [
    # 格式：('分 時 日 月 週', '要執行的 python 函式路徑')
    # 例如：每小時的第 0 分鐘執行一次 my_app/cron.py 裡的 my_scheduled_job 函式
    ('0 * * * *', 'my_app.cron.my_scheduled_job'),
    
    # 也可以執行自訂的 Django Management Command
    # ('*/5 * * * *', 'django.core.management.call_command', ['my_custom_command']),
]
```
## 3. 編寫任務代碼 (my_app/cron.py)
```python
def my_scheduled_job():
    # 這裡寫您要定時執行的邏輯
    print("排程任務執行成功！")
```
## 4. 將排程注入 Linux 系統
此步驟會將 settings.py 裡的配置自動寫入操作系統的 crontab 中： [1] 
```python
# 將排程新增到系統中
python manage.py crontab add
# 查看目前已由 django-crontab 管理的排程
python manage.py crontab show
# 移除排程
python manage.py crontab remove
```

------------------------------
## 💡 總結建議

* 如果您希望利用 Django Unfold 的高顏值後台 來動態監控、臨時關閉或調整排程時間，請選擇 【方法一 (Celery Beat)】。 [2] 
* 如果您只是想寫死排程，不打算在後台動過它，且伺服器架設在 Linux 系統上，選擇 【方法二 (django-crontab)】 速度最快、配置最輕量。

如果您決定使用 Celery Beat，需要我為您提供完整的 celery.py 初始化程式碼設定嗎？

[1] [https://carsonwah.github.io](https://carsonwah.github.io/django-cron-jobs.html)
[2] [https://tw.pycon.org](https://tw.pycon.org/2017/zh-hant/events/talk/314386410792550475/)
