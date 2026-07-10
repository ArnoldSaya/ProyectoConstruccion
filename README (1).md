# Sistema de Préstamos / Alquiler de Productos

Plataforma web tipo *marketplace* de alquiler entre usuarios (peer-to-peer):
un usuario publica un producto (herramienta, equipo, etc.) y otro lo reserva
y paga por un rango de fechas. Incluye roles (cliente / rentador), sistema
de reseñas, favoritos, puntos, ubicaciones de recojo y login con Google.

## Tabla de contenidos

- [Arquitectura](#arquitectura)
- [Proveedor OAuth: Google](#proveedor-oauth-google)
- [Por qué dos bases de datos](#por-qué-dos-bases-de-datos)
- [Cómo correr el proyecto](#cómo-correr-el-proyecto)
- [Estructura de carpetas](#estructura-de-carpetas)
- [Deploy](#deploy)

---

## Arquitectura

```
┌─────────────────────┐        HTTPS / JWT        ┌──────────────────────────┐
│   Frontend (Vue 3)   │ ────────────────────────▶ │   Backend (Flask API)    │
│   Vite + Pinia +     │ ◀──────────────────────── │   Blueprints por entidad │
│   Vue Router + Axios │        JSON               │   JWT + Google OAuth 2.0 │
└─────────────────────┘                            └───────────┬──────────────┘
                                                                 │
                                              ┌──────────────────┴──────────────────┐
                                              ▼                                     ▼
                                   ┌────────────────────┐              ┌────────────────────┐
                                   │  PostgreSQL         │              │  MongoDB             │
                                   │  (Supabase)          │              │  (catálogo)          │
                                   │  users, roles,        │              │  products,            │
                                   │  reservations,          │              │  categories            │
                                   │  payments, invoices,     │              │                        │
                                   │  reviews, points,          │              │                        │
                                   │  locations, favorites        │              │                        │
                                   └────────────────────┘              └────────────────────┘
```

**Backend — Flask**, organizado por **Blueprints**: cada entidad tiene su
`model` (SQLAlchemy o helper de PyMongo) y su `routes` (endpoints REST bajo
`/api`), registrados en `app/__init__.py`. Autenticación con JWT
(`flask-jwt-extended`); los endpoints de escritura están protegidos con
`@jwt_required()`.

**Frontend — Vue 3 + Vite**, con:
- `services/*.js` → funciones que llaman a la API con Axios
- `stores/auth.js` (Pinia) → estado de sesión, guarda el JWT en `localStorage`
- `router/index.js` → rutas con *guards* que bloquean vistas si no hay sesión
  o si el usuario no tiene el rol requerido (`meta.requiresAuth`, `meta.role`)

En producción, el backend sirve el build del frontend como SPA (ver
[Deploy](#deploy)), así que en Render es un solo servicio.

---

## Proveedor OAuth: Google

Se eligió **Google como único proveedor OAuth 2.0** (vía `Authlib`).

**Por qué Google y no otro (Facebook, GitHub, etc.):**
- Es el proveedor con mayor adopción entre los usuarios objetivo (cualquier
  persona con una cuenta de Gmail, que en Perú es prácticamente universal),
  reduce fricción en el registro.
- Google entrega, además del login, acceso a **APIs útiles para el negocio**
  sin pedirle credenciales extra al usuario: Drive (para adjuntar
  comprobantes/fotos), Calendar (recordatorios de fechas de devolución) y
  Gmail (envío de notificaciones) — todo bajo el mismo consentimiento OAuth.
- Tiene un flujo de *discovery* estándar (`GOOGLE_DISCOVERY_URL`) y librerías
  maduras (`authlib`, `google-auth`) que evitan implementar el protocolo a mano.

**Cómo funciona en este proyecto** (`app/oauth.py`, `app/routes/google_auth_routes.py`):

1. El usuario entra a `GET /api/auth/google/login` → el backend arma un
   `redirect_uri` **fijo** (desde `BACKEND_URL`, no con `url_for`) para evitar
   el error `redirect_uri_mismatch` en Google Cloud Console, y redirige a la
   pantalla de consentimiento de Google.
2. Google redirige de vuelta a `GET /api/auth/google/callback` con un `code`.
   Authlib lo intercambia por el `access_token` y los datos del usuario
   (scopes: `openid email profile` + Drive/Calendar/Gmail).
3. El backend crea o busca al usuario en Postgres, guarda su
   `refresh_token` de Google **encriptado con Fernet** (para volver a pedir
   acceso a las APIs sin que el usuario reautorice cada vez), y genera **sus
   propios** JWT (access 15 min + refresh 30 días).
4. Redirige al frontend a `/oauth-callback?token=...&refresh=...`, donde Vue
   guarda esos tokens en `localStorage` y queda logueado.

También existe `POST /api/auth/google/token` como alternativa para flujos
donde el frontend ya obtuvo un `id_token` directamente del SDK de Google
(botón "Sign in with Google" renderizado en el cliente).

**Nota sobre cookies:** las cookies de sesión de Flask (`config.py`) solo se
usan unos segundos durante el intercambio con Google, para guardar el
`state` anti-CSRF. La sesión del usuario dentro de la app se mantiene con
**JWT en localStorage**, no con cookies.

---

## Por qué dos bases de datos

| | PostgreSQL (Supabase) | MongoDB |
|---|---|---|
| **Qué guarda** | usuarios, roles, ubicaciones, reservas, pagos, facturas, reseñas, puntos | productos, categorías |
| **Por qué ahí** | Datos **transaccionales y relacionales**: una reserva referencia a un usuario, una ubicación y un pago; necesitan integridad referencial (`ForeignKey`), transacciones ACID y consultas con `JOIN` (ej. "reservas de un usuario con su ubicación de recojo") | Catálogo con **estructura variable**: cada producto puede tener campos distintos según categoría, imágenes múltiples, atributos libres; no necesita relaciones estrictas y se beneficia de esquema flexible |
| **Ejemplo del problema que resolvería la BD equivocada** | Meter reservas/pagos en Mongo complicaría validar que no haya dos reservas solapadas para el mismo producto sin transacciones fuertes | Forzar productos a un esquema fijo de SQL obligaría a migraciones cada vez que se agregue un atributo nuevo a una categoría |

En resumen: **Postgres para lo que necesita consistencia e integridad
(dinero, reservas, usuarios)**, **Mongo para lo que necesita flexibilidad de
esquema (catálogo de productos)**. Es un patrón de **persistencia
poliglota**, común cuando conviven datos muy estructurados con datos muy
variables en el mismo sistema.

El backend inicializa ambas conexiones en `app/__init__.py`: SQLAlchemy
(`db.init_app(app)`) para Postgres y `pymongo.MongoClient` para Mongo,
expuestas globalmente como `db` y `mongo_db`.

---

## Cómo correr el proyecto

### Requisitos

- Python 3.11
- Node.js 20
- Una base PostgreSQL (ej. proyecto en [Supabase](https://supabase.com))
- Una base MongoDB (ej. cluster en [MongoDB Atlas](https://www.mongodb.com/atlas))
- Credenciales OAuth de Google ([Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials)

### 1. Backend (Flask)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copia `.env.example` a `.env` y completa los valores:

```powershell
copy .env.example .env
```

Variables clave a completar en `.env`:

| Variable | De dónde sale |
|---|---|
| `SECRET_KEY` / `JWT_SECRET_KEY` | cualquier string largo aleatorio |
| `DATABASE_URL` | connection string de tu proyecto Postgres/Supabase |
| `MONGO_URI` | connection string de tu cluster MongoDB |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Google Cloud Console → Credentials → OAuth 2.0 Client ID |
| `ENCRYPTION_KEY` | generar con: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| `BACKEND_URL` | `http://127.0.0.1:5000` en local |
| `FRONTEND_URL` | `http://localhost:5173` en local |

⚠️ En Google Cloud Console, el **Authorized redirect URI** debe ser
exactamente `http://127.0.0.1:5000/api/auth/google/callback` (o el
equivalente en producción) — si no coincide con `BACKEND_URL`, falla el
login con Google.

Levantar el servidor:

```powershell
python run.py
```

Esto crea las tablas de Postgres automáticamente (`db.create_all()`) y
siembra los roles `cliente`/`rentador` si no existen. Backend corriendo en
`http://127.0.0.1:5000`.

### 2. Frontend (Vue)

En otra terminal:

```powershell
cd frontend
npm install
copy .env.example .env
```

En `frontend/.env`, para desarrollo local usa:

```
VITE_API_URL=http://127.0.0.1:5000/api
```

Levantar:

```powershell
npm run dev
```

Frontend corriendo en `http://localhost:5173`, ya conectado al backend local.

### 3. Probar los endpoints sin frontend

Usa la colección de Postman (`postman_collection.json`) — importa el archivo
en Postman, corre **Auth → Login/Register** primero (guarda el token
automáticamente) y ya puedes probar el resto de endpoints.

---

## Estructura de carpetas

```
backend/
  app/
    models/        → un archivo por entidad (SQLAlchemy) + mongo_models.py
    routes/         → un Blueprint por entidad, registrados en __init__.py
    __init__.py      → create_app(): conecta Postgres+Mongo, CORS, JWT, OAuth
    config.py        → toda la configuración vía variables de entorno
    oauth.py          → registro del cliente OAuth de Google + encriptación de tokens
    google_api.py      → helpers para usar Drive/Calendar/Gmail a nombre del usuario
  run.py
  requirements.txt
  render.yaml

frontend/
  src/
    views/          → una pantalla por ruta (Home, Login, PublishProduct...)
    services/         → llamadas a la API, una por entidad
    stores/            → Pinia (auth.js)
    router/             → rutas + guards de auth/rol
  package.json
```

---

## Deploy

El proyecto está pensado para **un solo servicio en Render**: `render.yaml`
en la raíz define un build (`backend/build.sh`) que instala el backend,
**además compila el frontend con Vite** y copia el resultado dentro de
`backend/app/static/dist/`, donde Flask lo sirve como SPA (ver la ruta
`serve_spa` en `app/__init__.py`).

Variables de entorno a configurar en el panel de Render (las mismas del
`.env` del backend): `SECRET_KEY`, `DATABASE_URL`, `MONGO_URI`,
`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `JWT_SECRET_KEY`,
`ENCRYPTION_KEY`, `BACKEND_URL`, `FRONTEND_URL` (en este modo, `BACKEND_URL`
y `FRONTEND_URL` normalmente apuntan al mismo dominio de Render).

No olvides agregar la URL final de Render como **Authorized redirect URI**
en Google Cloud Console:
`https://tu-app.onrender.com/api/auth/google/callback`.
