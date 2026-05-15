import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    # ==================================
    # CLAVE SECRETA
    # ==================================
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta'

    # ==================================
    # POSTGRESQL
    # ==================================
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SSL PARA RENDER / RAILWAY / NUBE
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {
            "sslmode": "require"
        }
    }

    # ==================================
    # MONGODB
    # ==================================
    MONGO_URI = os.environ.get('MONGO_URI')