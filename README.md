# Sistema de Préstamos / Alquiler de Productos

Plataforma full-stack para publicar, buscar y alquilar productos, gestionar
reservas, favoritos, reseñas, pagos y ubicaciones. Incluye autenticación con
email/contraseña (JWT) y login con Google (OAuth 2.0).

---

## Arquitectura

```
ProyectoConstruccion/
├── backend/     # API REST en Flask (Python)
└── frontend/    # SPA en Vue 3 + Vite
```

- **Frontend** y **Backend** se despliegan como servicios **separados**.
- El frontend consume la API vía `VITE_API_URL`.
- El backend usa **PostgreSQL** (datos relacionales) + **MongoDB** (catálogo/categorías).

---

## Stack tecnológico

### Backend (Flask)
- Flask 3, Flask-REST (blueprints), Flask-SQLAlchemy, Flask-JWT-Extended
- PostgreSQL (`psycopg2`) + MongoDB (`pymongo`)
- Authlib (OAuth 2.0 con Google)
- Flask-CORS, gunicorn (producción)
- Google API client (Drive, Calendar, Gmail) para integraciones opcionales

### Frontend (Vue 3)
- Vue 3 + Vite, Vue Router 4 (`createWebHistory`)
- Pinia (estado de autenticación)
- Axios (cliente HTTP con interceptor de JWT y refresh automático)

---

## Puesta en marcha en local

### 1. Backend

```bash
cd backend
python -m venv venv
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux/Mac:
# source venv/bin/activate

pip install -r requirements.txt
cp app/.env.example app/.env   # crea app/.env con tus valores
python run.py
```

El backend queda en `http://127.0.0.1:5000`.

Variables de entorno del backend (`backend/app/.env`):

| Variable | Descripción |
|----------|-------------|
| `SECRET_KEY` | Clave secreta de Flask |
| `JWT_SECRET_KEY` | Clave para firmar JWT (puede igual a SECRET_KEY) |
| `DATABASE_URL` | URL de PostgreSQL (Supabase, Render, local, etc.) |
| `MONGO_URI` | URI de conexión a MongoDB |
| `GOOGLE_CLIENT_ID` | Client ID de Google Cloud OAuth |
| `GOOGLE_CLIENT_SECRET` | Client Secret de Google Cloud OAuth |
| `ENCRYPTION_KEY` | Clave Fernet (44 chars) para encriptar refresh_token de Google |
| `BACKEND_URL` | URL pública fija del backend (usada en `redirect_uri`) |
| `FRONTEND_URL` | Origen del frontend (adonde redirige tras login con Google) |

Genera `ENCRYPTION_KEY` con:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env   # define VITE_API_URL
npm run dev
```

El frontend queda en `http://localhost:5173`.

Variables de entorno del frontend (`frontend/.env`):

| Variable | Descripción |
|----------|-------------|
| `VITE_API_URL` | Base URL de la API (ej. `http://127.0.0.1:5000/api` en local) |

---

## Configuración de Google OAuth 2.0

1. En **Google Cloud Console → Credenciales → OAuth 2.0 Client ID**, añade la
   **Authorized redirect URI** exactamente igual a:

   ```
   {BACKEND_URL}/api/auth/google/callback
   ```

   - Local: `http://127.0.0.1:5000/api/auth/google/callback`
   - Render: `https://<tu-backend>.onrender.com/api/auth/google/callback`

2. Usa **`127.0.0.1`**, no `localhost` (Google los trata como orígenes distintos).

3. El flujo: frontend → `GET /api/auth/google/login` → Google →
   `GET /api/auth/google/callback` (backend intercambia el `code`, crea/obtiene
   el usuario, emite JWT propios) → redirige a
   `{FRONTEND_URL}/oauth-callback?token=...&refresh=...` → Vue completa la sesión.

---

## Estructura del backend

