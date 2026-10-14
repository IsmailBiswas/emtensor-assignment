# AGENTS.md

Guidance for humans and coding agents working in this repo.

## Project

Read-only flood early-warning **project status** app: load CSVs from root `data/` **once at startup into memory**, validate, expose APIs (including a **refresh** endpoint to reload from disk), show progress / money / dependencies / people / anomalies. Do not hand-edit CSVs. Spec: `docs/BRIEF.md`, `docs/HIERARCHY.md`, `data/README.md`.

## Tech stack

| Layer | Choice |
|---|---|
| Backend | Python 3.12+, FastAPI, Pydantic v2 |
| Frontend | React + TypeScript (Vite), shadcn/ui, Lucide icons |
| Run | `docker compose up` |
| Tests | pytest (API / domain); frontend tests as needed |

## Frontend

- UI built with **shadcn/ui** on React + TypeScript.
- **Responsive** for mobile, tablet, and desktop: layouts and nav must work at all three breakpoints.
- Keep **buttons and icons compact**; do not use oversized default sizes. Prefer `size="sm"` / smaller icon classes over default chunky controls.
- Use **Lucide** (`lucide-react`) for icons whenever an icon is appropriate.

## Architecture

- Prefer a thin API layer, domain/services, and data adapters.
- **Interfaces only between components**: no direct imports of concrete implementations across boundaries. Define Protocols / ABCs (backend) and ports or typed client interfaces (frontend). Wire concretes in composition roots (DI / factory / `main`).
- CSV loading, validation, anomaly rules, and aggregations live behind interfaces; routers and UI never reach into adapters or filesystems directly.

## FastAPI / async (hard rule)

- **Route handlers and async call paths must never block the event loop** for heavy CPU or I/O-bound work (CSV parse, pandas, large joins, disk reads, sync HTTP/DB).
- Offload blocking work with `asyncio.to_thread()`, a process/thread pool, or equivalent; keep handlers `async` and await those calls.
- Prefer async-friendly libraries when available. Do not run long sync loops in `async def` endpoints.
- Keep request handlers thin: validate input → call an interface → return a schema.

## Coding standards

- Type everything that crosses a boundary (Pydantic models, TS types).
- Clear names; small modules; one responsibility per service.
- Fail loudly on bad data where it matters; surface anomalies in plain language; never silently drop rule breaks.
- Tests for validation, anomaly rules, and critical aggregations.
- Meaningful git commits; no secrets in the repo.

## Layout (target)

```
data/           # CSV source of truth
docs/           # assignment brief
backend/        # FastAPI app
frontend/       # React app
docker-compose.yml
AGENTS.md
```

## Out of scope for core

CRUD for tasks/expenses/timesheets; auth/role login (role views are optional stretch).
