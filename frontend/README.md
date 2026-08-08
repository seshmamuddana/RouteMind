# RouteMind Frontend

Professional light-theme dashboard for the RouteMind logistics platform.

## Prerequisites

The **API server must be running** before starting the frontend:

```bash
# From project root
pip install -r api/requirements.txt
python -m uvicorn api.main:app --reload --port 8000
```

## Development

```bash
npm install
npm run dev
```

Vite proxies `/api` requests to `http://localhost:8000`.

## Build

```bash
npm run build
npm run preview
```

## Pages

- **Dashboard** — live KPIs and charts
- **Optimization** — compare optimizer algorithms per route
- **Route Explorer** — dynamic route/stop map viewer
- **Disruptions** — filterable disruption monitor
- **AI Decisions** — risk-scored routing recommendations
