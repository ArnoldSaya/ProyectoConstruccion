from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.models.review import Review
from app.models.reservation import Reservation
from app.models.user import User
from app import db
from app.utils import validate_required, paginate, error_response

review_bp = Blueprint('reviews', __name__)


@review_bp.route('/reviews', methods=['POST'])
@jwt_required()
def create_review():
    data = request.get_json()
    if not data:
        return error_response("Datos JSON requeridos")

    err = validate_required(data, ['reservation_id', 'reviewer_id', 'reviewed_user_id', 'rating'])
    if err:
        return jsonify(err), 400

    try:
        reservation = Reservation.query.get(data['reservation_id'])
        if not reservation:
            return error_response("Reserva no encontrada", 404)

        reviewer = User.query.get(data['reviewer_id'])
        if not reviewer:
            return error_response("Reviewer no encontrado", 404)

        reviewed = User.query.get(data['reviewed_user_id'])
        if not reviewed:
            return error_response("Usuario evaluado no encontrado", 404)

        rating = int(data['rating'])
        if rating < 1 or rating > 5:
            return error_response("La calificacion debe ser entre 1 y 5")

        review = Review(
            reservation_id=data['reservation_id'],
            reviewer_id=data['reviewer_id'],
            reviewed_user_id=data['reviewed_user_id'],
            rating=rating,
            comment=data.get('comment'),
            mongo_review_id=data.get('mongo_review_id')
        )
        db.session.add(review)
        db.session.commit()

        return jsonify({"message": "Resena creada", "id": review.id}), 201

    except Exception as e:
        return error_response(str(e), 400)


@review_bp.route('/reviews', methods=['GET'])
def get_reviews():
    result = paginate(Review.query.order_by(Review.created_at.desc()))
    items = []
    for r in result["items"]:
        items.append({
            "id": r.id,
            "reservation_id": r.reservation_id,
            "reviewer_id": r.reviewer_id,
            "reviewed_user_id": r.reviewed_user_id,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
    return jsonify({"data": items, "page": result["page"], "per_page": result["per_page"],
                    "total": result["total"], "pages": result["pages"]}), 200


@review_bp.route('/reviews/user/<int:user_id>', methods=['GET'])
def get_user_reviews(user_id):
    result = paginate(Review.query.filter_by(reviewed_user_id=user_id).order_by(Review.created_at.desc()))
    items = []
    for r in result["items"]:
        items.append({
            "id": r.id,
            "reservation_id": r.reservation_id,
            "reviewer_id": r.reviewer_id,
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
    return jsonify({"data": items, "page": result["page"], "per_page": result["per_page"],
                    "total": result["total"], "pages": result["pages"]}), 200


@review_bp.route('/reviews/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_review(id):
    review = Review.query.get_or_404(id)
    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Resena eliminada"}), 200
