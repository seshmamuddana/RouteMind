# RouteMind

Adaptive Route Optimization for the Supply Chain.

## Run the application

**Terminal 1 — API (port 8000):**
```bash
pip install -r api/requirements.txt
python -m uvicorn api.main:app --reload --port 8000
```

**Terminal 2 — Frontend (port 5173):**
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Architecture

| Layer | Description |
|-------|-------------|
| `api/` | FastAPI server — reads CSVs live, computes disruptions/AI decisions when output files are missing |
| `frontend/` | React dashboard — fetches `/api/*` endpoints (proxied in dev) |
| `route_ai/`, `small_dataset/` | Existing Python pipeline (unchanged) |

## API Endpoints

- `GET /api/health`
- `GET /api/dashboard/summary`
- `GET /api/routes` — list all routes
- `GET /api/routes/{route_id}` — stops + features for one route
- `GET /api/optimizer` — optimizer results
- `GET /api/disruptions` — from CSV or computed on demand
- `GET /api/ai-decisions` — from CSV or computed on demand

Data reloads automatically when CSV files change on disk.
