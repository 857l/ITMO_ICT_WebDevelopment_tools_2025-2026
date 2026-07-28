import os

from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_ADMIN")

# Секрет для подписи JWT — в реальном проекте храни только в .env!
JWT_SECRET = os.getenv("JWT_SECRET", "change_this_secret_in_env_file")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24  # токен живёт сутки

# Адрес сервиса-парсера (отдельный контейнер, Lab3)
PARSER_SERVICE_URL = os.getenv("PARSER_SERVICE_URL", "http://parser:8001")

# Celery / Redis (Lab3, подзадача 3)
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
