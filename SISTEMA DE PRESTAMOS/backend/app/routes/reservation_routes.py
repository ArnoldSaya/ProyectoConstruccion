from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson import ObjectId

from app.models.reservation import Reservation
from app.models.user import User
from app.models.location import Location
from app import db, mongo_db
from app.utils import validate_required, paginate, error_response

reservation_bp = Blueprint('reservations', __name__)


@reservation_bp.route('/reservations', methods=['POST'])
@jwt_required()
def create_reservation():
    data = request.get_json()
    if not data:
        return error_response("Datos JSON requeridos")

    err = validate_required(data, ['renter_user_id', 'mongo_product_id', 'start_date', 'end_date', 'total_price'])
    if err:
        return jsonify(err), 400

    try:
        user = User.query.get(data['renter_user_id'])
        if not user:
            return error_response("Usuario no encontrado", 404)

        product = mongo_db.products.find_one({"_id": ObjectId(data['mongo_product_id'])})
        if not product:
            return error_response("Producto no encontrado", 404)

        if data.get('pickup_location_id'):
            location = Location.query.get(data['pickup_location_id'])
            if not location:
                return error_response("Ubicacion no encontrada", 404)

        start = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        if start >= end:
            return error_response("La fecha de inicio debe ser anterior a la fecha de fin")

        reservation = Reservation(
            renter_user_id=data['renter_user_id'],
            mongo_product_id=data['mongo_product_id'],
            pickup_location_id=data.get('pickup_location_id'),
            start_date=start,
            end_date=end,
            total_price=data['total_price'],
            status=data.get('status', 'pending')
        )
        db.session.add(reservation)
        db.session.commit()

        return jsonify({"message": "Reserva creada", "id": reservation.id}), 201

    except Exception as e:
        return error_response(str(e), 400)


@reservation_bp.route('/reservations', methods=['GET'])
def get_reservations():
    result = paginate(Reservation.query.order_by(Reservation.created_at.desc()))
    items = []
    for r in result["items"]:
        items.append({
            "id": r.id,
            "renter_user_id": r.renter_user_id,
            "mongo_product_id": r.mongo_product_id,
            "pickup_location_id": r.pickup_location_id,
            "start_date": str(r.start_date),
            "end_date": str(r.end_date),
            "total_price": float(r.total_price),
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
    return jsonify({"data": items, "page": result["page"], "per_page": result["per_page"],
                    "total": result["total"], "pages": result["pages"]}), 200


@reservation_bp.route('/reservations/<int:id>', methods=['GET'])
def get_reservation(id):
    r = Reservation.query.get_or_404(id)
    return jsonify({
        "id": r.id,
        "renter_user_id": r.renter_user_id,
        "mongo_product_id": r.mongo_product_id,
        "pickup_location_id": r.pickup_location_id,
        "start_date": str(r.start_date),
        "end_date": str(r.end_date),
        "total_price": float(r.total_price),
        "status": r.status,
        "created_at": r.created_at.isoformat() if r.created_at else None
    }), 200


@reservation_bp.route('/reservations/<int:id>', methods=['PUT'])
@jwt_required()
def update_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return error_response("Datos JSON requeridos")

    try:
        if 'status' in data:
            reservation.status = data['status']
        if 'start_date' in data:
            reservation.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        if 'end_date' in data:
            reservation.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        if 'total_price' in data:
            reservation.total_price = data['total_price']
        if 'pickup_location_id' in data:
            reservation.pickup_location_id = data['pickup_location_id']

        db.session.commit()
        return jsonify({"message": "Reserva actualizada"}), 200

    except Exception as e:
        return error_response(str(e), 400)


@reservation_bp.route('/reservations/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    db.session.delete(reservation)
    db.session.commit()
    return jsonify({"message": "Reserva eliminada"}), 200


@reservation_bp.route('/reservations/user/<int:user_id>', methods=['GET'])
def get_user_reservations(user_id):
    result = paginate(Reservation.query.filter_by(renter_user_id=user_id).order_by(Reservation.created_at.desc()))
    items = []
    for r in result["items"]:
        items.append({
            "id": r.id,
            "renter_user_id": r.renter_user_id,
            "mongo_product_id": r.mongo_product_id,
            "pickup_location_id": r.pickup_location_id,
            "start_date": str(r.start_date),
            "end_date": str(r.end_date),
            "total_price": float(r.total_price),
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })
    return jsonify({"data": items, "page": result["page"], "per_page": result["per_page"],
                    "total": result["total"], "pages": result["pages"]}), 200
