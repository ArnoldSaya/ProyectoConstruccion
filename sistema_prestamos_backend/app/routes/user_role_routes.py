from flask import Blueprint, request, jsonify
from app.models.user_role import UserRole
from app.models.user import User
from app.models.role import Role
from app import db

user_role_bp = Blueprint('user_roles', __name__)

# ASIGNAR ROL
@user_role_bp.route('/user-roles', methods=['POST'])
def assign_role():

    data = request.get_json()

    try:

        # VALIDAR USUARIO
        user = User.query.get(
            data['user_id']
        )

        if not user:
            return jsonify({
                "error": "Usuario no encontrado"
            }), 404

        # VALIDAR ROL
        role = Role.query.get(
            data['role_id']
        )

        if not role:
            return jsonify({
                "error": "Rol no encontrado"
            }), 404

        # VALIDAR DUPLICADO
        existing_role = UserRole.query.filter_by(
            user_id=data['user_id'],
            role_id=data['role_id']
        ).first()

        if existing_role:
            return jsonify({
                "error": "El usuario ya tiene este rol"
            }), 400

        user_role = UserRole(
            user_id=data['user_id'],
            role_id=data['role_id']
        )

        db.session.add(user_role)
        db.session.commit()

        return jsonify({
            "message": "Rol asignado",
            "id": user_role.id
        }), 201

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400


# LISTAR ROLES
@user_role_bp.route('/user-roles', methods=['GET'])
def get_roles():

    roles = UserRole.query.all()

    result = []

    for role in roles:
        result.append({
            "id": role.id,
            "user_id": role.user_id,
            "role_id": role.role_id,
            "assigned_at": role.assigned_at
        })

    return jsonify(result), 200


# ELIMINAR ROL
@user_role_bp.route('/user-roles/<int:id>', methods=['DELETE'])
def delete_role(id):

    role = UserRole.query.get_or_404(id)

    db.session.delete(role)
    db.session.commit()

    return jsonify({
        "message": "Rol eliminado"
    }), 200