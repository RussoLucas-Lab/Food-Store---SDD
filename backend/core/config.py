import os
from dotenv import load_dotenv
from pathlib import Path

# Carga variables de entorno desde el .env en la raíz del proyecto
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / '.env', override=True)

class Settings:
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_USER = os.getenv('DB_USER', '')
    DB_PASS = os.getenv('DB_PASS', '')
    DB_NAME = os.getenv('DB_NAME', '')

    # JWT Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 15))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 7))

    # Environment
    ENV = os.getenv('ENV', 'development')
    DEBUG = ENV == 'development'

# Uso:
# from backend.core.config import Settings
# secret = Settings.SECRET_KEY
