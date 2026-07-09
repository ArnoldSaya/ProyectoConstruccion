import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.models.payment import Payment
from app.models.reservation import Reservation
from app import db
from app.utils import validate_required, paginate, error_response

payment_bp = Blueprint('payments', __name__)


@payment_bp.route('/payments', methods=['POST'])
@jwt_required()
def create_payment():
    data = request.get_json()
    if not data:
        return error_response("Datos JSON requeridos")

    err = validate_required(data, ['reservation_id', 'amount'])
    if err:
        return jsonify(err), 400

    try:
        reservation = Reservation.query.get(data['reservation_id'])
        if not reservation:
            return error_response("Reserva no encontrada", 404)

        payment = Payment(
            reservation_id=data['reservation_id'],
            amount=data['amount'],
            payment_status=data.get('payment_status', 'completed'),
            transaction_code=data.get('transaction_code', str(uuid.uuid4()))
        )
        db.session.add(payment)
        db.session.commit()

        return jsonify({"message": "Pago registrado", "id": payment.id}), 201

    except Exception as e:
        return error_response(str(e), 400)


@payment_bp.route('/payments', methods=['GET'])
def get_payments():
    result = paginate(Payment.query.order_by(Payment.payment_date.desc()))
    items = []
    for p in result["items"]:
        items.append({
            "id": p.id,
            "reservation_id": p.reservation_id,
            "amount": float(p.amount),
            "payment_date": p.payment_date.isoformat() if p.payment_date else None,
            "payment_status": p.payment_status,
            "transaction_code": p.transaction_code
        })
    return jsonify({"data": items, "page": result["page"], "per_page": result["per_page"],
                    "total": result["total"], "pages": result["pages"]}), 200


@payment_bp.route('/payments/<int:id>', methods=['GET'])
def get_payment(id):
    p = Payment.query.get_or_404(id)
    return jsonify({
        "id": p.id,
        "reservation_id": p.reservation_id,
        "amount": float(p.amount),
        "payment_date": p.payment_date.isoformat() if p.payment_date else None,
        "payment_status": p.payment_status,
        "transaction_code": p.transaction_code
    }), 200


@payment_bp.route('/payments/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_payment(id):
    payment = Payment.query.get_or_404(id)
    db.session.delete(payment)
    db.session.commit()
    return jsonify({"message": "Pago eliminado"}), 200
