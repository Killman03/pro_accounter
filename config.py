from dotenv import load_dotenv
import os

load_dotenv()  # Загружает переменные из .env

BOT_TOKEN = os.getenv('BOT_TOKEN', '')
ADMIN_ID = int(os.getenv('ADMIN_ID', 5717967396))  # Замените на свой Telegram ID
DEV_LOG_TELEGRAM_ID = int(os.getenv('DEV_LOG_TELEGRAM_ID', 0))
TELEGRAM_PROXY_URL = os.getenv('TELEGRAM_PROXY_URL', '').strip()
STARTUP_MAX_TELEGRAM_LATENCY_MS = int(os.getenv('STARTUP_MAX_TELEGRAM_LATENCY_MS', 2000))
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 5432))
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_NAME = os.getenv('DB_NAME', 'coffee_rent')
META_CAPI_ACCESS_TOKEN = os.getenv('META_CAPI_ACCESS_TOKEN', '').strip()
META_CAPI_DATASET_ID = os.getenv('META_CAPI_DATASET_ID', '').strip()
META_CAPI_API_VERSION = os.getenv('META_CAPI_API_VERSION', 'v25.0').strip() or 'v25.0'
META_CAPI_LEAD_EVENT_SOURCE = os.getenv('META_CAPI_LEAD_EVENT_SOURCE', 'Telegram Bot CRM').strip()
META_CAPI_TEST_EVENT_CODE = os.getenv('META_CAPI_TEST_EVENT_CODE', '').strip()
META_CAPI_CURRENCY = os.getenv('META_CAPI_CURRENCY', 'KGS').strip() or 'KGS'
