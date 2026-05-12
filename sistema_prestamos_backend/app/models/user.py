from datetime import datetime
from . import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    reputation_score = db.Column(db.Numeric(3, 2), default=5.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones principales
    reservations = db.relationship('Reservation', backref='renter', lazy=True)
    locations = db.relationship('Location', backref='user', lazy=True)