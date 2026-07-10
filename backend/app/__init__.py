import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix   # <-- NUEVO
from .config import Config
from app.models import db
from app.oauth import init_oauth
from flask_jwt_extended import JWTManager
from pymongo import MongoClient

# ==================================
# VARIABLES GLOBALES MONGODB
# ==================================
mongo_client = None
mongo_db = None


def create_app():

    app = Flask(__name__)
    app.config.from_object(Config)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    # Asegurar que exista la carpeta de subida de imagenes de productos
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ==================================
    # CORS (permite peticiones del frontend Vue en otro origen)
    # Cuando frontend y backend comparten dominio se agrega tambien
    # la URL del backend como origen valido (same-origin en Render).
    # ==================================
    allowed_origins = list({app.config['FRONTEND_URL'], app.config['BACKEND_URL']})
    CORS(
        app,
        supports_credentials=True,
        origins=allowed_origins
    )

    # ==================================
    # INICIALIZAR JWT
    # ==================================
    JWTManager(app)

    # ==================================
    # INICIALIZAR POSTGRESQL
    # ==================================
    db.init_app(app)

    # ==================================
    # INICIALIZAR GOOGLE OAUTH
    # ==================================
    init_oauth(app)

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
        from .routes.google_auth_routes import google_auth_bp
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
        app.register_blueprint(google_auth_bp, url_prefix='/api/auth')
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
        # CREAR TABLAS SI NO EXISTEN
        # ==================================
        db.create_all()
        print("[OK] Tablas de PostgreSQL creadas/verificadas")

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
        # INDICE UNICO EN CATEGORIAS (MongoDB) - case-insensitive
        # ==================================
        try:
            mongo_db.categories.drop_index("name_cat_1")
        except Exception:
            pass
        try:
            mongo_db.categories.create_index(
                "name_cat",
                unique=True,
                background=True,
                collation={"locale": "es", "strength": 2}
            )
        except Exception as e:
            print("[INFO] Indice MongoDB (no critico):", e)

        # ==================================
        # MOSTRAR RUTAS
        # ==================================
        print(app.url_map)

        # ==================================
        # SPA FALLBACK: sirve el index.html de Vue para cualquier
        # ruta que no sea /api/** ni /static/**.
        # Esto permite que Vue Router maneje rutas como /oauth-callback,
        # /login, /perfil, etc. cuando frontend y backend comparten dominio.
        # ==================================
        spa_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'dist')

        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def serve_spa(path):
            """Sirve el SPA de Vue. Rutas /api/ y /static/ son manejadas antes por Flask."""
            # Si existe el archivo exacto en dist, servirlo (assets JS/CSS/img)
            requested = os.path.join(spa_dist, path)
            if path and os.path.isfile(requested):
                return send_from_directory(spa_dist, path)
            # Para cualquier otra ruta (incluyendo /oauth-callback), devolver index.html
            index = os.path.join(spa_dist, 'index.html')
            if os.path.isfile(index):
                return send_from_directory(spa_dist, 'index.html')
            # Si aun no se ha hecho el build del frontend, mensaje claro
            return '<h2>Frontend no encontrado. Ejecuta: cd frontend && npm run build</h2>', 404

    return app
