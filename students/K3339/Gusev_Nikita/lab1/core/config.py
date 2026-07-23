import os

from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_ADMIN")

# Секрет для подписи JWT — в реальном проекте храни только в .env!
JWT_SECRET = os.getenv("JWT_SECRET", "change_this_secret_in_env_file")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24  # токен живёт сутки
