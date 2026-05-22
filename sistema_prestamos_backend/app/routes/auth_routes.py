from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import db
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.utils import validate_required, error_response

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return error_response("Datos JSON requeridos")

    err = validate_required(data, ['full_name', 'email', 'password'])
    if err:
        return jsonify(err), 400

    existing = User.query.filter_by(email=data['email']).first()
    if existing:
        return error_response("El email ya esta registrado", 400)

    user = User(
        full_name=data['full_name'],
        email=data['email'],
        phone=data.get('phone')
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.flush()

    # Asignar rol "cliente" automaticamente
    rol_cliente = Role.query.filter_by(role_name='cliente').first()
    if rol_cliente:
        ur = UserRole(user_id=user.id, role_id=rol_cliente.id)
        db.session.add(ur)

    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"message": "Usuario registrado", "token": token, "user": user.to_dict()}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return error_response("Datos JSON requeridos")

    err = validate_required(data, ['email', 'password'])
    if err:
        return jsonify(err), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return error_response("Credenciales invalidas", 401)

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200
