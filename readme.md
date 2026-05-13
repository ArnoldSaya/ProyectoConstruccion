```python
with open("README.md", "w", encoding="utf-8") as f:
    f.write("""# Sistema de Gestión y Alquiler de Productos - Backend 🛠️

Este repositorio contiene el código fuente del backend para el **Sistema de Gestión y Alquiler de Productos**, diseñado bajo una arquitectura moderna de 3 capas y utilizando el principio de **Persistencia Políglota** (bases de datos híbridas).

## 🚀 Arquitectura Tecnológica (Tech Stack)

* **Backend Framework:** [Flask (Python)](https://flask.palletsprojects.com/) - Micro-framework ligero ideal para construir APIs RESTful rápidas y modulares.
* **Base de Datos Relacional (SQL):** [PostgreSQL](https://www.postgresql.org/) - Encargada de los datos transaccionales críticos (Usuarios, Reservas, Pagos). Garantiza la integridad referencial y el cumplimiento de las propiedades ACID.
* **Base de Datos No Relacional (NoSQL):** [MongoDB](https://www.mongodb.com/) - Encargada del catálogo de productos y categorías. Ofrece la flexibilidad necesaria para almacenar productos con especificaciones técnicas heterogéneas.
* **Frontend (Cliente):** Svelte (Implementado en su propio repositorio para máxima velocidad y rendimiento sin DOM virtual).
* **APIs Externas Integradas:** Stripe (Pagos), Google Maps Platform (Geolocalización), Twilio/SendGrid (Notificaciones).

## 📁 Estructura del Proyecto (Patrón "Fábrica de Aplicaciones")

```text
sistema_prestamos_backend/
│
├── app/
│   ├── __init__.py          # Fábrica de la aplicación: une Flask, PostgreSQL y MongoDB.
│   ├── config.py            # Carga de variables de entorno (credenciales).
│   ├── models/              # Definición de datos
│   │   ├── __init__.py      # Instancia global de SQLAlchemy
│   │   ├── sql_models.py    # (O modelos individuales: user.py, reservation.py, etc.)
│   │   └── mongo_models.py  # Modelos/Colecciones NoSQL (Categorías, Productos)
│   └── routes/              # Endpoints de la API REST
│       ├── auth_routes.py   # Rutas de autenticación y registro
│       └── product_routes.py# Rutas para el catálogo híbrido
│
├── .env                     # (Ignorado por Git) Credenciales de bases de datos
├── .gitignore               # Archivos excluidos del control de versiones
├── requirements.txt         # Dependencias del proyecto (Flask, SQLAlchemy, PyMongo, etc.)
└── run.py                   # Archivo principal para arrancar el servidor

```

## ⚙️ Requisitos Previos

Asegúrate de tener instalado en tu máquina local:

1. **Python 3.10+** (Añadido al PATH).
2. **PostgreSQL** (y pgAdmin 4).
3. **MongoDB Community Server** (y MongoDB Compass).

## 🛠️ Instrucciones de Instalación y Ejecución

Sigue estos pasos en orden para levantar el servidor localmente en Windows:

### 1. Clonar el repositorio y abrir terminal

```powershell
git clone https://github.com/ArnoldSaya/ProyectoConstruccion.git
cd sistema_prestamos_backend

```

### 2. Crear y activar el Entorno Virtual

Es imperativo usar un entorno virtual (`venv`) para aislar las dependencias.

```powershell
# Crear el entorno virtual
python -m venv venv

# Autorizar ejecución de scripts (Si te da error de seguridad en Windows)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Activar el entorno virtual
.\\venv\\Scripts\\activate

```

*(Debes ver el prefijo `(venv)` de color verde en tu terminal).*

### 3. Instalar las dependencias

```powershell
pip install -r requirements.txt

```

### 4. Configurar Variables de Entorno (.env)

Crea un archivo llamado `.env` en la raíz del proyecto. **No lo subas a GitHub.** Solicita las claves de producción al equipo, o usa esta plantilla para desarrollo local (nota: sin contraseña para `postgres` según la configuración de desarrollo local):

```env
# Seguridad de Flask
SECRET_KEY=clave-secreta-super-segura

# Conexión PostgreSQL (Transaccional)
DATABASE_URL=postgresql://postgres@localhost:5432/prestamos_db

# Conexión MongoDB Local (Catálogo)
MONGO_URI=mongodb://localhost:27017/prestamos_mongo_db

```

### 5. Preparar la Base de Datos Relacional

Abre **pgAdmin 4** y crea una base de datos vacía llamada exactamente: `prestamos_db`. (No es necesario crear tablas, Flask lo hará automáticamente).

### 6. Ejecutar el Servidor

```powershell
python run.py

```

Si todo está configurado correctamente, verás en la terminal que el servidor se está ejecutando en `http://127.0.0.1:5000`. Además, la instrucción `db.create_all()` generará automáticamente las tablas en PostgreSQL.

## 🧪 Pruebas de la API (Endpoints Principales)

Puedes utilizar **Thunder Client** o **Postman** para probar la persistencia políglota:

1. **Registro de Usuario (PostgreSQL):** `POST http://127.0.0.1:5000/api/auth/register`
2. **Crear Categoría (MongoDB):** `POST http://127.0.0.1:5000/api/categories`
3. **Crear Producto (Híbrido - SQL+NoSQL):** `POST http://127.0.0.1:5000/api/products` (Requiere `owner_id` de PostgreSQL y `category_id` de MongoDB).
""")


```