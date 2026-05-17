# AB Comercial API

Backend para la prueba tecnica full stack de AB Comercial. Expone autenticacion JWT, control de roles y CRUD de vehiculos para alimentar la tabla del concesionario del frontend.

## Stack

- FastAPI
- SQLAlchemy async
- PostgreSQL con asyncpg
- Alembic
- JWT con python-jose
- Passlib + bcrypt
- Pytest + httpx + SQLite en memoria para tests

## Funcionalidad principal

- Login con JWT.
- Registro publico de usuarios `viewer`.
- Creacion administrativa de usuarios.
- Roles `admin` y `viewer`.
- CRUD de vehiculos protegido por RBAC.
- Respuestas consistentes con `success`, `message`, `data` y `errors`.
- Manejo centralizado de errores y validaciones.
- Logging de peticiones HTTP en consola.
- Migraciones con Alembic.
- Seed con usuarios y datos demo.
- Configuracion lista para Render.

## Modelo de vehiculo

La tabla principal representa el caso pedido en la prueba:

```json
{
  "brand": "Toyota",
  "arrival_location": "Bogota",
  "applicant_name": "Laura Gomez"
}
```

Equivalencia con el enunciado:

- `brand`: marca de carro.
- `arrival_location`: localidad de llegada.
- `applicant_name`: aspirante al vehiculo.

## Variables de entorno

Copia `.env.example` a `.env` y ajusta los valores segun tu entorno.

```bash
copy .env.example .env
```

Variables principales:

| Variable | Descripcion |
| --- | --- |
| `APP_NAME` | Nombre mostrado en Swagger/OpenAPI. |
| `ENVIRONMENT` | Entorno actual: `local`, `staging` o `production`. |
| `DEBUG` | Activa o desactiva modo debug. En produccion debe ser `false`. |
| `API_V1_PREFIX` | Prefijo de la API, por defecto `/api/v1`. |
| `DATABASE_URL` | URL de conexion a PostgreSQL. |
| `SECRET_KEY` | Clave privada para firmar JWT. Debe ser larga y secreta. |
| `ALGORITHM` | Algoritmo JWT, por defecto `HS256`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tiempo de vida del token. |
| `CORS_ORIGINS` | Origenes permitidos separados por coma. |
Ejemplo local de `DATABASE_URL`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dbp_ab_comercial
```

## Instalacion local

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Aplica migraciones y carga datos demo:

```bash
alembic upgrade head
python -m scripts.seed
```

Levanta la API:

```bash
uvicorn app.main:app --reload
```

Swagger queda disponible en:

```text
http://localhost:8000/docs
```

## Credenciales demo

```text
admin / Admin12345
viewer / Viewer12345
```

El rol `viewer` puede consultar vehiculos. El rol `admin` consultar, crear, editar y eliminar.

## Endpoints

```text
GET    /health
POST   /api/v1/auth/login
POST   /api/v1/auth/register
POST   /api/v1/auth/users
GET    /api/v1/vehicles
GET    /api/v1/vehicles/{vehicle_id}
POST   /api/v1/vehicles
PATCH  /api/v1/vehicles/{vehicle_id}
DELETE /api/v1/vehicles/{vehicle_id}
```

Notas:

- `POST /api/v1/auth/register` es publico y siempre crea usuarios `viewer`.
- `POST /api/v1/auth/users` requiere token de `admin` y permite definir rol.
- Los endpoints de vehiculos requieren `Authorization: Bearer <token>`.
- Crear, editar y eliminar vehiculos requiere rol `admin`.

El login usa form-data compatible con OAuth2:

```text
username=admin
password=Admin12345
```

Para consumir endpoints protegidos:

```http
Authorization: Bearer <token>
```

## Postman

La coleccion esta en:

```text
postman/AB Comercial API.postman_collection.json
```

Para importarla:

1. Abre Postman.
2. Haz clic en `Import`.
3. Selecciona `files`.
4. Carga el archivo `postman/AB Comercial API.postman_collection.json`.
5. Verifica que la variable `base_url` apunte a tu API local o desplegada.

Variables incluidas:

- `base_url`
- `access_token`
- `vehicle_id`
- `admin_username`
- `admin_password`
- `new_viewer_username`
- `new_viewer_password`

Flujo recomendado:

1. Ejecuta `Login Admin`.
2. Ejecuta `Crear Vehiculo`.
3. Usa `Obtener`, `Actualizar` o `Eliminar Vehiculo` con el `vehicle_id` guardado.

## Tests

Los tests no dependen de PostgreSQL. Usan SQLite en memoria y cubren autenticacion, RBAC, validaciones, errores 404 y flujo CRUD principal.

```bash
cd backend
python -B -m pytest
```

Resultado esperado:

```text
19 passed
```

## Docker Opcional

Este backend puede ejecutarse con Docker desde un repositorio opcional que orquesta backend y frontend juntos:

```text
Configura aqui el link publico del repositorio Docker si decides publicarlo.
```

Si PostgreSQL corre en tu maquina y el backend corre en Docker, usa `host.docker.internal` en `DATABASE_URL`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@host.docker.internal:5432/dbp_ab_comercial
```

Para cargar datos demo con Docker:

```bash
docker compose --profile tools run --rm seed
```

El contenedor del backend mantiene el `CMD` del `Dockerfile` para iniciar `uvicorn`. Docker Compose usa un servicio separado `migrate` para aplicar migraciones antes del arranque.

El repositorio Docker es un plus de desarrollo local. La entrega principal se mantiene separada entre backend y frontend para conservar responsabilidades y despliegues independientes.

## Deploy en Render

El archivo `render.yaml` crea el Web Service y la base PostgreSQL.

Comandos usados por Render:

```text
Build command: pip install -r requirements.txt
Start command: alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Variables importantes:

```text
APP_NAME
ENVIRONMENT
DEBUG
API_V1_PREFIX
DATABASE_URL
SECRET_KEY
ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES
CORS_ORIGINS
```

Despues del primer deploy, ejecuta una vez:

```bash
python -m scripts.seed
```
