

```
# Sistema de Gestión de Préstamos - Backend (Flask)

Este es el núcleo del sistema de préstamos, encargado de la lógica de negocio y la persistencia híbrida (SQL + NoSQL).

## 🚀 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado lo siguiente en tu Windows:

1. **Python 3.10+** (Añadido al PATH).
2. **PostgreSQL** (Crear base de datos llamada `prestamos_db`).
3. **MongoDB Community Server** (Corriendo localmente).
4. **Visual Studio Code**.

## 🛠️ Configuración del Proyecto

Sigue estos pasos en orden para levantar el servidor:

### 1. Clonar y preparar el entorno
Abre una terminal en la carpeta del proyecto y ejecuta:

```powershell
# Crear el entorno virtual
python -m venv venv

# Autorizar ejecución de scripts (Solo si es necesario)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# Activar el entorno
.\venv\Scripts\activate

```

### 2. Instalar dependencias

Con el entorno `(venv)` activo, instala las librerías necesarias:

```powershell
pip install -r requirements.txt

```

### 3. Configuración de Variables de Entorno

Crea un archivo llamado `.env` en la raíz (usa como base el archivo de ejemplo o solicita las claves al administrador) con el siguiente contenido:

```env
SECRET_KEY=tu_clave_secreta
DATABASE_URL=postgresql://postgres@localhost:5432/prestamos_db
MONGO_URI=mongodb://localhost:27017/prestamos_mongo_db

```

### 4. Inicialización de la Base de Datos

Abre **pgAdmin**, crea una base de datos vacía con el nombre `prestamos_db`. El sistema se encargará de crear las tablas automáticamente al arrancar.

### 5. Ejecutar el Servidor

Inicia el backend con el siguiente comando:

```powershell
python run.py

```

El servidor estará disponible en: `http://127.0.0.1:5000`

## 🏗️ Arquitectura

* **Framework:** Flask (Python)
* **SQL:** PostgreSQL (Usuarios, Reservas, Pagos) - Propiedades ACID.
* **NoSQL:** MongoDB (Catálogo de productos dinámico).
* **ORM:** SQLAlchemy.

```

---

