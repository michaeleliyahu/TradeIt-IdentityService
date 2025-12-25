# Identity Service

## Project Structure

```
identity-service/
├── app/
│   ├── api/
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── health.py        # Health check endpoint
│   │       └── auth.py          # Register & Login endpoints
│   ├── core/
│   │   ├── config.py            # Settings management
│   │   └── security.py          # Password hashing & JWT tokens
│   ├── db/
│   │   ├── base.py              # SQLAlchemy base model
│   │   └── database.py          # Database session & connection
│   ├── models/
│   │   └── user.py              # User ORM model
│   ├── repositories/
│   │   └── user.py              # Database access layer
│   ├── schemas/
│   │   └── user.py              # Request/response schemas
│   ├── services/
│   │   └── user.py              # Business logic layer
│   └── main.py                  # FastAPI application
├── migrations/                   # Alembic migrations
│   └── versions/
│       └── 001_initial.py
├── tests/                        # Unit tests
├── .env.example                  # Environment template
├── Dockerfile                    # Container image
├── docker-compose.yml            # Multi-container setup
├── requirements.txt              # Python dependencies
├── run.py                        # Local development runner
└── README.md
```

## Architecture Overview

### 1. **API Layer** (`app/api/routers/`)
- **Purpose:** HTTP endpoints and request handling
- **Components:**
  - `auth.py`: Register, Login, Get User endpoints
  - `health.py`: Service health check
- **Responsibility:** Route requests to services, validate input, return responses

### 2. **Service Layer** (`app/services/`)
- **Purpose:** Business logic and orchestration
- **Key Methods:**
  - `register_user()`: Registration flow
  - `login_user()`: Login flow with password verification
  - `get_user_details()`: Fetch user info
- **Responsibility:** Implement workflows, call repositories, handle errors

### 3. **Repository Layer** (`app/repositories/`)
- **Purpose:** Database abstraction and queries
- **Key Methods:**
  - `create_user()`: Insert user
  - `get_user_by_email()`: Query by email
  - `get_user_by_id()`: Query by ID
- **Responsibility:** SQL operations, data persistence

### 4. **Models** (`app/models/`)
- **Purpose:** SQLAlchemy ORM models
- **User Model:** Email, username, hashed_password, timestamps
- **Responsibility:** Database table schema

### 5. **Schemas** (`app/schemas/`)
- **Purpose:** Pydantic validation for requests/responses
- **Key Schemas:**
  - `UserRegisterRequest`: email, username, password
  - `UserLoginRequest`: email, password
  - `TokenResponse`: access_token, refresh_token
  - `UserResponse`: User details
- **Responsibility:** Input/output validation

### 6. **Core** (`app/core/`)
- **config.py:** Centralized settings from environment
- **security.py:** Password hashing (`PasswordUtil`) and JWT management (`TokenUtil`)

### 7. **Database** (`app/db/`)
- **database.py:** Async SQLAlchemy engine and session factory
- **base.py:** SQLAlchemy declarative base

## Register → Login Flow

### Registration Flow
```
1. Client POST /auth/register
   ├─ UserRegisterRequest validation (email, username, password)
   │
2. API Router → Service
   ├─ Check email uniqueness
   ├─ Check username uniqueness
   │
3. Service → Repository
   ├─ Hash password using bcrypt (PasswordUtil.hash_password)
   ├─ Create user in database
   │
4. Service generates tokens
   ├─ Access token (15 min expiry)
   ├─ Refresh token (7 day expiry)
   │
5. Return TokenResponse
   └─ Client receives tokens to use in subsequent requests
```

### Login Flow
```
1. Client POST /auth/login
   ├─ UserLoginRequest validation (email, password)
   │
2. API Router → Service
   ├─ Fetch user by email
   ├─ Verify password (PasswordUtil.verify_password)
   ├─ Check is_active status
   │
3. Service generates tokens
   ├─ Access token (15 min expiry)
   ├─ Refresh token (7 day expiry)
   │
4. Return TokenResponse
   └─ Client receives tokens
```

## Key Features

### Security
- **Password Hashing:** Bcrypt with automatic salt (passlib)
- **JWT Tokens:** RS256 algorithm, configurable expiry
- **Token Types:** Access (short-lived), Refresh (long-lived)

### Database
- **ORM:** SQLAlchemy 2.0 with async support
- **Database:** PostgreSQL with UUID primary keys
- **Migrations:** Alembic versioning

### Best Practices
- **Layered Architecture:** Clean separation of concerns
- **Dependency Injection:** FastAPI Depends for session management
- **Environment Config:** Settings from .env file
- **Error Handling:** Custom exceptions with appropriate HTTP status codes
- **API Documentation:** Auto-generated OpenAPI (Swagger UI at `/docs`)

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment
```bash
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Run Migrations
```bash
alembic upgrade head
```

### 4. Start Service
```bash
python run.py
```

### 5. Access API
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## Docker Deployment

### Build & Run
```bash
docker-compose up --build
```

### Run Migrations in Container
```bash
docker-compose exec identity-service alembic upgrade head
```

## API Examples

### Register
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "john_doe",
    "password": "SecurePass123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

### Get User
```bash
curl -X GET http://localhost:8000/auth/users/{user_id}
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `JWT_SECRET_KEY` | Secret key for JWT signing | Required (production) |
| `JWT_ALGORITHM` | JWT algorithm | RS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | 15 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | 7 |
| `DEBUG` | Enable debug mode | False |

## Microservices Integration

This service is designed as an independent microservice:
- **Isolated Database:** Fully separate PostgreSQL instance
- **Independent Ports:** Runs on port 8000 by default
- **Service Discovery:** Ready for Kubernetes/Consul integration
- **Health Checks:** `/health` endpoint for load balancers

## Future Enhancements

- [ ] OAuth2 integration
- [ ] Email verification
- [ ] Two-factor authentication (2FA)
- [ ] Rate limiting
- [ ] Audit logging
- [ ] Public/private key rotation for JWT
- [ ] Token revocation list (blacklist)
