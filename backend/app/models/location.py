from datetime import datetime
from . import db

class Location(db.Model):
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    location_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Numeric(10, 8))
    longitude = db.Column(db.Numeric(11, 8))
    city = db.Column(db.String(100))
    reference = db.Column(db.Text)
    is_meeting_point = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)