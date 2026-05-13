from bson.objectid import ObjectId
from app import mongo_db  # Importamos la conexión a Mongo que creaste en __init__.py

class CategoryModel:
    @staticmethod
    def create_category(name_cat, description):
        category_data = {
            "name_cat": name_cat,
            "description": description
        }
        result = mongo_db.categories.insert_one(category_data)
        return str(result.inserted_id)

    @staticmethod
    def get_all_categories():
        categories = list(mongo_db.categories.find())
        # Convertir el ObjectId a string para poder enviarlo en JSON
        for cat in categories:
            cat['_id'] = str(cat['_id'])
        return categories

class ProductModel:
    @staticmethod
    def create_product(owner_id, name_prod, description, category_id, price, details, status="disponible"):
        product_data = {
            "owner_id": owner_id,  # Este ID viene de tu base de datos PostgreSQL
            "name_prod": name_prod,
            "description": description,
            "category_id": ObjectId(category_id), # Relación con la colección Categories
            "price": float(price),
            "details": details,
            "status": status
        }
        result = mongo_db.products.insert_one(product_data)
        return str(result.inserted_id)

    @staticmethod
    def get_products_by_category(category_id):
        products = list(mongo_db.products.find({"category_id": ObjectId(category_id)}))
        for prod in products:
            prod['_id'] = str(prod['_id'])
            prod['category_id'] = str(prod['category_id'])
        return products
    