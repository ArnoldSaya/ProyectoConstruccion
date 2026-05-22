from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.models.point import Point
from app.models.user import User
from app import db
from app.utils import validate_required, paginate, error_response

point_bp = Blueprint('points', __name__)


@point_bp.route('/points', methods=['POST'])
@jwt_required()
def add_points():
    data = request.get_json()
    if not data:
        return error_response("Datos JSON requeridos")

    err = validate_required(data, ['user_id', 'points_earned'])
    if err:
        return jsonify(err), 400

    try:
        user = User.query.get(data['user_id'])
        if not user:
            return error_response("Usuario no encontrado", 404)

        point = Point(
            user_id=data['user_id'],
            points_earned=data['points_earned'],
            reason=data.get('reason')
        )
        db.session.add(point)
        db.session.commit()

        return jsonify({"message": "Puntos agregados", "id": point.id}), 201

    except Exception as e:
        return error_response(str(e), 400)


@point_bp.route('/points', methods=['GET'])
def get_points():
    result = paginate(Point.query.order_by(Point.created_at.desc()))
    items = []
    for p in result["items"]:
        items.append({
            "id": p.id,
            "user_id": p.user_id,
            "points_earned": p.points_earned,
            "reason": p.reason,
            "created_at": p.created_at.isoformat() if p.created_at else None
        })
    return jsonify({"data": items, "page": result["page"], "per_page": result["per_page"],
                    "total": result["total"], "pages": result["pages"]}), 200


@point_bp.route('/points/user/<int:user_id>', methods=['GET'])
def get_user_points(user_id):
    result = paginate(Point.query.filter_by(user_id=user_id).order_by(Point.created_at.desc()))
    items = []
    for p in result["items"]:
        items.append({
            "id": p.id,
            "points_earned": p.points_earned,
            "reason": p.reason,
            "created_at": p.created_at.isoformat() if p.created_at else None
        })

    total_points = db.session.query(db.func.sum(Point.points_earned)).filter_by(user_id=user_id).scalar() or 0

    return jsonify({
        "data": items,
        "total_points": total_points,
        "page": result["page"],
        "per_page": result["per_page"],
        "total": result["total"],
        "pages": result["pages"]
    }), 200


@point_bp.route('/points/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_point(id):
    point = Point.query.get_or_404(id)
    db.session.delete(point)
    db.session.commit()
    return jsonify({"message": "Puntos eliminados"}), 200
