import os
import uuid
from bson.objectid import ObjectId
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.models.mongo_models import CategoryModel, ProductModel
from app.models.role import Role
from app.models.user_role import UserRole
from app import db, mongo_db
from app.utils import validate_required, error_response

product_bp = Blueprint('products', __name__)


@product_bp.route('/categories', methods=['POST'])
@jwt_required()
def add_category():
    data = request.get_json()
    if not data:
        return error_response("Datos JSON requeridos")

    err = validate_required(data, ['name_cat', 'description'])
    if err:
        return jsonify(err), 400

    try:
        category_id = CategoryModel.create_category(
            name_cat=data['name_cat'],
            description=data['description']
        )
        return jsonify({"message": "Categoria creada", "id": category_id}), 201
    except Exception as e:
        return error_response(str(e), 400)


@product_bp.route('/categories', methods=['GET'])
def list_categories():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    skip = (page - 1) * per_page

    total = mongo_db.categories.count_documents({})
    categories = list(mongo_db.categories.find().skip(skip).limit(per_page))

    for cat in categories:
        cat['_id'] = str(cat['_id'])

    return jsonify({
        "data": categories,
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": (total + per_page - 1) // per_page if total > 0 else 0
    }), 200


@product_bp.route('/categories/<string:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    data = request.get_json()
    if not data:
        return error_response("Datos JSON requeridos")

    try:
        updated = CategoryModel.update_category(
            category_id,
            name_cat=data.get('name_cat'),
            description=data.get('description')
        )
        if not updated:
            return error_response("Categoria no encontrada o sin cambios", 404)
        return jsonify({"message": "Categoria actualizada"}), 200
    except Exception as e:
        return error_response(str(e), 400)


@product_bp.route('/categories/<string:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    try:
        deleted = CategoryModel.delete_category(category_id)
        if not deleted:
            return error_response("Categoria no encontrada", 404)
        return jsonify({"message": "Categoria eliminada"}), 200
    except Exception as e:
        return error_response(str(e), 400)


@product_bp.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    data = request.get_json()
    if not data:
        return error_response("Datos JSON requeridos")

    err = validate_required(data, ['owner_id', 'name_prod', 'description', 'category_id', 'price'])
    if err:
        return jsonify(err), 400

    try:
        product_id = ProductModel.create_product(
            owner_id=data['owner_id'],
            name_prod=data['name_prod'],
            description=data['description'],
            category_id=data['category_id'],
            price=data['price'],
            details=data.get('details'),
            image_url=data.get('image_url')
        )

        # Cambiar rol a "rentador" si aun no lo tiene
        rol_rentador = Role.query.filter_by(role_name='rentador').first()
        if rol_rentador:
            tiene_rol = UserRole.query.filter_by(
                user_id=data['owner_id'], role_id=rol_rentador.id
            ).first()
            if not tiene_rol:
                ur = UserRole(user_id=data['owner_id'], role_id=rol_rentador.id)
                db.session.add(ur)
                db.session.commit()

        return jsonify({"message": "Producto publicado", "id": product_id}), 201
    except Exception as e:
        return error_response(str(e), 400)


@product_bp.route('/products', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    skip = (page - 1) * per_page
    category_id = request.args.get('category_id')

    query = {}
    if category_id:
        query["category_id"] = ObjectId(category_id)

    total = mongo_db.products.count_documents(query)
    products_cursor = mongo_db.products.find(query).skip(skip).limit(per_page)

    result = []
    for product in products_cursor:
        result.append({
            "_id": str(product['_id']),
            "owner_id": product.get('owner_id'),
            "name_prod": product.get('name_prod'),
            "description": product.get('description'),
            "category_id": str(product.get('category_id')) if product.get('category_id') else None,
            "price": product.get('price'),
            "details": product.get('details'),
            "status": product.get('status', 'disponible'),
            "image_url": product.get('image_url')
        })

    return jsonify({
        "data": result,
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": (total + per_page - 1) // per_page if total > 0 else 0
    }), 200


@product_bp.route('/products/<string:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = mongo_db.products.find_one({"_id": ObjectId(product_id)})
        if not product:
            return error_response("Producto no encontrado", 404)
        product['_id'] = str(product['_id'])
        product['category_id'] = str(product['category_id']) if product.get('category_id') else None
        return jsonify(product), 200
    except Exception as e:
        return error_response(str(e), 400)


@product_bp.route('/products/<string:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """Elimina un producto de MongoDB. Bloquea si tiene reservas activas."""
    try:
        product = mongo_db.products.find_one({"_id": ObjectId(product_id)})
        if not product:
            return error_response("Producto no encontrado", 404)

        from app.models.reservation import Reservation
        activas = Reservation.query.filter(
            Reservation.mongo_product_id == product_id,
            Reservation.status.in_(['pending', 'confirmed'])
        ).count()
        if activas > 0:
            return error_response(
                f"No se puede eliminar: tiene {activas} reserva(s) activa(s)", 400
            )

        # Limpiar referencias en favoritos
        try:
            from app.models.favorite import Favorite
            Favorite.query.filter_by(mongo_product_id=product_id).delete()
            db.session.commit()
        except Exception:
            db.session.rollback()

        result = mongo_db.products.delete_one({"_id": ObjectId(product_id)})
        if result.deleted_count == 0:
            return error_response("Producto no encontrado", 404)

        return jsonify({"message": "Producto eliminado"}), 200
    except Exception as e:
        return error_response(str(e), 400)


@product_bp.route('/uploads', methods=['POST'])
@jwt_required()
def upload_image():
    """
    Sube una foto de producto (multipart/form-data, campo 'file').
    Guarda el archivo en app/static/uploads/products/ con un nombre unico
    y devuelve la URL publica para luego guardarla en el producto.
    """
    if 'file' not in request.files:
        return error_response("No se envio ningun archivo (campo 'file')", 400)

    file = request.files['file']
    if not file or file.filename == '':
        return error_response("Nombre de archivo vacio", 400)

    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    allowed = current_app.config['ALLOWED_IMAGE_EXTENSIONS']
    if ext not in allowed:
        return error_response(
            "Formato no permitido. Usa: " + ", ".join(sorted(allowed)), 400
        )

    filename = uuid.uuid4().hex + "." + ext
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, filename))

    relative_url = "/static/uploads/products/" + filename
    full_url = current_app.config['BACKEND_URL'] + relative_url

    return jsonify({
        "message": "Imagen subida",
        "url": full_url,
        "path": relative_url
    }), 201


@product_bp.route("/testmongo")
def testmongo():
    mongo_db.test.insert_one({"ok": True})
    return {"msg": "Mongo Railway OK"}
