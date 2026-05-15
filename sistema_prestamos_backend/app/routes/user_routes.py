from flask import Blueprint, request, jsonify
from app.models.user import User
from app import db

user_bp = Blueprint('users', __name__)

# CREAR USUARIO
@user_bp.route('/users', methods=['POST'])
def create_user():

    data = request.get_json()

    try:

        # VALIDAR EMAIL ÚNICO
        existing_user = User.query.filter_by(
            email=data['email']
        ).first()

        if existing_user:
            return jsonify({
                "error": "El email ya está registrado"
            }), 400

        user = User(
            full_name=data['full_name'],
            email=data['email'],
            phone=data.get('phone')
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            "message": "Usuario creado",
            "id": user.id
        }), 201

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400


# LISTAR USUARIOS
@user_bp.route('/users', methods=['GET'])
def get_users():

    users = User.query.all()

    result = []

    for user in users:
        result.append({
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "reputation_score": float(user.reputation_score),
            "created_at": user.created_at
        })

    return jsonify(result), 200


# OBTENER USUARIO
@user_bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):

    user = User.query.get_or_404(id)

    return jsonify({
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "reputation_score": float(user.reputation_score)
    }), 200


# ACTUALIZAR USUARIO
@user_bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):

    user = User.query.get_or_404(id)

    data = request.get_json()

    try:

        if 'email' in data:

            existing_user = User.query.filter_by(
                email=data['email']
            ).first()

            if existing_user and existing_user.id != id:
                return jsonify({
                    "error": "El email ya está en uso"
                }), 400

        user.full_name = data.get(
            'full_name',
            user.full_name
        )

        user.email = data.get(
            'email',
            user.email
        )

        user.phone = data.get(
            'phone',
            user.phone
        )

        db.session.commit()

        return jsonify({
            "message": "Usuario actualizado"
        }), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400


# ELIMINAR USUARIO
@user_bp.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):

    user = User.query.get_or_404(id)

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "message": "Usuario eliminado"
    }), 200