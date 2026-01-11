# Identity Service

Short description: FastAPI service for user registration, login, and issuing JWT access/refresh tokens.

## 🎯 Responsibilities
- Register users, verify credentials, issue JWT access/refresh tokens
- Store user records in PostgreSQL
- Expose auth-related REST endpoints

Out of scope:
- ❌ Content/post logic
- ❌ Feed/notifications
- ❌ Likes/comments

## 🏗️ Architecture
- Framework: FastAPI (async)
- Architecture: Layered (routers → services → repositories → DB/models)
- Layers:
   - api/routers (auth, health)
   - services (userService)
   - repositories (usreRepository)
   - models (SQLAlchemy `user` with UUID PK)
   - schemas (Pydantic request/response)
   - core (config, security)

Folder sketch:
```
identity-service/
├─ app/
│  ├─ api/routers/ (auth, health)
│  ├─ core/ (config, security)
│  ├─ db/ (base, database)
│  ├─ models/ (user.py)
│  ├─ repositories/ (usreRepository.py)
│  ├─ schemas/ (user.py)
│  ├─ services/ (userService.py)
│  └─ main.py
└─ migrations/, tests/, run.py, Dockerfile, docker-compose.yml
```

## 🔌 External Dependencies
- PostgreSQL
- (Optional) Email provider for future verification

## 🔄 Service Communication
- Publisher: none (no events published)
- Consumer: none (auth is self-contained)

## 🌐 REST APIs (Overview)
- `POST /auth/register` — register and receive tokens
- `POST /auth/login` — login and receive tokens
- `GET  /auth/users/{user_id}` — fetch user details (currently unauthenticated; secure via gateway in production)
- `GET  /health`

## ⚙️ Environment (.env)
- `DATABASE_URL` (e.g., postgresql+asyncpg://user:pass@host:5432/identity_db)
- `JWT_SECRET_KEY` (HS256 default key)
- `JWT_ALGORITHM` (default `HS256` — code currently uses HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (default `15`)
- `REFRESH_TOKEN_EXPIRE_DAYS` (default `7`)
- `DEBUG`
- `.env.example` may be missing; create manually if absent

## ▶️ Local Run
```bash
pip install -r requirements.txt
cp .env.example .env   # create if missing
alembic upgrade head
python run.py
```

## Docker
```bash
docker-compose up --build
docker-compose exec identity-service alembic upgrade head
```

## 🧪 Tests
- Tests folder exists; add `pytest` as needed (no suite documented here)

## 🧠 Notes / Design Decisions
- HS256 by default; switch to RS256 only if you supply key pairs
- Password hashing via `bcrypt_sha256` for stronger hashing without 72-byte limit
- UUID primary keys for users
- `GET /auth/users/{user_id}` is open in code—ensure it is protected by the gateway or add JWT validation if exposed directly

## 🔐 Authentication Model
- JWTs issued by this Identity Service
- Algorithm: HS256 (default in code)
- Claims: `sub` = user_id, plus `exp`, `iat`, `type` (access/refresh)
- Downstream services validate tokens locally using the shared signing key; no per-request call back to Identity Service

## Future Enhancements
- [ ] OAuth2 integration
- [ ] Email verification
- [ ] Two-factor authentication (2FA)
- [ ] Rate limiting
- [ ] Audit logging
- [ ] Key rotation for JWT
- [ ] Token revocation list (blacklist)
