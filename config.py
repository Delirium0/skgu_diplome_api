from starlette.config import Config

config = Config(".env")

DB_HOST = config("DB_HOST")
DB_PORT = config("DB_PORT")
DB_NAME = config("DB_NAME")
DB_USER = config("DB_USER")
DB_PASS = config("DB_PASS")
PASSWORD = config("PASSWORD")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DEBUG = False
API_TOKEN = config("API_TOKEN")
LANG_MESSAGES = config("LANG_MESSAGES")
TELEGRAM_ADMIN_ID = int(config("TELEGRAM_ADMIN_ID"))
REFERRER_PRIZE = float(config("REFERRER_PRIZE"))

chats = config("CHATS", default="").strip()

chat_links = chats.split(",") if chats else []
# config.py

RABBITMQ_URL = config("RABBITMQ_URL")
TEST = config("TEST")
TEST_MODE = config("TEST_MODE")
CHANNEL_NOTIFICATION_ID = int(config("CHANNEL_NOTIFICATION_ID"))
ID_ADMIN = str(config('ID_ADMIN'))
ERROR_BOT_TOKEN = config('ERROR_BOT_TOKEN')
EDIT_MESSAGE_BOT = str(config('EDIT_MESSAGE_BOT'))
