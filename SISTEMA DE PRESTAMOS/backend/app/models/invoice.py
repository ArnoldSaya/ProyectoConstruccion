from datetime import datetime
from . import db

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    platform_fee = db.Column(db.Numeric(10, 2), nullable=False)
    owner_earnings = db.Column(db.Numeric(10, 2), nullable=False)
    taxes = db.Column(db.Numeric(10, 2), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    invoice_code = db.Column(db.String(100), unique=True, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)