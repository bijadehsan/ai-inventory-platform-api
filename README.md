# AI Inventory Platform: API

Backend for an AI-native inventory & operations platform: products, warehouses, stock movements, RBAC, and AI features (natural-language search, RAG, approval-gated agents).

**Stack:** Python 3.14 · FastAPI · Pydantic v2 · SQLAlchemy 2.0 (async) · PostgreSQL · uv

## Run locally
```bash
uv sync
uv run fastapi dev src/app/main.py
```
- Health check: http://127.0.0.1:8000/health
- API docs: http://127.0.0.1:8000/docs

## Architecture
Modular monolith: feature modules with clean layering (router → service → repository). See [docs/adr](docs/adr).
