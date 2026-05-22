# Sistema de Gestion y Alquiler de Productos - Backend

Backend API REST para el sistema de gestion y alquiler de productos.

**Stack:** Flask + PostgreSQL (SQLAlchemy) + MongoDB (PyMongo) + JWT

## Requisitos

- Python 3.10+
- Conexion a bases de datos en la nube (PostgreSQL + MongoDB)

## Instalacion

```powershell
git clone https://github.com/ArnoldSaya/ProyectoConstruccion.git
cd sistema_prestamos_backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Configuracion

Crear archivo `.env` en `sistema_prestamos_backend/app/` con:

```env
SECRET_KEY=clave-secreta
DATABASE_URL=postgresql://usuario:password@host:puerto/basedatos
MONGO_URI=mongodb://usuario:password@host:puerto/basedatos?authSource=admin
JWT_SECRET_KEY=clave-jwt
```

## Ejecutar

```powershell
python run.py
```

El servidor inicia en `http://127.0.0.1:5000`.

## Endpoints

| Recurso | Endpoints |
|---|---|
| Auth | POST /api/auth/register, POST /api/auth/login, GET /api/auth/me |
| Usuarios | CRUD /api/users |
| Categorias | GET /api/categories, POST /api/categories |
| Productos | GET /api/products, POST /api/products, GET /api/products/<id> |
| Ubicaciones | CRUD /api/locations |
| Roles | CRUD /api/user-roles |
| Favoritos | CRUD /api/favorites |
| Reservas | CRUD /api/reservations |
| Pagos | CRUD /api/payments |
| Facturas | CRUD /api/invoices |
| Resenas | CRUD /api/reviews |
| Puntos | CRUD /api/points |
