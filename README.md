# LockApp Backend

A FastAPI backend for LockApp that handles user accounts with JWT authentication and lets you create and manage database tables at runtime. You define a table's columns through the API, the server creates the table, records its schema in a registry, and you can then insert rows into it and read them back.

## Features

- **User accounts**: sign up, log in, view your profile, change your password, delete your account
- **JWT auth**: OAuth2 password flow with HS256-signed bearer tokens that expire after 30 minutes
- **Password hashing**: Argon2 by default, with bcrypt hashes still accepted (via `pwdlib`)
- **Superuser role**: only superusers can list all users
- **Dynamic tables**: create tables from a JSON column definition, list them, delete them
- **Table registry**: every created table's schema is stored in `table_registry`
- **Default table**: mark one table as the default so the frontend can fetch its columns and rows directly
- **Bulk row insert**: insert many rows at once, checked against the registered columns

## Tech Stack

| Layer | Tool |
|---|---|
| Framework | FastAPI + Uvicorn |
| ORM / DB | SQLAlchemy, SQLite |
| Validation & settings | Pydantic, pydantic-settings, python-dotenv |
| Auth | PyJWT, pwdlib (Argon2 / bcrypt) |

## Project Structure

```
LockApp_backend/
├── app/
│   ├── main.py            # App entry point: CORS, table creation, routers
│   ├── models.py          # SQLAlchemy models: User, TableRegistery
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── crud.py            # User lookup, creation, authentication
│   ├── api/
│   │   ├── main.py        # Combines all route modules
│   │   ├── deps.py        # Current-user and superuser dependencies
│   │   ├── ddl_helper.py  # Builds CREATE TABLE statements, type mapping
│   │   └── routes/
│   │       ├── login.py   # POST /login
│   │       ├── users.py   # /signup, /me, /admin
│   │       └── tables.py  # /tables endpoints
│   └── core/
│       ├── config.py      # Settings loaded from .env
│       ├── db.py          # Engine, session, get_db dependency
│       └── security.py    # Password hashing, token creation
└── requirements.txt
```

## Getting Started

### Prerequisites

- Python 3.10 or newer

### 1. Clone and install

```bash
git clone https://github.com/SwaroopSyriack/LockApp_backend.git
cd LockApp_backend

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
pip install "pydantic[email]" passlib   # needed by the code but not yet in requirements.txt
```

### 2. Configure environment

Create a `.env` file in the project root:

```env
SECRET_KEY="replace-with-a-long-random-string"
DB_URL="sqlite:///./test.db"
```

You can generate a secret key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

| Variable | Description |
|---|---|
| `SECRET_KEY` | Key used to sign JWT access tokens |
| `DB_URL` | SQLAlchemy database URL (SQLite is what the code is written for) |

### 3. Run the server

```bash
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. The database tables are created on startup.

Interactive docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

CORS is set to allow `http://localhost:5173` (the default Vite dev server). Edit `origins` in `app/main.py` to add other frontends.

## API Reference

### Authentication

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/login` | – | Log in with form fields `username` (your email) and `password`. Returns `access_token`, `token_type`, `username`. |

Send the token on protected routes as:

```
Authorization: Bearer <access_token>
```

### Users

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/signup` | – | Register a new user |
| GET | `/me` | User | Get the current user's profile |
| PATCH | `/me` | User | Change password (`current_password`, `new_password`) |
| DELETE | `/me` | User | Delete your account (superusers can't delete themselves) |
| GET | `/admin` | Superuser | List all users, newest first |
| POST | `/admin` | – | Create a user, optionally with `is_superuser: true` |

Passwords must be 8–128 characters.

### Tables

| Method | Endpoint | Description |
|---|---|---|
| POST | `/tables` | Create a table and register it |
| GET | `/tables` | List all registered tables |
| GET | `/tables/default` | Get the default table |
| GET | `/tables/rows` | Get all rows of the default table |
| GET | `/tables/{table_id}` | Get one table's details |
| GET | `/tables/{table_id}/cols` | Get columns (only works for the default table) |
| PATCH | `/tables/{table_id}/default` | Make this table the default |
| DELETE | `/tables/{table_id}` | Drop the table and remove it from the registry |
| POST | `/tables/{table_id}/rows` | Bulk insert rows |

## Examples

**Sign up**

```bash
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "username": "swaroop", "password": "strongpass123"}'
```

**Log in**

```bash
curl -X POST http://localhost:8000/login \
  -d "username=user@example.com&password=strongpass123"
```

**Create a table**

```bash
curl -X POST http://localhost:8000/tables \
  -H "Content-Type: application/json" \
  -d '{
    "table_name": "lock_events",
    "display_name": "Lock Events",
    "columns": [
      {"column_name": "device", "data_type": "TEXT", "nullable": false},
      {"column_name": "locked", "data_type": "BOOLEAN", "nullable": true, "default_value": "0"},
      {"column_name": "event_time", "data_type": "TIMESTAMP", "nullable": true}
    ]
  }'
```

An auto-increment `id` primary key is added to every table. Table names must start with a letter or underscore, contain only letters, digits and underscores, and be at most 63 characters. Column names must be unique.

**Insert rows**

```bash
curl -X POST http://localhost:8000/tables/1/rows \
  -H "Content-Type: application/json" \
  -d '{
    "timedata": "2026-11-10T00:00:00",
    "data": [
      {"device": "front-door", "locked": 1, "event_time": "2026-11-10T08:00:00"},
      {"device": "back-door",  "locked": 0, "event_time": "2026-11-10T08:05:00"}
    ]
  }'
```

Each row should include every registered column; unknown columns are rejected.

### Supported column types

Column types are mapped to SQLite storage types:

| You send | Stored as |
|---|---|
| `TEXT`, `VARCHAR`, `CHAR`, `STRING`, `DATE`, `TIME`, `TIMESTAMP`, `DATETIME`, `UUID`, `JSON`, `JSONB` | `TEXT` |
| `INTEGER`, `INT`, `BIGINT`, `SMALLINT`, `BOOLEAN` | `INTEGER` |
| `FLOAT`, `DOUBLE`, `REAL` | `REAL` |
| `DECIMAL`, `NUMERIC` | `NUMERIC` |
| `BLOB` | `BLOB` |

## Roadmap

- Require authentication on the `/tables` routes and on `POST /admin`
- Block login for inactive users
- Rehash passwords automatically when a stronger algorithm is available
- Support databases other than SQLite
