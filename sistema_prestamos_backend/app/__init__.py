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
        # Importamos los Blueprints
        from .routes.auth_routes import auth_bp
        from .routes.product_routes import product_bp # <-- Nueva línea
        
        # Registramos los Blueprints
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(product_bp, url_prefix='/api') # <-- Nueva línea

        db.create_all()

    return app