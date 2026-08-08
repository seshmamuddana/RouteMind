from __future__ import annotations

import random
import uuid
from typing import Any

import pandas as pd

DISRUPTION_TYPES = [
  "TRAFFIC_DELAY",
  "ROAD_CLOSURE",
  "VEHICLE_CAPACITY_REDUCTION",
  "NEW_STOP",
]
SEVERITIES = ["LOW", "MEDIUM", "HIGH"]


def _traffic_delay(route_id: str, route_df: pd.DataFrame) -> dict[str, Any]:
  stop = route_df.sample(n=1).iloc[0]
  severity = random.choice(SEVERITIES)
  delay = { "LOW": (5, 15), "MEDIUM": (15, 30), "HIGH": (30, 60) }[severity]
  delay_minutes = random.randint(*delay)
  return {
    "DisruptionID": f"DISRUPTION_{uuid.uuid4()}",
    "RouteID": route_id,
    "DisruptionType": "TRAFFIC_DELAY",
    "Severity": severity,
    "StopID": stop["StopID"],
    "Latitude": float(stop["Latitude"]),
    "Longitude": float(stop["Longitude"]),
    "DelayMinutes": delay_minutes,
    "CapacityReduction": 0,
    "Description": f"Traffic delay of {delay_minutes} minutes near stop {stop['StopID']}",
  }


def _road_closure(route_id: str, route_df: pd.DataFrame) -> dict[str, Any]:
  stop = route_df.sample(n=1).iloc[0]
  severity = random.choice(["MEDIUM", "HIGH"])
  return {
    "DisruptionID": f"DISRUPTION_{uuid.uuid4()}",
    "RouteID": route_id,
    "DisruptionType": "ROAD_CLOSURE",
    "Severity": severity,
    "StopID": stop["StopID"],
    "Latitude": float(stop["Latitude"]),
    "Longitude": float(stop["Longitude"]),
    "DelayMinutes": 0,
    "CapacityReduction": 0,
    "Description": f"Road closure affecting stop {stop['StopID']}",
  }


def _capacity_reduction(route_id: str, route_df: pd.DataFrame) -> dict[str, Any]:
  stop = route_df.sample(n=1).iloc[0]
  severity = random.choice(SEVERITIES)
  ranges = { "LOW": (5, 10), "MEDIUM": (10, 25), "HIGH": (25, 50) }
  reduction = random.randint(*ranges[severity])
  return {
    "DisruptionID": f"DISRUPTION_{uuid.uuid4()}",
    "RouteID": route_id,
    "DisruptionType": "VEHICLE_CAPACITY_REDUCTION",
    "Severity": severity,
    "StopID": stop["StopID"],
    "Latitude": float(stop["Latitude"]),
    "Longitude": float(stop["Longitude"]),
    "DelayMinutes": 0,
    "CapacityReduction": reduction,
    "Description": f"Vehicle capacity reduced by {reduction} stops",
  }


def _new_stop(route_id: str, route_df: pd.DataFrame) -> dict[str, Any]:
  ref = route_df.sample(n=1).iloc[0]
  lat = float(ref["Latitude"]) + random.uniform(-0.01, 0.01)
  lng = float(ref["Longitude"]) + random.uniform(-0.01, 0.01)
  return {
    "DisruptionID": f"DISRUPTION_{uuid.uuid4()}",
    "RouteID": route_id,
    "DisruptionType": "NEW_STOP",
    "Severity": random.choice(["LOW", "MEDIUM"]),
    "StopID": f"NEW_{uuid.uuid4().hex[:6].upper()}",
    "Latitude": lat,
    "Longitude": lng,
    "DelayMinutes": 0,
    "CapacityReduction": 0,
    "Description": "New delivery stop added to active route",
  }


GENERATORS = {
  "TRAFFIC_DELAY": _traffic_delay,
  "ROAD_CLOSURE": _road_closure,
  "VEHICLE_CAPACITY_REDUCTION": _capacity_reduction,
  "NEW_STOP": _new_stop,
}


def generate_disruptions(
  processed: pd.DataFrame,
  route_ids: list[str] | None = None,
  per_route: int = 2,
  seed: int = 42,
) -> list[dict[str, Any]]:
  random.seed(seed)
  targets = route_ids or sorted(processed["RouteID"].unique().tolist())
  results: list[dict[str, Any]] = []

  for route_id in targets:
    route_df = processed[processed["RouteID"] == route_id]
    if route_df.empty:
      continue
    for _ in range(per_route):
      dtype = random.choice(DISRUPTION_TYPES)
      results.append(GENERATORS[dtype](route_id, route_df))

  return results
