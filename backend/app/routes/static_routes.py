import os
from flask import send_from_directory, Blueprint

static_bp = Blueprint('static_bp', __name__)

# Carpeta del build de produccion del frontend (npm run build -> frontend/dist).
# Se puede sobreescribir con FRONTEND_DIST en las variables de entorno (Render).
_DEFAULT_DIST = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', '..', '..', 'frontend', 'dist'
)
FRONTEND_DIST = os.environ.get('FRONTEND_DIST', _DEFAULT_DIST)


@static_bp.route('/', defaults={'path': ''}, methods=['GET'])
@static_bp.route('/<path:path>', methods=['GET'])
def serve_spa(path):
    # No interceptar rutas de la API: que sigan dando 404 real si no existen.
    if path.startswith('api/'):
        return {'error': 'not found'}, 404

    # Archivo estatico real del build (js, css, imagenes, favicon, etc.)
    file_path = os.path.join(FRONTEND_DIST, path)
    if path and os.path.isfile(file_path):
        return send_from_directory(FRONTEND_DIST, path)

    # Cualquier otra ruta (ej. /oauth-callback, /login) -> index.html (SPA fallback)
    index_path = os.path.join(FRONTEND_DIST, 'index.html')
    if os.path.isfile(index_path):
        return send_from_directory(FRONTEND_DIST, 'index.html')

    return {'error': 'Frontend no construido. Ejecuta npm run build en frontend/'
                     ' o define FRONTEND_DIST.'}, 404
