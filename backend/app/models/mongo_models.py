from bson.objectid import ObjectId
from app import mongo_db  # Importamos la conexion a Mongo que creaste en __init__.py


class CategoryModel:
    @staticmethod
    def _normalize(name_cat):
        return " ".join(name_cat.strip().split())

    @staticmethod
    def _find_duplicate(clean_name, exclude_id=None):
        """
        Busca una categoria cuyo nombre normalizado (minusculas, espacios
        colapsados) coincida con 'clean_name'. No depende de indices unicos
        (util cuando la BD no puede crear el indice por falta de espacio).
        Devuelve el documento duplicado o None.
        """
        target = clean_name.strip().lower()
        query = {}
        if exclude_id is not None:
            query["_id"] = {"$ne": ObjectId(exclude_id)}
        for cat in mongo_db.categories.find(query, {"name_cat": 1}):
            existing = (cat.get("name_cat") or "").strip().lower()
            if existing == target:
                return cat
        return None

    @staticmethod
    def create_category(name_cat, description):
        clean_name = CategoryModel._normalize(name_cat)
        if not clean_name:
            raise ValueError("El nombre de la categoria no puede estar vacio")

        # Validacion insensible a mayusculas/minusculas y espacios extra,
        # para evitar duplicados como 'Hogar' / 'hogar' / 'Hogar  '.
        if CategoryModel._find_duplicate(clean_name):
            raise ValueError("Ya existe una categoria con ese nombre")

        category_data = {
            "name_cat": clean_name,
            "description": description
        }
        result = mongo_db.categories.insert_one(category_data)
        return str(result.inserted_id)

    @staticmethod
    def update_category(category_id, name_cat=None, description=None):
        updates = {}
        if name_cat is not None:
            clean_name = CategoryModel._normalize(name_cat)
            if not clean_name:
                raise ValueError("El nombre de la categoria no puede estar vacio")
            duplicate = CategoryModel._find_duplicate(clean_name, category_id)
            if duplicate:
                raise ValueError("Ya existe una categoria con ese nombre")
            updates["name_cat"] = clean_name
        if description is not None:
            updates["description"] = description

        if not updates:
            return False

        result = mongo_db.categories.update_one(
            {"_id": ObjectId(category_id)}, {"$set": updates}
        )
        return result.matched_count > 0

    @staticmethod
    def delete_category(category_id):
        in_use = mongo_db.products.count_documents({"category_id": ObjectId(category_id)})
        if in_use > 0:
            raise ValueError("No se puede eliminar: hay productos usando esta categoria")
        result = mongo_db.categories.delete_one({"_id": ObjectId(category_id)})
        return result.deleted_count > 0

    @staticmethod
    def get_all_categories():
        categories = list(mongo_db.categories.find())
        # Convertir el ObjectId a string para poder enviarlo en JSON
        for cat in categories:
            cat['_id'] = str(cat['_id'])
        return categories


class ProductModel:
    @staticmethod
    def create_product(owner_id, name_prod, description, category_id, price, details, status="disponible", image_url=None):
        product_data = {
            "owner_id": owner_id,  # Este ID viene de tu base de datos PostgreSQL
            "name_prod": name_prod,
            "description": description,
            "category_id": ObjectId(category_id),  # Relacion con la coleccion Categories
            "price": float(price),
            "details": details,
            "status": status,
            "image_url": image_url
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
