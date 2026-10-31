# AI Inventory Platform: API

Backend for an AI-native inventory & operations platform: products, warehouses, stock movements, RBAC, and AI features (natural-language search, RAG, approval-gated agents).

**Stack:** Python 3.14 · FastAPI · Pydantic v2 · SQLAlchemy 2.0 (async) · PostgreSQL · uv

## Run locally
```bash
cp .env.example .env            # then set a real POSTGRES_PASSWORD
docker compose up -d            # PostgreSQL 18 + pgvector on localhost:5434
uv sync
uv run alembic upgrade head     # apply database migrations
uv run fastapi dev src/app/main.py
```
- Liveness: http://127.0.0.1:8000/health
- Readiness (checks the database): http://127.0.0.1:8000/health/ready
- API docs: http://127.0.0.1:8000/docs

## Quality checks
```bash
uv run ruff check          # lint
uv run ruff format --check # formatting
uv run mypy                # strict type checking
uv run pytest              # tests
```

## Architecture
Modular monolith: feature modules with clean layering (router → service → repository). See [docs/adr](docs/adr).