```
backend/
├── run.py                  # Arranque de la app (Flask)
├── requirements.txt
├── app/
│   ├── __init__.py         # create_app(): CORS, JWT, DB, OAuth, registro de blueprints
│   ├── config.py           # Configuración y variables de entorno
│   ├── oauth.py            # Cliente OAuth de Google (Authlib)
│   ├── models/             # user, role, reservation, review, payment, invoice,
│   │                       # location, favorite, point, mongo_models (categorías)
│   ├── routes/             # Un blueprint por recurso:
│   │                       # auth, google_auth, product, reservation, favorite,
│   │                       # location, payment, invoice, review, point, user, user_role
│   └── static/uploads/products/  # Imágenes subidas
```

### Principales endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/register` | Registro con email/contraseña |
| POST | `/api/auth/login` | Login (devuelve access + refresh JWT) |
| GET | `/api/auth/me` | Datos del usuario autenticado |
| POST | `/api/auth/refresh` | Renovar access token |
| GET | `/api/auth/google/login` | Iniciar login con Google |
| GET | `/api/auth/google/callback` | Callback de Google (retorna JWT al frontend) |
| POST | `/api/auth/google/token` | Login con Google vía `id_token` (SDK cliente) |
| GET | `/api/products` | Listado de productos (paginado, por categoría) |
| GET | `/api/products/<id>` | Detalle de producto |
| POST | `/api/products` | Publicar producto (auth) |
| POST | `/api/reservations` | Crear reserva (auth) |
| GET | `/api/reservations` | Mis reservas |
| POST | `/api/favorites` | Agregar a favoritos (auth) |
| GET | `/api/favorites` | Mis favoritos |
| GET/POST | `/api/reviews`, `/api/payments`, `/api/invoices`, `/api/locations`, `/api/points` | CRUD de cada recurso |
| GET/POST | `/api/user-roles` | Asignar/consultar roles (cliente, rentador, admin) |

---

## Estructura del frontend

```
frontend/
├── index.html
├── static.json            # SPA fallback para Render (reescribe /* -> /index.html)
├── src/
│   ├── main.js
│   ├── App.vue
│   ├── router/index.js    # Rutas (history mode) + guard de auth
│   ├── stores/auth.js     # Pinia: login, logout, refresh, fetchMe
│   ├── services/          # Clientes axios: api, auth, products, reservations,
│   │                       # favorites, locations, users
│   ├── views/             # Login, Registro, Home, ProductDetail, PublishProduct,
│   │                       # MyProducts, Reservations, Favorites, Profile, OAuthCallback
│   └── components/        # NavBar, ProductCard
```

---

## Despliegue en Render (producción)

### Backend (Web Service)
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn run:app` (ejecutar desde `backend/`)
- **Environment:**
  ```
  BACKEND_URL=https://<tu-backend>.onrender.com
  FRONTEND_URL=https://<tu-frontend>.onrender.com
  DATABASE_URL=...
  MONGO_URI=...
  GOOGLE_CLIENT_ID=...
  GOOGLE_CLIENT_SECRET=...
  ENCRYPTION_KEY=...
  SECRET_KEY=...
  JWT_SECRET_KEY=...
  ```

### Frontend (Static Site)
- **Build Command:** `npm run build`
- **Publish Directory:** `dist`
- `static.json` ya configura el **SPA fallback** (`/*` → `/index.html`),
  necesario para que rutas como `/oauth-callback` funcionen con recarga directa.
- **Environment:** `VITE_API_URL=https://<tu-backend>.onrender.com/api`

### Google Cloud Console
- Authorized redirect URI: `https://<tu-backend>.onrender.com/api/auth/google/callback`

---

## Notas importantes

- **SPA fallback:** el frontend usa `createWebHistory()`. En producción el host
  debe reescribir rutas desconocidas a `index.html`; `frontend/static.json`
  lo hace en Render. Sin esto, el callback de Google (`/oauth-callback`) da 404.
- **CORS:** el backend habilita CORS solo para `FRONTEND_URL`.
- **HTTPS en producción:** `SESSION_COOKIE_SECURE = True` y `PREFERRED_URL_SCHEME = "https"`.
- **Roles:** al registrarse se asigna `cliente`; `rentador` se activa desde el perfil.
```
