# Sistema de Gestion y Alquiler de Productos - Frontend

Frontend en **Vue 3 + Vite**, conectado al backend Flask del proyecto (`sistema_prestamos_backend`).

## Requisitos

- Node.js 18+
- El backend corriendo (por defecto en `http://127.0.0.1:5000`)
- **Importante:** el backend necesita `flask-cors` habilitado para aceptar peticiones desde este frontend (ver nota abajo).

## Instalación

```bash
npm install
cp .env.example .env
npm run dev
```

La app queda en `http://localhost:5173`.

## Variables de entorno

- `VITE_API_URL`: URL base de la API del backend (por defecto `http://127.0.0.1:5000/api`).

## Estructura

```
src/
  services/     # clientes axios por recurso (products, reservations, favorites, locations, users, api)
  stores/       # Pinia: estado de autenticacion (token + usuario en localStorage)
  router/       # rutas y guard de autenticacion
  views/        # paginas: Login, Registro, Home (catalogo), Detalle de producto,
                # Publicar producto, Mis reservas, Favoritos, Perfil
  components/   # NavBar, ProductCard
```

## Flujo cubierto

- Registro / login (JWT guardado en localStorage, enviado como `Authorization: Bearer <token>`).
- Listado de productos por categoria (con paginacion) y detalle de producto.
- Crear reserva desde el detalle de un producto.
- Publicar un producto propio.
- Ver/cancelar mis reservas, ver/quitar favoritos, editar perfil.

## Pendiente para conectar 100% con el backend actual

1. Agregar `flask-cors` al backend:
   ```python
   from flask_cors import CORS
   CORS(app, supports_credentials=True, origins=["http://localhost:5173"])
   ```
2. El endpoint de favoritos (`POST /favorites`) y otros CRUD secundarios (locations, payments, invoices, reviews, points, user-roles) no se leyeron campo por campo; revisa el `error` que devuelva la API la primera vez que los uses desde el formulario y ajusta el payload en `src/services/*.js` si el backend espera otros nombres de campo.
3. Login con Google (`/api/auth/google/...`) no esta integrado en el frontend todavia; se dejo solo login/registro con email y contraseña.

## Login con Google (OAuth 2.0)

El frontend usa el flujo de redireccion que ya expone el backend:

1. El boton "Continuar con Google" hace `window.location.href = \`${VITE_API_URL}/auth/google/login\``.
2. El backend redirige a Google, Google vuelve a `GET /api/auth/google/callback`.
3. El backend crea/vincula el usuario, genera un JWT y redirige a `\`${FRONTEND_URL}/oauth-callback?token=...\``.
4. `OAuthCallbackView.vue` toma ese `token`, lo guarda y llama a `GET /auth/me` para completar la sesion, luego redirige a inicio.

Para que esto funcione en el backend (Flask) agrega en su `.env`:

```env
FRONTEND_URL=http://localhost:5173
```

y asegurate de que `http://127.0.0.1:5000/api/auth/google/callback` este registrado como *Authorized redirect URI* en las credenciales OAuth de Google Cloud Console.
