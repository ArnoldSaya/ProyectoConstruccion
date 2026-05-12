from datetime import datetime
from . import db

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservations.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.String(50), default='completed')
    transaction_code = db.Column(db.String(100), unique=True)
    
    # Relación con facturas
    invoice = db.relationship('Invoice', backref='payment', uselist=False)