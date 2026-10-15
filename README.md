# Brahmaputra Basin Flood Early-Warning Network - Project Status

Scaffold for the take-home assignment: CSV source of truth is `data/` at the repo root.

## Data loading approach

**On server startup**, the backend reads all CSV files from the root `data/` directory, validates them, and keeps the parsed dataset **in memory**. Subsequent API requests use that in-memory store.

A dedicated **refresh API** reloads the files from `data/` into memory when the CSVs change (for example after replacing files on disk), without restarting the whole stack.

### Why this fits the assignment

- The brief treats the CSV files as the **source of truth**; we load them as provided from `data/`.
- The dataset is small (thousands of rows), so an in-memory store is fast, simple, and easy to review.
- A refresh endpoint covers updates when files on disk change, in line with the optional CSV watcher stretch.



## Quick start

```bash
docker compose up --build
```

- UI: [http://localhost:13130](http://localhost:13130)  
- API: [http://localhost:18180/api/health](http://localhost:18180/api/health)  
- Docs: [http://localhost:18180/docs](http://localhost:18180/docs)



## Local development



### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
APP_DATA_DIR=../data uvicorn app.main:app --reload --port 8000
```



### Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api` to `http://localhost:8000`.

## Layout

```
data/           # CSV source of truth (loaded at startup into memory)
docs/           # BRIEF.md, HIERARCHY.md
backend/        # FastAPI
frontend/       # React + Vite + shadcn/ui
docker-compose.yml
AGENTS.md
```

