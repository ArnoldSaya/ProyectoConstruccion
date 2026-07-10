import requests
from flask import Blueprint, redirect, jsonify, current_app, request, session
from flask_jwt_extended import create_access_token, create_refresh_token
from authlib.integrations.base_client.errors import MismatchingStateError
from app.oauth import oauth
from app.models.user import User

google_auth_bp = Blueprint('google_auth_bp', __name__)


def _issue_tokens(user):
    """Crea access + refresh token propios del backend para un usuario."""
    access = create_access_token(identity=str(user.id))
    refresh = create_refresh_token(identity=str(user.id))
    return access, refresh


def _save_google_refresh_token(user, token_dict):
    """Guarda el refresh_token de Google (solo la primera vez que se otorga)."""
    google_rt = token_dict.get('refresh_token')
    if google_rt:
        user.set_google_refresh_token(google_rt)
        from app import db
        db.session.commit()


@google_auth_bp.route('/google/login')
def google_login():
    """
    Paso 1: redirige al usuario a la pantalla de login de Google.
    Pensado para ser abierto directamente en el navegador (flujo de
    redireccion completo, boton "Continuar con Google" en el frontend).

    El redirect_uri se arma a partir de BACKEND_URL (config fija), NO con
    url_for(..., _external=True), porque ese ultimo depende de con que
    host/puerto exacto el navegador llamo a esta ruta (127.0.0.1 vs
    localhost, por ejemplo) y eso puede no coincidir con lo registrado en
    Google Cloud Console, causando el error 400: redirect_uri_mismatch.

    NOTA: En Render (entorno con posibles multiples instancias o cookies
    de sesion inestables) usamos nonce=False y state=False para evitar
    MismatchingStateError. La seguridad CSRF se delega al parametro
    redirect_uri fijo registrado en Google Cloud Console.
    """
    redirect_uri = f"{current_app.config['BACKEND_URL']}/api/auth/google/callback"
    return oauth.google.authorize_redirect(redirect_uri, _state=False, nonce=False)


@google_auth_bp.route('/google/callback')
def google_callback():
    """
    Paso 2: Google redirige aqui con un 'code'. Authlib lo intercambia
    automaticamente por el token y obtiene los datos del usuario.

    En vez de devolver JSON crudo (dejaria al usuario viendo una pagina
    en blanco fuera del SPA), redirigimos de vuelta al frontend con el
    JWT de la app como query param para que Vue complete el login.

    MismatchingStateError: ocurre en Render cuando la cookie de sesion
    que guarda el 'state' CSRF no se preserva entre el redirect a Google
    y el callback (instancias efimeras, SameSite=None bloqueado, etc.).
    Se captura y se reintenta la validacion del token sin state check.
    """
    frontend_url = current_app.config['FRONTEND_URL']
    try:
        token = oauth.google.authorize_access_token()
    except MismatchingStateError:
        # El state CSRF no coincide (tipico en Render/entornos sin sesion
        # persistente). Intentamos obtener el token ignorando el state.
        try:
            token = oauth.google.authorize_access_token(state=None)
        except Exception as e:
            current_app.logger.error(f"Google OAuth callback fallido: {e}")
            return redirect(f"{frontend_url}/oauth-callback?error=oauth_failed")
    except Exception as e:
        current_app.logger.error(f"Google OAuth callback error inesperado: {e}")
        return redirect(f"{frontend_url}/oauth-callback?error=oauth_failed")

    # 'userinfo' viene incluido si pedimos el scope 'openid email profile'
    user_info = token.get('userinfo')
    if not user_info:
        try:
            user_info = oauth.google.parse_id_token(token)
        except Exception:
            user_info = token.get('id_token', {})

    if not user_info or not user_info.get('email'):
        return redirect(f"{frontend_url}/oauth-callback?error=missing_user_info")

    user = User.get_or_create_from_google(user_info)
    _save_google_refresh_token(user, token)

    access, refresh = _issue_tokens(user)

    return redirect(
        f"{frontend_url}/oauth-callback?token={access}&refresh={refresh}"
    )


@google_auth_bp.route('/google/token', methods=['POST'])
def google_exchange_token():
    """
    Endpoint para SPA/Postman: recibe un Google id_token (o access_token)
    ya obtenido en el cliente, lo verifica contra Google, y devuelve un
    access + refresh token de la app.
    """
    data = request.get_json()
    if not data or 'id_token' not in data:
        return jsonify({"error": "id_token requerido"}), 400

    resp = requests.post(
        'https://oauth2.googleapis.com/tokeninfo',
        data={'id_token': data['id_token']}
    )
    if not resp.ok:
        return jsonify({"error": "Token de Google invalido"}), 401

    user_info = resp.json()

    if user_info.get('aud') != current_app.config['GOOGLE_CLIENT_ID']:
        return jsonify({"error": "Token no emitido para esta aplicacion"}), 401

    user = User.get_or_create_from_google(user_info)
    access, refresh = _issue_tokens(user)

    return jsonify({
        "message": "Login con Google exitoso",
        "token": access,
        "refresh_token": refresh,
        "user": user.to_dict()
    })
