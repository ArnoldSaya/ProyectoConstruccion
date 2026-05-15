from flask import Blueprint, request, jsonify
from bson import ObjectId

from app.models.favorite import Favorite
from app.models.user import User
from app import db, mongo_db

favorite_bp = Blueprint('favorites', __name__)

# =========================================
# AGREGAR FAVORITO
# =========================================
@favorite_bp.route('/favorites', methods=['POST'])
def add_favorite():

    data = request.get_json()

    try:

        # =========================
        # VALIDAR USUARIO
        # =========================
        user = User.query.get(data['user_id'])

        if not user:
            return jsonify({
                "error": "Usuario no encontrado"
            }), 404

        # =========================
        # VALIDAR PRODUCTO EN MONGO
        # =========================
        product = mongo_db.products.find_one({
            "_id": ObjectId(data['mongo_product_id'])
        })

        if not product:
            return jsonify({
                "error": "Producto no encontrado"
            }), 404

        # =========================
        # VALIDAR FAVORITO DUPLICADO
        # =========================
        existing_favorite = Favorite.query.filter_by(
            user_id=data['user_id'],
            mongo_product_id=data['mongo_product_id']
        ).first()

        if existing_favorite:
            return jsonify({
                "error": "Producto ya agregado a favoritos"
            }), 400

        # =========================
        # CREAR FAVORITO
        # =========================
        favorite = Favorite(
            user_id=data['user_id'],
            mongo_product_id=data['mongo_product_id']
        )

        db.session.add(favorite)
        db.session.commit()

        return jsonify({
            "message": "Favorito agregado",
            "id": favorite.id
        }), 201

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 400


# =========================================
# LISTAR FAVORITOS
# =========================================
@favorite_bp.route('/favorites', methods=['GET'])
def get_favorites():

    favorites = Favorite.query.all()

    result = []

    for favorite in favorites:

        result.append({
            "id": favorite.id,
            "user_id": favorite.user_id,
            "mongo_product_id": favorite.mongo_product_id,
            "created_at": favorite.created_at
        })

    return jsonify(result), 200


# =========================================
# FAVORITOS POR USUARIO
# =========================================
@favorite_bp.route('/favorites/user/<int:user_id>', methods=['GET'])
def get_user_favorites(user_id):

    favorites = Favorite.query.filter_by(
        user_id=user_id
    ).all()

    result = []

    for favorite in favorites:

        result.append({
            "id": favorite.id,
            "mongo_product_id": favorite.mongo_product_id,
            "created_at": favorite.created_at
        })

    return jsonify(result), 200


# =========================================
# ELIMINAR FAVORITO
# =========================================
@favorite_bp.route('/favorites/<int:id>', methods=['DELETE'])
def delete_favorite(id):

    favorite = Favorite.query.get_or_404(id)

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({
        "message": "Favorito eliminado"
    }), 200