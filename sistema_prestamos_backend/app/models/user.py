from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(256), nullable=False)
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
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "reputation_score": float(self.reputation_score),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }