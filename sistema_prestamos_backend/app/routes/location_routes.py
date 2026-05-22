from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.models.location import Location
from app.models.user import User
from app import db
from app.utils import validate_required, paginate, error_response

location_bp = Blueprint('locations', __name__)


@location_bp.route('/locations', methods=['POST'])
@jwt_required()
def create_location():
    data = request.get_json()
    if not data:
        return error_response("Datos JSON requeridos")

    err = validate_required(data, ['user_id', 'location_name', 'address'])
    if err:
        return jsonify(err), 400

    try:
        user = User.query.get(data['user_id'])
        if not user:
            return error_response("Usuario no encontrado", 404)

        if data.get('latitude'):
            lat = float(data['latitude'])
            if lat < -90 or lat > 90:
                return error_response("Latitud invalida", 400)

        if data.get('longitude'):
            lng = float(data['longitude'])
            if lng < -180 or lng > 180:
                return error_response("Longitud invalida", 400)

        location = Location(
            user_id=data['user_id'],
            location_name=data['location_name'],
            address=data['address'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            city=data.get('city'),
            reference=data.get('reference'),
            is_meeting_point=data.get('is_meeting_point', False)
        )
        db.session.add(location)
        db.session.commit()

        return jsonify({"message": "Ubicacion creada", "id": location.id}), 201

    except Exception as e:
        return error_response(str(e), 400)


@location_bp.route('/locations', methods=['GET'])
def get_locations():
    result = paginate(Location.query.order_by(Location.created_at.desc()))
    items = []
    for loc in result["items"]:
        items.append({
            "id": loc.id,
            "user_id": loc.user_id,
            "location_name": loc.location_name,
            "address": loc.address,
            "city": loc.city,
            "latitude": float(loc.latitude) if loc.latitude else None,
            "longitude": float(loc.longitude) if loc.longitude else None,
            "is_meeting_point": loc.is_meeting_point,
            "created_at": loc.created_at.isoformat() if loc.created_at else None
        })
    return jsonify({"data": items, "page": result["page"], "per_page": result["per_page"],
                    "total": result["total"], "pages": result["pages"]}), 200


@location_bp.route('/locations/user/<int:user_id>', methods=['GET'])
def get_user_locations(user_id):
    result = paginate(Location.query.filter_by(user_id=user_id).order_by(Location.created_at.desc()))
    items = []
    for loc in result["items"]:
        items.append({
            "id": loc.id,
            "location_name": loc.location_name,
            "address": loc.address,
            "city": loc.city,
            "is_meeting_point": loc.is_meeting_point
        })
    return jsonify({"data": items, "page": result["page"], "per_page": result["per_page"],
                    "total": result["total"], "pages": result["pages"]}), 200


@location_bp.route('/locations/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_location(id):
    location = Location.query.get_or_404(id)
    db.session.delete(location)
    db.session.commit()
    return jsonify({"message": "Ubicacion eliminada"}), 200
