"""
Script de limpieza UNICA vez para la coleccion 'categories' de MongoDB.

Que hace:
  1. Corrige nombres mal escritos conocidos (por ejemplo 'herramientass' -> 'Herramientas').
  2. Normaliza espacios y capitalizacion basica.
  3. Busca categorias duplicadas (mismo nombre, sin importar mayusculas/espacios),
     se queda con la mas antigua, reasigna todos los productos de las duplicadas
     hacia esa, y borra las duplicadas.
  4. Vuelve a crear el indice unico sobre 'name_cat' (case-insensitive) para
     que no se puedan crear mas duplicados a futuro.

Como usarlo:
  1. Colocate en la carpeta sistema_prestamos_backend (donde esta tu .env real).
  2. Ejecuta:  python fix_categories.py
  3. Revisa el resumen impreso en consola.

Este script SOLO debe correrse una vez para arreglar los datos existentes.
NO se ejecuto automaticamente: se entrega para que tu lo corras contra tu
base de datos real, ya que este entorno de pruebas no tiene acceso a ella.
"""
import os
import re
from collections import defaultdict

from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', '.env'))

MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("No se encontro MONGO_URI en el .env")

# Correcciones conocidas de ortografia / nombre -> nombre correcto
KNOWN_FIXES = {
    "herramientass": "Herramientas",
    "herramienta": "Herramientas",
    "herramientas": "Herramientas",
    "hogar": "Hogar",
}


def clean_name(raw_name):
    name = " ".join(raw_name.strip().split())
    key = name.lower()
    if key in KNOWN_FIXES:
        return KNOWN_FIXES[key]
    return name


def main():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client.get_default_database()

    categories = list(db.categories.find().sort("_id", 1))
    print(f"Categorias encontradas: {len(categories)}")

    groups = defaultdict(list)
    for cat in categories:
        fixed_name = clean_name(cat.get("name_cat", ""))
        groups[fixed_name.lower()].append((cat, fixed_name))

    renamed = 0
    merged = 0
    deleted_ids = []

    for key, items in groups.items():
        # items: lista de (documento_original, nombre_corregido)
        items.sort(key=lambda pair: pair[0]["_id"])  # el mas antiguo primero
        keeper_doc, keeper_name = items[0]
        keeper_id = keeper_doc["_id"]

        # Renombrar el que se conserva si hacia falta corregirlo
        if keeper_doc.get("name_cat") != keeper_name:
            db.categories.update_one({"_id": keeper_id}, {"$set": {"name_cat": keeper_name}})
            renamed += 1
            print(f"  Renombrado: '{keeper_doc.get('name_cat')}' -> '{keeper_name}'")

        # El resto de items con el mismo nombre normalizado son duplicados
        for dup_doc, _ in items[1:]:
            dup_id = dup_doc["_id"]
            result = db.products.update_many(
                {"category_id": dup_id}, {"$set": {"category_id": keeper_id}}
            )
            db.categories.delete_one({"_id": dup_id})
            deleted_ids.append(dup_id)
            merged += 1
            print(
                f"  Duplicado '{dup_doc.get('name_cat')}' ({dup_id}) fusionado en "
                f"'{keeper_name}' ({keeper_id}); {result.modified_count} producto(s) reasignado(s)"
            )

    # Recrear el indice unico (por si antes fallo por los duplicados existentes)
    try:
        db.categories.drop_index("name_cat_1")
    except Exception:
        pass
    try:
        db.categories.create_index(
            "name_cat",
            unique=True,
            background=True,
            collation={"locale": "es", "strength": 2}
        )
    except Exception as e:
        print("[INFO] No se pudo crear el indice unico (posiblemente sin espacio en disco):", e)

    print("\nResumen:")
    print(f"  Nombres corregidos: {renamed}")
    print(f"  Categorias duplicadas eliminadas: {merged}")
    print(f"  Total categorias ahora: {db.categories.count_documents({})}")


if __name__ == "__main__":
    main()
