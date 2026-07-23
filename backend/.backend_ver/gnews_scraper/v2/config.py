from pathlib import Path

# 專案根目錄
BASE_DIR = Path(__file__).resolve().parent

# 資料儲存目錄
NEWS_DIR = BASE_DIR / "news"
LOGS_DIR = BASE_DIR / "logs"

# 預設設定
DEFAULT_PERIOD = "4h"
DEFAULT_LANGUAGE = "zh-TW"
DEFAULT_COUNTRY = "TW"
DEFAULT_MAX_RESULTS = 100
MAX_KEYWORDS_LIMIT = 4