from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from app.oauth import encrypt_token, decrypt_token

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))

    # password_hash ahora es opcional: los usuarios que entran por Google no tienen password
    password_hash = db.Column(db.String(256), nullable=True)

    # Datos de Google OAuth
    google_id = db.Column(db.String(64), unique=True, nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    auth_provider = db.Column(db.String(20), nullable=False, default='email')
    google_refresh_token = db.Column(db.Text, nullable=True)

    reputation_score = db.Column(db.Numeric(3, 2), default=5.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones principales
    reservations = db.relationship('Reservation', backref='renter', lazy=True, cascade='all, delete-orphan')
    locations = db.relationship('Location', backref='user', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', lazy=True, cascade='all, delete-orphan')
    points = db.relationship('Point', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def set_google_refresh_token(self, token: str):
        if token:
            self.google_refresh_token = encrypt_token(token)

    def get_google_refresh_token(self) -> str | None:
        if self.google_refresh_token:
            return decrypt_token(self.google_refresh_token)
        return None

    @classmethod
    def get_or_create_from_google(cls, google_info):
        """
        Busca un usuario por google_id o email. Si no existe, lo crea.
        google_info es el dict que devuelve Google con: sub, email, name, picture, etc.
        """
        google_id = google_info['sub']
        email = google_info.get('email')

        user = cls.query.filter_by(google_id=google_id).first()
        if user:
            return user

        # Si ya existia un usuario con ese email (registrado de otra forma), lo vincula
        user = cls.query.filter_by(email=email).first()
        if user:
            user.google_id = google_id
            user.avatar_url = google_info.get('picture')
            db.session.commit()
            return user

        # Crear usuario nuevo
        user = cls(
            full_name=google_info.get('name', email),
            email=email,
            google_id=google_id,
            avatar_url=google_info.get('picture'),
            auth_provider='google'
        )
        db.session.add(user)
        db.session.flush()  # para obtener user.id

        # Asignar rol 'cliente' por defecto (igual que en register)
        from app.models.role import Role
        from app.models.user_role import UserRole
        cliente_role = Role.query.filter_by(role_name='cliente').first()
        if cliente_role:
            db.session.add(UserRole(user_id=user.id, role_id=cliente_role.id))

        db.session.commit()
        return user

    def to_dict(self):
        from app.models.user_role import UserRole
        from app.models.role import Role
        role_rows = (
            UserRole.query.filter_by(user_id=self.id)
            .join(Role, Role.id == UserRole.role_id)
            .with_entities(Role.role_name)
            .all()
        )
        roles = [r.role_name for r in role_rows]
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "avatar_url": self.avatar_url,
            "auth_provider": self.auth_provider,
            "roles": roles,
            "reputation_score": float(self.reputation_score),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }