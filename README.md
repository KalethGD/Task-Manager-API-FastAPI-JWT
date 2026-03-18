# Task Manager API — FastAPI + JWT

API REST para gestión de tareas con autenticación JWT, sistema de refresh tokens y panel de administración web.

---

## Tecnologías

- **Backend:** Python, FastAPI, SQLAlchemy
- **Base de datos:** PostgreSQL
- **Autenticación:** JWT (access token + refresh token con rotación)
- **Seguridad:** bcrypt, python-jose
- **Tests:** Pytest, HTTPX
- **Frontend:** HTML, Tailwind CSS, JavaScript (Vanilla)

---

## Características

- Registro e inicio de sesión de usuarios
- Roles: `user` y `admin`
- Sistema de doble token:
    - **Access token** — duración 15 minutos, se envía en cada request
    - **Refresh token** — duración 7 días, renueva el access token automáticamente
    - **Rotación de tokens** — cada refresh invalida el token anterior
- CRUD completo de tareas por usuario
- Panel de administración para gestionar usuarios y tareas
- Logout con revocación del refresh token en base de datos

---

## Estructura del proyecto

```
├── main.py                  # Punto de entrada, configuración de FastAPI
├── database.py              # Conexión a la base de datos
├── requirements.txt
├── .env                     # Variables de entorno (no incluido en el repo)
│
├── core/
│   ├── config.py            # Configuración general (Settings)
│   ├── security.py          # Funciones JWT y bcrypt
│   ├── dependencies.py      # Dependencias de FastAPI (get_current_user, etc.)
│   └── enum.py              # Enumeraciones (UserRole)
│
├── models/
│   ├── model_user.py        # Modelo User
│   ├── model_task.py        # Modelo Task
│   └── model_refresh_token.py  # Modelo RefreshToken
│
├── routers/
│   ├── router_auth.py       # /auth/login, /auth/refresh, /auth/logout
│   ├── router_user.py       # /users/...
│   └── router_task.py       # /tasks/...
│
├── schemas/
│   ├── schema_auth.py       # Schemas de autenticación
│   ├── schema_user.py       # Schemas de usuario
│   └── schema_task.py       # Schemas de tarea
│
├── services/
│   ├── service_user.py      # Lógica de negocio de usuarios
│   └── service_task.py      # Lógica de negocio de tareas
│
├── static/                  # Frontend
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── admin.html
│   └── js/
│       ├── utils.js         # fetchWithAuth, logout, helpers
│       ├── auth.js          # Lógica de login
│       ├── api.js           # Lógica del dashboard (tareas)
│       └── admin.js         # Lógica del panel admin
│
└── tests/
    ├── conftest.py
    ├── test_auth.py
    ├── test_user.py
    └── test_task.py
```

---

## Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd F-P-JWT
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / Mac

pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
DATABASE_URL=postgresql+psycopg://usuario:contraseña@localhost:5432/nombre_db
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

> **Nota:** `SECRET_KEY` debe ser una cadena larga y aleatoria. Puedes generarla con:
>
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### 4. Iniciar el servidor

```bash
uvicorn main:app --reload
```

El servidor estará disponible en `http://localhost:8000`.  
La documentación interactiva en `http://localhost:8000/docs`.

---

## Endpoints

### Autenticación — `/auth`

| Método | Endpoint        | Descripción                                   | Auth requerida         |
| ------ | --------------- | --------------------------------------------- | ---------------------- |
| `POST` | `/auth/login`   | Inicia sesión, retorna access + refresh token | No                     |
| `POST` | `/auth/refresh` | Renueva el par de tokens (con rotación)       | No (usa refresh token) |
| `POST` | `/auth/logout`  | Revoca el refresh token                       | No (usa refresh token) |

**Login — Request:**

```json
{
    "email": "usuario@email.com",
    "password": "contraseña"
}
```

**Login — Response:**

```json
{
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer"
}
```

---

### Usuarios — `/users`

| Método   | Endpoint              | Descripción               | Rol requerido              |
| -------- | --------------------- | ------------------------- | -------------------------- |
| `GET`    | `/users/`             | Listar todos los usuarios | Admin                      |
| `GET`    | `/users/me/profile`   | Ver perfil propio         | User / Admin               |
| `GET`    | `/users/{id}`         | Ver usuario por ID        | User (solo propio) / Admin |
| `POST`   | `/users/register`     | Registrar nuevo usuario   | No                         |
| `POST`   | `/users/create-admin` | Crear usuario admin       | Admin                      |
| `PATCH`  | `/users/update/{id}`  | Actualizar usuario        | Admin                      |
| `DELETE` | `/users/delete/{id}`  | Eliminar usuario          | Admin                      |

---

### Tareas — `/tasks`

| Método   | Endpoint                  | Descripción                                 | Auth requerida |
| -------- | ------------------------- | ------------------------------------------- | -------------- |
| `GET`    | `/tasks/get_tasks`        | Listar tareas (propias o todas si es admin) | Sí             |
| `GET`    | `/tasks/get_task/{id}`    | Ver tarea por ID                            | Sí             |
| `POST`   | `/tasks/create_task`      | Crear nueva tarea                           | Sí             |
| `PATCH`  | `/tasks/update_task/{id}` | Actualizar tarea                            | Sí             |
| `DELETE` | `/tasks/delete_task/{id}` | Eliminar tarea                              | Sí             |

---

## Cómo funciona el sistema de tokens

```
LOGIN
  └─► retorna access_token (15 min) + refresh_token (7 días)

REQUESTS NORMALES
  └─► se envía access_token en el header Authorization: Bearer <token>

ACCESS TOKEN EXPIRA
  └─► el frontend detecta el 401 automáticamente (fetchWithAuth)
  └─► llama a /auth/refresh con el refresh_token
  └─► recibe nuevo par de tokens
  └─► reintenta el request original
  └─► el usuario no percibe ninguna interrupción ✓

INACTIVIDAD > 7 DÍAS
  └─► refresh_token expirado → redirige al login

LOGOUT
  └─► el refresh_token se revoca en la base de datos
  └─► el access_token expira solo en ≤ 15 min
```

---

## Ejecutar tests

```bash
pytest tests/ -v
```

```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

---

## Variables de entorno — Referencia completa

| Variable                      | Descripción                  | Valor por defecto           |
| ----------------------------- | ---------------------------- | --------------------------- |
| `DATABASE_URL`                | URL de conexión a PostgreSQL | — (requerida)               |
| `SECRET_KEY`                  | Clave para firmar los JWT    | — (requerida en producción) |
| `ALGORITHM`                   | Algoritmo JWT                | `HS256`                     |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del access token    | `15`                        |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | Duración del refresh token   | `7`                         |
