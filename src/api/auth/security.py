from datetime import timedelta
from authx import AuthX, AuthXConfig
from config import JWT_SECRET_KEY
from passlib.context import CryptContext

config = AuthXConfig()
config.JWT_SECRET_KEY = JWT_SECRET_KEY
config.JWT_ACCESS_COOKIE_NAME = 'access_token'
config.JWT_TOKEN_LOCATION = ['cookies', 'headers']
config.JWT_COOKIE_CSRF_PROTECT = False
config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

security = AuthX(config=config)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
