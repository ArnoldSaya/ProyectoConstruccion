from flask import Flask
from flask_jwt_extended import JWTManager
from .config import Config
from app.models import db
from pymongo import MongoClient

# ==================================
# VARIABLES GLOBALES MONGODB
# ==================================
mongo_client = None
mongo_db = None

jwt = JWTManager()


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    # ==================================
    # INICIALIZAR POSTGRESQL
    # ==================================
    db.init_app(app)

    # ==================================
    # INICIALIZAR JWT
    # ==================================
    jwt.init_app(app)

    # ==================================
    # INICIALIZAR MONGODB
    # ==================================
    global mongo_client, mongo_db

    try:
        mongo_client = MongoClient(
            app.config['MONGO_URI'],
            serverSelectionTimeoutMS=5000
        )
        mongo_db = mongo_client.get_default_database()
        mongo_client.admin.command('ping')
        print("[OK] MongoDB conectado correctamente")
    except Exception as e:
        print("[ERROR] conectando MongoDB:")
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
        from .routes.reservation_routes import reservation_bp
        from .routes.payment_routes import payment_bp
        from .routes.review_routes import review_bp
        from .routes.point_routes import point_bp

        # ==================================
        # REGISTRAR BLUEPRINTS
        # ==================================
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(product_bp, url_prefix='/api')
        app.register_blueprint(favorite_bp, url_prefix='/api')
        app.register_blueprint(invoice_bp, url_prefix='/api')
        app.register_blueprint(location_bp, url_prefix='/api')
        app.register_blueprint(user_role_bp, url_prefix='/api')
        app.register_blueprint(user_bp, url_prefix='/api')
        app.register_blueprint(reservation_bp, url_prefix='/api')
        app.register_blueprint(payment_bp, url_prefix='/api')
        app.register_blueprint(review_bp, url_prefix='/api')
        app.register_blueprint(point_bp, url_prefix='/api')

        # ==================================
        # SEMILLA DE ROLES
        # ==================================
        try:
            from app.models.role import Role
            from app.models.user_role import UserRole
            roles_existentes = {r.role_name: r for r in Role.query.all()}
            for nombre in ['cliente', 'rentador']:
                if nombre not in roles_existentes:
                    r = Role(role_name=nombre)
                    db.session.add(r)
                    db.session.flush()
                    print(f"[OK] Rol '{nombre}' creado")
            db.session.commit()
        except Exception as e:
            print("[INFO] Semilla de roles:", e)

        # ==================================
        # INDICE UNICO EN CATEGORIAS (MongoDB)
        # ==================================
        try:
            mongo_db.categories.create_index("name_cat", unique=True)
        except Exception as e:
            print("[INFO] Indice MongoDB:", e)

        # ==================================
        # MOSTRAR RUTAS
        # ==================================
        print(app.url_map)

    return app