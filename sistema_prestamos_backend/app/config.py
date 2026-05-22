import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY no configurada en variables de entorno")

    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL no configurada en variables de entorno")

    MONGO_URI = os.environ.get('MONGO_URI')
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI no configurada en variables de entorno")

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {
            "sslmode": "require"
        }
    }

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = 86400