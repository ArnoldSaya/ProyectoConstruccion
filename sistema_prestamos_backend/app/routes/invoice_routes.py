from flask import Blueprint, request, jsonify

from app.models.invoice import Invoice
from app.models.payment import Payment
from app import db

invoice_bp = Blueprint('invoices', __name__)

# CREAR FACTURA
@invoice_bp.route('/invoices', methods=['POST'])
def create_invoice():

    data = request.get_json()

    try:

        # VALIDAR PAYMENT
        payment = Payment.query.get(
            data['payment_id']
        )

        if not payment:
            return jsonify({
                "error": "Pago no encontrado"
            }), 404

        # VALIDAR CÓDIGO ÚNICO
        existing_invoice = Invoice.query.filter_by(
            invoice_code=data['invoice_code']
        ).first()

        if existing_invoice:
            return jsonify({
                "error": "Código de factura ya existe"
            }), 400

        # VALIDAR TOTAL
        if float(data['total']) <= 0:
            return jsonify({
                "error": "Total inválido"
            }), 400

        invoice = Invoice(
            payment_id=data['payment_id'],
            subtotal=data['subtotal'],
            platform_fee=data['platform_fee'],
            owner_earnings=data['owner_earnings'],
            taxes=data['taxes'],
            total=data['total'],
            invoice_code=data['invoice_code']
        )

        db.session.add(invoice)
        db.session.commit()

        return jsonify({
            "message": "Factura creada",
            "id": invoice.id
        }), 201

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400


# LISTAR FACTURAS
@invoice_bp.route('/invoices', methods=['GET'])
def get_invoices():

    invoices = Invoice.query.all()

    result = []

    for invoice in invoices:
        result.append({
            "id": invoice.id,
            "payment_id": invoice.payment_id,
            "subtotal": float(invoice.subtotal),
            "platform_fee": float(invoice.platform_fee),
            "owner_earnings": float(invoice.owner_earnings),
            "taxes": float(invoice.taxes),
            "total": float(invoice.total),
            "invoice_code": invoice.invoice_code
        })

    return jsonify(result), 200


# OBTENER FACTURA
@invoice_bp.route('/invoices/<int:id>', methods=['GET'])
def get_invoice(id):

    invoice = Invoice.query.get_or_404(id)

    return jsonify({
        "id": invoice.id,
        "payment_id": invoice.payment_id,
        "total": float(invoice.total),
        "invoice_code": invoice.invoice_code
    }), 200


# ELIMINAR FACTURA
@invoice_bp.route('/invoices/<int:id>', methods=['DELETE'])
def delete_invoice(id):

    invoice = Invoice.query.get_or_404(id)

    db.session.delete(invoice)
    db.session.commit()

    return jsonify({
        "message": "Factura eliminada"
    }), 200