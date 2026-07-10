from flask import jsonify, request
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User


def validate_required(data, fields):
    errors = []
    for field in fields:
        if field not in data or (isinstance(data[field], str) and not data[field].strip()):
            errors.append(f"Campo '{field}' es requerido")
    if errors:
        return {"error": errors}
    return None


def paginate(query, page=None, per_page=None):
    page = page or request.args.get('page', 1, type=int)
    per_page = per_page or request.args.get('per_page', 10, type=int)
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 10
    if per_page > 100:
        per_page = 100
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "items": paginated.items,
        "page": paginated.page,
        "per_page": paginated.per_page,
        "total": paginated.total,
        "pages": paginated.pages
    }


def error_response(message, status_code=400):
    if isinstance(message, str):
        message = [message]
    return jsonify({"error": message}), status_code
