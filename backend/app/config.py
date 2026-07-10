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

    # Forzar SSL solo si no es localhost (necesario para Render)
    if 'sslmode' not in DATABASE_URL and 'localhost' not in DATABASE_URL and '127.0.0.1' not in DATABASE_URL:
        sep = '&' if '?' in DATABASE_URL else '?'
        DATABASE_URL = f"{DATABASE_URL}{sep}sslmode=require"

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # ==================================
    # GOOGLE OAUTH 2.0
    # ==================================
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = os.environ.get(
        'GOOGLE_DISCOVERY_URL',
        'https://accounts.google.com/.well-known/openid-configuration'
    )

    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise RuntimeError(
            "GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET no configurados en variables de entorno"
        )

    # Clave para encriptar tokens sensibles (refresh_token de Google) en BD.
    # Genera una con:  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')

    # ==================================
    # JWT (ACCESS + REFRESH) - OAuth 2.0 Bearer tokens
    # ==================================
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 900))      # 15 min
    JWT_REFRESH_TOKEN_EXPIRES = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000))  # 30 dias

    # ==================================
    # URLS DE BACKEND Y FRONTEND
    # ==================================
    # URL publica y FIJA de este backend. Se usa para construir el
    # redirect_uri que se envia a Google, para que sea siempre exactamente
    # igual al que registraste en Google Cloud Console (evita el error
    # "redirect_uri_mismatch"). Debe incluir esquema y puerto, sin barra final.
    BACKEND_URL = os.environ.get('BACKEND_URL', 'http://127.0.0.1:5000').rstrip('/')

    # A donde se redirige al usuario despues de un login exitoso con Google.
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173').rstrip('/')

    # ==================================
    # SESIONES
    # ==================================
    SESSION_COOKIE_NAME = 'session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False     # Poner True en produccion (requiere HTTPS)

    # ==================================
    # SUBIDA DE IMAGENES DE PRODUCTOS
    # ==================================
    # Carpeta fisica donde se guardan las fotos subidas. Va dentro de
    # app/static/ para que Flask las sirva automaticamente en /static/...
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'static', 'uploads', 'products'
    )
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # Limite de 5 MB por imagen
