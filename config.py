from dotenv import load_dotenv
import os

load_dotenv()  # Загружает переменные из .env

BOT_TOKEN = os.getenv('BOT_TOKEN', '')
ADMIN_ID = int(os.getenv('ADMIN_ID', 5717967396))  # Замените на свой Telegram ID
TG_PROXY = os.getenv('TG_PROXY', '').strip()
TG_PROXY_URL = os.getenv('TG_PROXY_URL', '').strip()
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 5432))
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_NAME = os.getenv('DB_NAME', 'coffee_rent')
