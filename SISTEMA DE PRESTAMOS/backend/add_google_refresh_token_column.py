"""
Migracion UNICA: agrega la columna 'google_refresh_token' a la tabla
'users' si no existe.

Por que: se agrego el campo al modelo User (app/models/user.py) pero la
tabla ya existia en la BD, y db.create_all() NO altera tablas existentes,
asi que las consultas fallaban con "column users.google_refresh_token
does not exist".

Uso:
    cd backend
    python add_google_refresh_token_column.py
"""
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', '.env'))

from app import create_app, db
from sqlalchemy import inspect, text

app = create_app()

with app.app_context():
    insp = inspect(db.engine)
    cols = {c['name'] for c in insp.get_columns('users')}
    if 'google_refresh_token' in cols:
        print("[OK] La columna 'google_refresh_token' ya existe.")
    else:
        with db.engine.begin() as conn:
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN google_refresh_token TEXT"
            ))
        print("[OK] Columna 'google_refresh_token' agregada a 'users'.")

    # Refrescar metadatos para que SQLAlchemy reconozca la columna
    db.metadata.reflect(bind=db.engine)
    print("[OK] Metadatos reflejados.")
