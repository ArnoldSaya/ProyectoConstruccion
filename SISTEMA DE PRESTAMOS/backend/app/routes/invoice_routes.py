import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.models.invoice import Invoice
from app.models.payment import Payment
from app import db
from app.utils import validate_required, paginate, error_response

invoice_bp = Blueprint('invoices', __name__)


@invoice_bp.route('/invoices', methods=['POST'])
@jwt_required()
def create_invoice():
    data = request.get_json()
    if not data:
        return error_response("Datos JSON requeridos")

    err = validate_required(data, ['payment_id', 'subtotal', 'platform_fee', 'owner_earnings', 'taxes', 'total'])
    if err:
        return jsonify(err), 400

    try:
        payment = Payment.query.get(data['payment_id'])
        if not payment:
            return error_response("Pago no encontrado", 404)

        if float(data['total']) <= 0:
            return error_response("Total invalido", 400)

        invoice_code = data.get('invoice_code', f"INV-{uuid.uuid4().hex[:8].upper()}")
        existing = Invoice.query.filter_by(invoice_code=invoice_code).first()
        if existing:
            return error_response("Codigo de factura ya existe", 400)

        invoice = Invoice(
            payment_id=data['payment_id'],
            subtotal=data['subtotal'],
            platform_fee=data['platform_fee'],
            owner_earnings=data['owner_earnings'],
            taxes=data['taxes'],
            total=data['total'],
            invoice_code=invoice_code
        )
        db.session.add(invoice)
        db.session.commit()

        return jsonify({"message": "Factura creada", "id": invoice.id}), 201

    except Exception as e:
        return error_response(str(e), 400)


@invoice_bp.route('/invoices', methods=['GET'])
def get_invoices():
    result = paginate(Invoice.query.order_by(Invoice.generated_at.desc()))
    items = []
    for inv in result["items"]:
        items.append({
            "id": inv.id,
            "payment_id": inv.payment_id,
            "subtotal": float(inv.subtotal),
            "platform_fee": float(inv.platform_fee),
            "owner_earnings": float(inv.owner_earnings),
            "taxes": float(inv.taxes),
            "total": float(inv.total),
            "invoice_code": inv.invoice_code,
            "generated_at": inv.generated_at.isoformat() if inv.generated_at else None
        })
    return jsonify({"data": items, "page": result["page"], "per_page": result["per_page"],
                    "total": result["total"], "pages": result["pages"]}), 200


@invoice_bp.route('/invoices/<int:id>', methods=['GET'])
def get_invoice(id):
    inv = Invoice.query.get_or_404(id)
    return jsonify({
        "id": inv.id,
        "payment_id": inv.payment_id,
        "subtotal": float(inv.subtotal),
        "platform_fee": float(inv.platform_fee),
        "owner_earnings": float(inv.owner_earnings),
        "taxes": float(inv.taxes),
        "total": float(inv.total),
        "invoice_code": inv.invoice_code,
        "generated_at": inv.generated_at.isoformat() if inv.generated_at else None
    }), 200


@invoice_bp.route('/invoices/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_invoice(id):
    invoice = Invoice.query.get_or_404(id)
    db.session.delete(invoice)
    db.session.commit()
    return jsonify({"message": "Factura eliminada"}), 200
