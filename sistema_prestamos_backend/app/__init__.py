from flask import Flask
from .config import Config
from app.models import db
from pymongo import MongoClient

# ==================================
# VARIABLES GLOBALES MONGODB
# ==================================
mongo_client = None
mongo_db = None


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    # ==================================
    # INICIALIZAR POSTGRESQL
    # ==================================
    db.init_app(app)

    # ==================================
    # INICIALIZAR MONGODB
    # ==================================
    global mongo_client, mongo_db

    try:

        mongo_client = MongoClient(
            app.config['MONGO_URI'],
            serverSelectionTimeoutMS=5000
        )

        # Obtener base de datos automáticamente
        mongo_db = mongo_client.get_default_database()

        # Probar conexión
        mongo_client.admin.command('ping')

        print("✅ MongoDB conectado correctamente")

    except Exception as e:

        print("❌ Error conectando MongoDB:")
        print(e)

    with app.app_context():

        # ==================================
        # IMPORTAR BLUEPRINTS
        # ==================================
        from .routes.auth_routes import auth_bp
        from .routes.product_routes import product_bp
        from .routes.favorite_routes import favorite_bp
        from .routes.invoice_routes import invoice_bp
        from .routes.location_routes import location_bp
        from .routes.user_role_routes import user_role_bp
        from .routes.user_routes import user_bp

        # ==================================
        # REGISTRAR BLUEPRINTS
        # ==================================
        app.register_blueprint(
            auth_bp,
            url_prefix='/api/auth'
        )

        app.register_blueprint(
            product_bp,
            url_prefix='/api'
        )

        app.register_blueprint(
            favorite_bp,
            url_prefix='/api'
        )

        app.register_blueprint(
            invoice_bp,
            url_prefix='/api'
        )

        app.register_blueprint(
            location_bp,
            url_prefix='/api'
        )

        app.register_blueprint(
            user_role_bp,
            url_prefix='/api'
        )

        app.register_blueprint(
            user_bp,
            url_prefix='/api'
        )

        # ==================================
        # CREAR TABLAS SQL
        # ==================================
        db.create_all()

        # ==================================
        # MOSTRAR RUTAS
        # ==================================
        print(app.url_map)

    return app