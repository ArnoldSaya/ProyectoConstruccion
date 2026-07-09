from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.user_role import UserRole
from app.models.user import User
from app.models.role import Role
from app import db
from app.utils import validate_required, paginate, error_response

user_role_bp = Blueprint('user_roles', __name__)


@user_role_bp.route('/user-roles', methods=['POST'])
@jwt_required()
def assign_role():
    data = request.get_json()
    if not data:
        return error_response("Datos JSON requeridos")

    err = validate_required(data, ['user_id', 'role_id'])
    if err:
        return jsonify(err), 400

    try:
        user = User.query.get(data['user_id'])
        if not user:
            return error_response("Usuario no encontrado", 404)

        role = Role.query.get(data['role_id'])
        if not role:
            return error_response("Rol no encontrado", 404)

        existing = UserRole.query.filter_by(user_id=data['user_id'], role_id=data['role_id']).first()
        if existing:
            return error_response("El usuario ya tiene este rol", 400)

        user_role = UserRole(user_id=data['user_id'], role_id=data['role_id'])
        db.session.add(user_role)
        db.session.commit()

        return jsonify({"message": "Rol asignado", "id": user_role.id}), 201

    except Exception as e:
        return error_response(str(e), 400)


@user_role_bp.route('/user-roles/self', methods=['POST'])
@jwt_required()
def assign_role_self():
    """
    Permite al usuario autenticado asignarse un rol por nombre
    (ej. 'rentador'). No requiere ser admin. Valida que el rol exista.
    """
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data:
        return error_response("Datos JSON requeridos")

    err = validate_required(data, ['role_name'])
    if err:
        return jsonify(err), 400

    role = Role.query.filter_by(role_name=data['role_name']).first()
    if not role:
        return error_response("Rol no encontrado", 404)

    existing = UserRole.query.filter_by(user_id=current_user_id, role_id=role.id).first()
    if existing:
        return error_response("El usuario ya tiene este rol", 400)

    user_role = UserRole(user_id=current_user_id, role_id=role.id)
    db.session.add(user_role)
    db.session.commit()

    return jsonify({"message": f"Rol '{role.role_name}' asignado", "id": user_role.id}), 201


@user_role_bp.route('/user-roles', methods=['GET'])
def get_roles():
    result = paginate(UserRole.query.order_by(UserRole.assigned_at.desc()))
    items = []
    for ur in result["items"]:
        items.append({
            "id": ur.id,
            "user_id": ur.user_id,
            "role_id": ur.role_id,
            "assigned_at": ur.assigned_at.isoformat() if ur.assigned_at else None
        })
    return jsonify({"data": items, "page": result["page"], "per_page": result["per_page"],
                    "total": result["total"], "pages": result["pages"]}), 200


@user_role_bp.route('/user-roles/user/<int:user_id>', methods=['GET'])
def get_user_roles(user_id):
    result = paginate(UserRole.query.filter_by(user_id=user_id).order_by(UserRole.assigned_at.desc()))
    items = []
    for ur in result["items"]:
        role = Role.query.get(ur.role_id)
        items.append({
            "id": ur.id,
            "role_id": ur.role_id,
            "role_name": role.role_name if role else None,
            "assigned_at": ur.assigned_at.isoformat() if ur.assigned_at else None
        })
    return jsonify({"data": items, "page": result["page"], "per_page": result["per_page"],
                    "total": result["total"], "pages": result["pages"]}), 200


@user_role_bp.route('/user-roles/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_role(id):
    role = UserRole.query.get_or_404(id)
    db.session.delete(role)
    db.session.commit()
    return jsonify({"message": "Rol eliminado"}), 200
