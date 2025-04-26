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


# config.py

RABBITMQ_URL = config("RABBITMQ_URL")
TEST_MODE = config("TEST_MODE")
JWT_SECRET_KEY = config('JWT_SECRET_KEY')
MODE = config('MODE')
