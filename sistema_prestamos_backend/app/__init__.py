from flask import Flask
from .config import Config
from app.models import db 
from pymongo import MongoClient

# Variables globales para MongoDB
mongo_client = None
mongo_db = None

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 1. Inicializar PostgreSQL
    db.init_app(app)

    # 2. Inicializar MongoDB
    global mongo_client, mongo_db
    mongo_client = MongoClient(app.config['MONGO_URI'])
    mongo_db = mongo_client.get_database() 

    with app.app_context():
        # Importar y registrar las rutas AQUÍ ADENTRO
        from .routes.auth_routes import auth_bp
        
        # Ahora 'app' sí existe en este contexto
        app.register_blueprint(auth_bp, url_prefix='/api/auth')

        # Crear tablas si no existen
        db.create_all()

    return app