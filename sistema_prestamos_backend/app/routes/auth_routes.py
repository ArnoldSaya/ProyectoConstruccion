from flask import Blueprint, request, jsonify
from app.models import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    new_user = User(
        full_name=data['full_name'],
        email=data['email'],
        phone=data.get('phone')
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Usuario registrado con éxito"}), 201