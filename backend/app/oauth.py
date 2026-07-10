import os
from cryptography.fernet import Fernet
from authlib.integrations.flask_client import OAuth

oauth = OAuth()


def _fernet():
    key = os.environ.get('ENCRYPTION_KEY')
    if not key:
        raise RuntimeError("ENCRYPTION_KEY no configurada en variables de entorno")
    return Fernet(key.encode() if len(key) == 44 else Fernet.generate_key())


def encrypt_token(token: str) -> str:
    return _fernet().encrypt(token.encode()).decode()


def decrypt_token(token: str) -> str:
    return _fernet().decrypt(token.encode()).decode()


def init_oauth(app):
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
        client_kwargs={
            'scope': 'openid email profile https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/calendar.events https://www.googleapis.com/auth/gmail.send',
            'access_type': 'offline',
            'prompt': 'consent'
        }
    )
