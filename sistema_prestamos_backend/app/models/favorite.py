from datetime import datetime
from . import db

class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mongo_product_id = db.Column(db.String(24), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)