from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson import ObjectId

from app.models.favorite import Favorite
from app.models.user import User
from app import db, mongo_db
from app.utils import validate_required, paginate, error_response

favorite_bp = Blueprint('favorites', __name__)


@favorite_bp.route('/favorites', methods=['POST'])
@jwt_required()
def add_favorite():
    data = request.get_json()
    if not data:
        return error_response("Datos JSON requeridos")

    err = validate_required(data, ['user_id', 'mongo_product_id'])
    if err:
        return jsonify(err), 400

    try:
        user = User.query.get(data['user_id'])
        if not user:
            return error_response("Usuario no encontrado", 404)

        product = mongo_db.products.find_one({"_id": ObjectId(data['mongo_product_id'])})
        if not product:
            return error_response("Producto no encontrado", 404)

        existing = Favorite.query.filter_by(user_id=data['user_id'], mongo_product_id=data['mongo_product_id']).first()
        if existing:
            return error_response("Producto ya agregado a favoritos", 400)

        favorite = Favorite(user_id=data['user_id'], mongo_product_id=data['mongo_product_id'])
        db.session.add(favorite)
        db.session.commit()

        return jsonify({"message": "Favorito agregado", "id": favorite.id}), 201

    except Exception as e:
        return error_response(str(e), 400)


@favorite_bp.route('/favorites', methods=['GET'])
def get_favorites():
    result = paginate(Favorite.query.order_by(Favorite.created_at.desc()))
    items = []
    for f in result["items"]:
        items.append({
            "id": f.id,
            "user_id": f.user_id,
            "mongo_product_id": f.mongo_product_id,
            "created_at": f.created_at.isoformat() if f.created_at else None
        })
    return jsonify({"data": items, "page": result["page"], "per_page": result["per_page"],
                    "total": result["total"], "pages": result["pages"]}), 200


@favorite_bp.route('/favorites/user/<int:user_id>', methods=['GET'])
def get_user_favorites(user_id):
    result = paginate(Favorite.query.filter_by(user_id=user_id).order_by(Favorite.created_at.desc()))
    items = []
    for f in result["items"]:
        items.append({
            "id": f.id,
            "mongo_product_id": f.mongo_product_id,
            "created_at": f.created_at.isoformat() if f.created_at else None
        })
    return jsonify({"data": items, "page": result["page"], "per_page": result["per_page"],
                    "total": result["total"], "pages": result["pages"]}), 200


@favorite_bp.route('/favorites/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_favorite(id):
    favorite = Favorite.query.get_or_404(id)
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorito eliminado"}), 200
