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

    err = validate_required(data, ['renter_user_id', 'mongo_product_id', 'start_date', 'end_date'])
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

        # Validar solapamiento con reservas existentes del mismo producto
        overlap = Reservation.query.filter(
            Reservation.mongo_product_id == data['mongo_product_id'],
            Reservation.status.in_(['pending', 'confirmed', 'active']),
            Reservation.start_date <= end,
            Reservation.end_date >= start
        ).first()
        if overlap:
            return error_response("El producto ya tiene una reserva para esas fechas", 409)

        # ==================================
        # PRECIO CALCULADO POR EL SISTEMA (autoritativo)
        # total = precio_del_producto * dias_de_alquiler
        # ==================================
        days = (end - start).days
        if days < 1:
            days = 1
        product_price = float(product.get('price') or 0)
        total_price = round(product_price * days, 2)

        reservation = Reservation(
            renter_user_id=data['renter_user_id'],
            mongo_product_id=data['mongo_product_id'],
            pickup_location_id=data.get('pickup_location_id'),
            start_date=start,
            end_date=end,
            total_price=total_price,
            status=data.get('status', 'pending')
        )
        db.session.add(reservation)

        # Actualizar estado del producto a "reservado"
        mongo_db.products.update_one(
            {"_id": ObjectId(data['mongo_product_id'])},
            {"$set": {"status": "reservado"}}
        )

        db.session.commit()

        return jsonify({
            "message": "Reserva creada",
            "id": reservation.id,
            "days": days,
            "unit_price": product_price,
            "total_price": float(reservation.total_price)
        }), 201

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

    old_status = reservation.status
    product_id = reservation.mongo_product_id

    try:
        if 'status' in data:
            reservation.status = data['status']
        if 'start_date' in data:
            reservation.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        if 'end_date' in data:
            reservation.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        if 'pickup_location_id' in data:
            reservation.pickup_location_id = data['pickup_location_id']

        # Recalcular precio si cambiaron las fechas (el sistema lo pone)
        if 'start_date' in data or 'end_date' in data:
            product = mongo_db.products.find_one({"_id": ObjectId(reservation.mongo_product_id)})
            if not product:
                return error_response("Producto asociado no encontrado", 404)
            days = (reservation.end_date - reservation.start_date).days
            if days < 1:
                days = 1
            unit = float(product.get('price') or 0)
            reservation.total_price = round(unit * days, 2)

        db.session.commit()

        # Actualizar estado del producto según estado de la reserva
        if old_status != reservation.status:
            if reservation.status in ('cancelled', 'rejected'):
                # Verificar si hay otras reservas activas para este producto
                active = Reservation.query.filter(
                    Reservation.mongo_product_id == product_id,
                    Reservation.id != id,
                    Reservation.status.in_(['pending', 'confirmed', 'active'])
                ).first()
                new_status = 'disponible' if not active else 'reservado'
                mongo_db.products.update_one(
                    {"_id": ObjectId(product_id)},
                    {"$set": {"status": new_status}}
                )
            elif reservation.status in ('pending', 'confirmed', 'active'):
                mongo_db.products.update_one(
                    {"_id": ObjectId(product_id)},
                    {"$set": {"status": "reservado"}}
                )

        return jsonify({"message": "Reserva actualizada"}), 200

    except Exception as e:
        return error_response(str(e), 400)


@reservation_bp.route('/reservations/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_reservation(id):
    reservation = Reservation.query.get_or_404(id)
    product_id = reservation.mongo_product_id
    db.session.delete(reservation)
    db.session.commit()

    # Verificar si quedan otras reservas activas para este producto
    active = Reservation.query.filter(
        Reservation.mongo_product_id == product_id,
        Reservation.id != id,
        Reservation.status.in_(['pending', 'confirmed', 'active'])
    ).first()
    new_status = 'disponible' if not active else 'reservado'
    mongo_db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"status": new_status}}
    )
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
