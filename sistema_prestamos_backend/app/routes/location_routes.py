from flask import Blueprint, request, jsonify

from app.models.location import Location
from app.models.user import User
from app import db

location_bp = Blueprint('locations', __name__)

# CREAR UBICACIÓN
@location_bp.route('/locations', methods=['POST'])
def create_location():

    data = request.get_json()

    try:

        # VALIDAR USUARIO
        user = User.query.get(
            data['user_id']
        )

        if not user:
            return jsonify({
                "error": "Usuario no encontrado"
            }), 404

        # VALIDAR LATITUD
        if data.get('latitude'):

            latitude = float(
                data['latitude']
            )

            if latitude < -90 or latitude > 90:
                return jsonify({
                    "error": "Latitud inválida"
                }), 400

        # VALIDAR LONGITUD
        if data.get('longitude'):

            longitude = float(
                data['longitude']
            )

            if longitude < -180 or longitude > 180:
                return jsonify({
                    "error": "Longitud inválida"
                }), 400

        location = Location(
            user_id=data['user_id'],
            location_name=data['location_name'],
            address=data['address'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            city=data.get('city'),
            reference=data.get('reference'),
            is_meeting_point=data.get(
                'is_meeting_point',
                False
            )
        )

        db.session.add(location)
        db.session.commit()

        return jsonify({
            "message": "Ubicación creada",
            "id": location.id
        }), 201

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400


# LISTAR UBICACIONES
@location_bp.route('/locations', methods=['GET'])
def get_locations():

    locations = Location.query.all()

    result = []

    for location in locations:
        result.append({
            "id": location.id,
            "user_id": location.user_id,
            "location_name": location.location_name,
            "address": location.address,
            "city": location.city,
            "is_meeting_point": location.is_meeting_point
        })

    return jsonify(result), 200


# ELIMINAR UBICACIÓN
@location_bp.route('/locations/<int:id>', methods=['DELETE'])
def delete_location(id):

    location = Location.query.get_or_404(id)

    db.session.delete(location)
    db.session.commit()

    return jsonify({
        "message": "Ubicación eliminada"
    }), 200