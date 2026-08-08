from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from api.services.ai_engine import build_ai_decisions
from api.services.data_store import store
from api.services.disruptions import generate_disruptions

app = FastAPI(title="RouteMind API", version="1.0.0")

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


def _get_disruptions(
  route_id: str | None = None,
  seed: int = 42,
  per_route: int = 2,
) -> list[dict[str, Any]]:
  saved = store.optional_csv("disruptions")
  if saved is not None:
    if route_id:
      saved = saved[saved["RouteID"] == route_id]
    return store.dataframe_records(saved)

  processed = store.processed()
  route_ids = [route_id] if route_id else None
  return generate_disruptions(processed, route_ids=route_ids, per_route=per_route, seed=seed)


def _get_ai_decisions(
  route_id: str | None = None,
  risk_level: str | None = None,
  seed: int = 42,
) -> list[dict[str, Any]]:
  for key in ("ai_decisions", "ai_decisions_rules"):
    saved = store.optional_csv(key)
    if saved is not None:
      if route_id:
        saved = saved[saved["RouteID"] == route_id]
      if risk_level:
        col = "FinalRiskLevel" if "FinalRiskLevel" in saved.columns else "RiskLevel"
        if col in saved.columns:
          saved = saved[saved[col].str.upper() == risk_level.upper()]
      return store.dataframe_records(saved)

  disruption_items = _get_disruptions(route_id=route_id, seed=seed)
  optimizer = store.optimizer()
  items = build_ai_decisions(disruption_items, optimizer, seed=seed)
  if risk_level:
    items = [i for i in items if i["FinalRiskLevel"].upper() == risk_level.upper()]
  return items


@app.get("/api/health")
def health() -> dict[str, str]:
  from api.config import ROOT
  return {"status": "ok", "dataRoot": str(ROOT)}


@app.get("/api/routes")
def list_routes() -> list[dict[str, Any]]:
  features = store.features()
  return [
    {
      "routeId": row["RouteID"],
      "totalStops": int(row["TotalStops"]),
      "totalDistance": float(row["TotalDistance"]),
      "routeScore": row["RouteScore"],
      "station": int(row["Station"]),
      "departureHour": int(row["DepartureHour"]),
    }
    for _, row in features.iterrows()
  ]


@app.get("/api/routes/{route_id}")
def get_route(route_id: str) -> dict[str, Any]:
  try:
    route = store.route_stops(route_id)
  except KeyError as exc:
    raise HTTPException(status_code=404, detail="Route not found") from exc

  feature_row = store.features()
  match = feature_row[feature_row["RouteID"] == route_id]
  if not match.empty:
    row = match.iloc[0]
    route["features"] = {
      "totalDistance": float(row["TotalDistance"]),
      "averageStopDistance": float(row["AverageStopDistance"]),
      "vehicleCapacity": float(row["VehicleCapacity"]),
      "departureHour": int(row["DepartureHour"]),
      "dayOfWeek": int(row["DayOfWeek"]),
      "dropoffRatio": float(row["DropoffRatio"]),
      "stopsPerKM": float(row["StopsPerKM"]),
      "capacityUtilization": float(row["CapacityUtilization"]),
      "routeScore": row["RouteScore"],
    }
  return route


@app.get("/api/optimizer")
def optimizer_results(route_id: str | None = None) -> list[dict[str, Any]]:
  df = store.optimizer()
  if route_id:
    df = df[df["RouteID"] == route_id]
    if df.empty:
      raise HTTPException(status_code=404, detail="Route not found")
  return store.dataframe_records(df)


@app.get("/api/disruptions")
def disruptions(
  route_id: str | None = None,
  seed: int = Query(42, ge=0),
  per_route: int = Query(2, ge=1, le=5),
) -> list[dict[str, Any]]:
  return _get_disruptions(route_id=route_id, seed=seed, per_route=per_route)


@app.get("/api/ai-decisions")
def ai_decisions(
  route_id: str | None = None,
  risk_level: str | None = None,
  seed: int = Query(42, ge=0),
) -> list[dict[str, Any]]:
  return _get_ai_decisions(route_id=route_id, risk_level=risk_level, seed=seed)


@app.get("/api/dashboard/summary")
def dashboard_summary(seed: int = Query(42, ge=0)) -> dict[str, Any]:
  optimizer = store.optimizer()
  ai = _get_ai_decisions(seed=seed)
  processed = store.processed()

  avg_improvement = float(optimizer["Improvement(%)"].mean())
  all_served = int(optimizer["AllStopsServed"].sum())
  high_risk = sum(1 for d in ai if d.get("FinalRiskLevel") == "HIGH")

  risk_dist = {
    level: sum(1 for d in ai if d.get("FinalRiskLevel") == level)
    for level in ("HIGH", "MEDIUM", "LOW")
  }

  top_routes = (
    optimizer.sort_values("Improvement(%)", ascending=False)
    .head(8)[["RouteID", "Improvement(%)", "OptimizedDistance(KM)", "TotalStops"]]
  )

  return {
    "totalRoutes": int(optimizer.shape[0]),
    "totalStops": int(processed.shape[0]),
    "avgImprovement": round(avg_improvement, 2),
    "allStopsServed": all_served,
    "highRiskAlerts": high_risk,
    "riskDistribution": risk_dist,
    "topRoutes": store.dataframe_records(top_routes),
    "defaultRouteId": store.route_ids()[0],
  }
