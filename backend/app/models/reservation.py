from datetime import datetime
from . import db

class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    renter_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mongo_product_id = db.Column(db.String(24), nullable=False)
    pickup_location_id = db.Column(db.Integer, db.ForeignKey('locations.id'))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con pagos
    payment = db.relationship('Payment', backref='reservation', uselist=False)