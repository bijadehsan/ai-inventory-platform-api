# ADR 0001: Backend architecture: feature modules with light clean layering

- **Status:** accepted
- **Date:** 2026-10-27

## Context
The FastAPI backend will grow from products CRUD to stock, auth, audit and AI modules. We need a structure that:
- keeps business rules out of HTTP code and is testable;
- gives clear module boundaries (a modular monolith we can split later if needed);
- maps to familiar .NET Clean Architecture concepts without heavy ceremony.

FastAPI itself does not impose a structure.

## Options considered
| Option | How it works | Strengths | Weaknesses |
|---|---|---|---|
| 1. Layered by type | Top-level `routers/`, `services/`, `repositories/` | Simple, familiar | A feature gets scattered as the app grows; weak boundaries |
| 2. Feature modules | One package per feature, each with its own router/service/repo | Cohesive, clear boundaries, extractable | Needs internal rules or logic leaks into routers |
| 3. Full Clean/Hexagonal | `domain/application/infrastructure/api` + ports everywhere | Maximum isolation and testability | Heavy ceremony for a small team; over-engineering risk |
| 4. Django-style fat models | Logic in ORM models | Fast to start | Business logic coupled to the ORM |

## Decision
**Option 2 + 3 (light):** feature modules on the outside, clean layers inside each module.

```
app/core/                     shared: config, db, security, logging
app/modules/<feature>/
    router.py                 HTTP only (Api layer)
    schemas.py                Pydantic DTOs
    service.py                use cases, transactions (Application layer)
    repository.py             SQL access (Infrastructure layer)
    models.py                 SQLAlchemy tables
    domain.py                 pure business rules, only when real rules exist
```

Rules:
1. Dependencies point inward: router → service → repository. No business logic in routers.
2. Transactions are owned by the service layer.
3. A module may call another module's **service**, never its repository or models.
4. `typing.Protocol` interfaces only where substitution is genuinely useful (external APIs, LLM providers, tests), not for every class.
5. Authorization is enforced in the backend (service/dependency level), never only in the UI.

## Rejected alternatives
- **1, layered by type:** fine for tiny apps; boundaries erode as modules grow. Reconsider: never for this project.
- **3, full hexagonal everywhere:** cost exceeds benefit at our size. Reconsider for a module whose domain becomes complex (e.g. stock/AI workflows), and adopt it locally there.
- **4, fat models:** couples rules to the ORM and hurts testing.

## Consequences
- Each feature lives in one folder; new contributors find code easily.
- Service-level unit tests are possible with fake repositories; integration tests use real Postgres.
- **10x:** unchanged; scale by running more instances of the same monolith.
- **100x / many teams:** a module with distinct scaling or ownership needs can be extracted into a service, because boundaries are already enforced; the module's service interface becomes its API contract.
