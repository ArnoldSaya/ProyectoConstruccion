"""
Helper para consumir las Google APIs (Drive, Calendar, Gmail) en nombre del
usuario, usando el refresh_token de Google que guardamos en el modelo User.

Requiere las dependencias:
    pip install google-auth google-api-python-client

El backend actua como cliente confidencial de OAuth 2.0: con el
refresh_token (encriptado en BD) obtiene un nuevo access_token bajo demanda
y llama a la API correspondiente sin que el usuario tenga que re-loguearse.
"""
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from app.models.user import User


def _build_credentials(user: User):
    refresh_token = user.get_google_refresh_token()
    if not refresh_token:
        raise RuntimeError(
            "El usuario no tiene refresh_token de Google. Debe volver a "
            "iniciar sesion con Google (consentimiento)."
        )
    return Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=_client_id(),
        client_secret=_client_secret(),
        scopes=[
            "openid",
            "email",
            "profile",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/calendar.events",
            "https://www.googleapis.com/auth/gmail.send",
        ],
    )


def _client_id():
    from flask import current_app
    return current_app.config["GOOGLE_CLIENT_ID"]


def _client_secret():
    from flask import current_app
    return current_app.config["GOOGLE_CLIENT_SECRET"]


def get_drive_service(user: User):
    creds = _build_credentials(user)
    creds.refresh(Request())
    return build("drive", "v3", credentials=creds)


def get_calendar_service(user: User):
    creds = _build_credentials(user)
    creds.refresh(Request())
    return build("calendar", "v3", credentials=creds)


def get_gmail_service(user: User):
    creds = _build_credentials(user)
    creds.refresh(Request())
    return build("gmail", "v1", credentials=creds)


def upload_file_to_drive(user: User, name: str, content, mime_type: str):
    """Sube un archivo a Google Drive del usuario y devuelve el file_id."""
    service = get_drive_service(user)
    file_metadata = {"name": name}
    from googleapiclient.http import MediaIoBaseUpload
    import io
    if isinstance(content, (bytes, str)):
        content = io.BytesIO(
            content.encode() if isinstance(content, str) else content
        )
    media = MediaIoBaseUpload(content, mimetype=mime_type)
    file = service.files().create(
        body=file_metadata, media_body=media, fields="id"
    ).execute()
    return file.get("id")


def upload_public_image_to_drive(user: User, name: str, content, mime_type: str):
    """
    Sube una imagen al Google Drive del usuario, la hace publica (para poder
    incrustarla en <img>) y devuelve (file_id, url_embebible).
    Requiere que el usuario tenga refresh_token de Google (login con Google).
    """
    service = get_drive_service(user)
    file_metadata = {"name": name}
    from googleapiclient.http import MediaIoBaseUpload
    import io
    if isinstance(content, (bytes, str)):
        content = io.BytesIO(
            content.encode() if isinstance(content, str) else content
        )
    media = MediaIoBaseUpload(content, mimetype=mime_type)
    file = service.files().create(
        body=file_metadata, media_body=media, fields="id"
    ).execute()
    file_id = file.get("id")

    # Hacer el archivo publico para que sea visible en <img src>
    service.permissions().create(
        body={"type": "anyone", "role": "reader"},
        fileId=file_id,
        fields="id",
    ).execute()

    url = f"https://drive.google.com/uc?export=view&id={file_id}"
    return file_id, url


def create_calendar_event(user: User, summary: str, start, end, description=None):
    """Crea un evento en el calendario principal del usuario."""
    service = get_calendar_service(user)
    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start},
        "end": {"dateTime": end},
    }
    return service.events().insert(calendarId="primary", body=event).execute()


def send_email(user: User, to: str, subject: str, body: str):
    """Envía un email usando Gmail en nombre del usuario."""
    from email.mime.text import MIMEText
    import base64
    service = get_gmail_service(user)
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return service.users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()
