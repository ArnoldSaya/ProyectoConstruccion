from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.models import db
from app.utils import validate_required, paginate, error_response

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    data = request.get_json()
    if not data:
        return error_response("Datos JSON requeridos")

    err = validate_required(data, ['full_name', 'email', 'password'])
    if err:
        return jsonify(err), 400

    try:
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return error_response("El email ya esta registrado", 400)

        user = User(
            full_name=data['full_name'],
            email=data['email'],
            phone=data.get('phone')
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()

        rol_cliente = Role.query.filter_by(role_name='cliente').first()
        if rol_cliente:
            ur = UserRole(user_id=user.id, role_id=rol_cliente.id)
            db.session.add(ur)

        db.session.commit()

        return jsonify({"message": "Usuario creado", "id": user.id}), 201

    except Exception as e:
        return error_response(str(e), 400)


@user_bp.route('/users', methods=['GET'])
def get_users():
    result = paginate(User.query.order_by(User.created_at.desc()))
    items = [u.to_dict() for u in result["items"]]
    return jsonify({"data": items, "page": result["page"], "per_page": result["per_page"],
                    "total": result["total"], "pages": result["pages"]}), 200


@user_bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict()), 200


@user_bp.route('/users/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return error_response("Datos JSON requeridos")

    try:
        if 'email' in data:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != id:
                return error_response("El email ya esta en uso", 400)
            user.email = data['email']

        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'password' in data:
            user.set_password(data['password'])

        db.session.commit()
        return jsonify({"message": "Usuario actualizado"}), 200

    except Exception as e:
        return error_response(str(e), 400)


@user_bp.route('/users/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Usuario eliminado"}), 200
