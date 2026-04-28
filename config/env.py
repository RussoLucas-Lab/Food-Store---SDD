import os
from dotenv import load_dotenv
from pathlib import Path

# Carga variables de entorno desde el .env en la raíz del proyecto
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env', override=True)

class Settings:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_USER = os.getenv('DB_USER', '')
    DB_PASS = os.getenv('DB_PASS', '')
    DB_NAME = os.getenv('DB_NAME', '')
    ENV = os.getenv('ENV', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY', '')

# Uso:
# from config.env import Settings
# host = Settings.DB_HOST
