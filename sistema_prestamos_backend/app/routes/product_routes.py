from flask import Blueprint, request, jsonify
from app.models.mongo_models import CategoryModel, ProductModel
from app import mongo_db

product_bp = Blueprint('products', __name__)

# --- RUTAS PARA CATEGORÍAS ---
@product_bp.route('/categories', methods=['POST'])
def add_category():
    data = request.get_json()
    try:
        # Usamos el modelo de Mongo para insertar
        category_id = CategoryModel.create_category(
            name_cat=data['name_cat'],
            description=data['description']
        )
        return jsonify({"message": "Categoría creada", "id": category_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@product_bp.route('/categories', methods=['GET'])
def list_categories():
    categories = CategoryModel.get_all_categories()
    return jsonify(categories), 200

# --- RUTAS PARA PRODUCTOS ---
@product_bp.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    try:
        # El owner_id debe ser un ID válido de tu PostgreSQL
        product_id = ProductModel.create_product(
            owner_id=data['owner_id'], 
            name_prod=data['name_prod'],
            description=data['description'],
            category_id=data['category_id'],
            price=data['price'],
            details=data['details']
        )
        return jsonify({"message": "Producto publicado", "id": product_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@product_bp.route("/testmongo")
def testmongo():
    mongo_db.test.insert_one({"ok": True})
    return {"msg": "Mongo Railway OK"}
@product_bp.route('/products', methods=['GET'])
def get_products():

    products_cursor = mongo_db.products.find()

    result = []

    for product in products_cursor:

        result.append({
            "_id": str(product['_id']),
            "owner_id": product.get('owner_id'),
            "name_prod": product.get('name_prod'),
            "description": product.get('description'),
            "category_id": str(product.get('category_id')),
            "price": product.get('price'),
            "details": product.get('details')
        })

    return jsonify(result), 200