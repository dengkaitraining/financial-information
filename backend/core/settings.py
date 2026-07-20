# ==============================================================================
# Django 5.2 核心設定檔 (backend/core/settings.py)
# 說明：設定 MariaDB 多資料庫 (user_stock_db, db_employee)、Redis 快取、Unfold 後台與 employees 模組
# ==============================================================================

import os
from pathlib import Path

# 專案基礎路徑
BASE_DIR = Path(__file__).resolve().parent.parent

# 安全與除錯設定
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-default-key')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,web').split(',')

# ------------------------------------------------------------------------------
# 1. 應用程式清單 (INSTALLED_APPS)
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    # Django Unfold 美觀後台 UI 套件 (必須置於 django.contrib.admin 之前)
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',

    # Django 內建模組
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 本地專案應用模組
    'core',
    'employees',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ------------------------------------------------------------------------------
# 2. 多資料庫與連線帳密設定 (Multi-Database & Multi-User Management)
# ------------------------------------------------------------------------------
DATABASES = {
    # 主要資料庫 (user_stock_db / user_stock 帳號)
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'user_stock_db'),
        'USER': os.environ.get('DB_USER', 'user_stock'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'user_stock_pass'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    },
    # 員工資料庫 (db_employee / user_employee 帳號)
    'employee_db': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('EMPLOYEE_DB_NAME', 'db_employee'),
        'USER': os.environ.get('EMPLOYEE_DB_USER', 'user_employee'),
        'PASSWORD': os.environ.get('EMPLOYEE_DB_PASSWORD', 'user_employee_pass'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# 多資料庫路由轉接器 (Database Router)
DATABASE_ROUTERS = ['core.db_router.PrimaryEmployeeRouter']

# ------------------------------------------------------------------------------
# 3. Redis 快取與 Session 機制 (Redis 8.8)
# ------------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{os.environ.get('REDIS_HOST', 'redis')}:{os.environ.get('REDIS_PORT', '6379')}/1",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# 密碼驗證
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 語系與時區
LANGUAGE_CODE = 'zh-hant'
TIME_ZONE = 'Asia/Taipei'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ------------------------------------------------------------------------------
# 4. Django Unfold 美觀後台樣式設定
# ------------------------------------------------------------------------------
UNFOLD = {
    "SITE_TITLE": "Django + Vue 資訊系統管理後台",
    "SITE_HEADER": "Django 5.2 系統管理儀表板",
    "SITE_URL": "/tech-stack/",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
    },
}
