import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Clave de seguridad para sesiones y tokens
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta'
    
    # URL de conexión para PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # URI de conexión para MongoDB
    MONGO_URI = os.environ.get('MONGO_URI')