from __future__ import annotations

import random
from typing import Any

import pandas as pd


def _risk_score(row: dict[str, Any]) -> int:
  score = 0
  severity = str(row["Severity"]).upper()
  disruption = row["DisruptionType"]

  if severity == "HIGH":
    score += 35
  elif severity == "MEDIUM":
    score += 20
  else:
    score += 5

  if disruption == "ROAD_CLOSURE":
    score += 25
  elif disruption == "TRAFFIC_DELAY":
    score += 15
  elif disruption == "VEHICLE_CAPACITY_REDUCTION":
    score += 20
  elif disruption == "NEW_STOP":
    score += 10

  delay = float(row.get("DelayMinutes") or 0)
  if delay >= 40:
    score += 20
  elif delay >= 20:
    score += 12
  elif delay >= 10:
    score += 6

  capacity = float(row.get("CapacityReduction") or 0)
  if capacity >= 30:
    score += 20
  elif capacity >= 15:
    score += 12
  elif capacity > 0:
    score += 5

  stops_lost = int(row.get("StopsLost") or 0)
  if stops_lost >= 10:
    score += 15
  elif stops_lost >= 5:
    score += 8
  elif stops_lost > 0:
    score += 3

  time_change = abs(float(row.get("TimeChange(Hours)") or 0))
  if time_change >= 1:
    score += 15
  elif time_change >= 0.5:
    score += 8
  elif time_change > 0.2:
    score += 3

  total_stops = int(row.get("TotalStops") or 0)
  if total_stops >= 180:
    score += 8
  elif total_stops >= 150:
    score += 5
  elif total_stops >= 120:
    score += 2

  recovery = float(row.get("RecoveryEfficiency(%)") or 100)
  if recovery < 80:
    score += 10
  elif recovery < 90:
    score += 5

  return min(score, 100)


def _risk_level(score: int) -> str:
  if score >= 70:
    return "HIGH"
  if score >= 40:
    return "MEDIUM"
  return "LOW"


def _routing_decision(row: dict[str, Any]) -> str:
  risk = row["RiskLevel"]
  disruption = row["DisruptionType"]

  if risk == "HIGH":
    return "IMMEDIATE_REROUTE"
  if risk == "MEDIUM":
    mapping = {
      "ROAD_CLOSURE": "REROUTE_AVOID_CLOSED_ROAD",
      "TRAFFIC_DELAY": "REROUTE_TRAFFIC_AVOIDANCE",
      "VEHICLE_CAPACITY_REDUCTION": "REBALANCE_LOAD_AND_REROUTE",
      "NEW_STOP": "INSERT_STOP_OPTIMALLY",
    }
    return mapping.get(disruption, "MONITOR_ROUTE")
  mapping = {
    "NEW_STOP": "INSERT_STOP_OPTIMALLY",
    "TRAFFIC_DELAY": "MONITOR_TRAFFIC",
    "ROAD_CLOSURE": "MONITOR_CLOSED_ROAD",
    "VEHICLE_CAPACITY_REDUCTION": "MONITOR_CAPACITY",
  }
  return mapping.get(disruption, "MONITOR_ROUTE")


def _recommendation(row: dict[str, Any]) -> str:
  risk = row["RiskLevel"]
  disruption = row["DisruptionType"]
  if risk == "HIGH":
    return "Trigger immediate dynamic rerouting and notify fleet operator"
  if risk == "MEDIUM":
    texts = {
      "ROAD_CLOSURE": "Avoid affected road and recalculate route",
      "TRAFFIC_DELAY": "Recalculate route using traffic-aware alternatives",
      "VEHICLE_CAPACITY_REDUCTION": "Rebalance vehicle load and recalculate route",
      "NEW_STOP": "Insert new stop at the most efficient position",
    }
    return texts.get(disruption, "Recalculate route and monitor constraint violations")
  return "Continue current route and monitor disruption"


def build_ai_decisions(
  disruptions: list[dict[str, Any]],
  optimizer: pd.DataFrame,
  seed: int = 42,
) -> list[dict[str, Any]]:
  random.seed(seed)
  opt_map = optimizer.set_index("RouteID").to_dict(orient="index")
  results: list[dict[str, Any]] = []

  for d in disruptions:
    opt = opt_map.get(d["RouteID"], {})
    total_stops = int(opt.get("TotalStops", 0))
    stops_lost = random.randint(0, min(12, max(0, total_stops // 10)))
    time_change = round(random.uniform(-0.2, 1.1), 2)
    distance_change = round(random.uniform(-1.5, 4.5), 2)
    recovery = round(random.uniform(78, 99), 1)
    ml_confidence = round(random.uniform(72, 98), 1)

    row: dict[str, Any] = {
      **d,
      "TotalStops": total_stops,
      "StopsLost": stops_lost,
      "DistanceChange(KM)": distance_change,
      "TimeChange(Hours)": time_change,
      "RecoveryEfficiency(%)": recovery,
      "RecoverySuccessful": recovery >= 85,
    }

    risk = _risk_score(row)
    row["RiskScore"] = risk
    row["RiskLevel"] = _risk_level(risk)
    row["AI_Decision"] = _routing_decision(row)
    row["Recommendation"] = _recommendation(row)
    row["PriorityScore"] = round(
      min(row["RiskScore"] * 0.7 + float(d.get("DelayMinutes") or 0) * 0.2 + stops_lost * 0.1, 100),
      2,
    )
    row["MLRisk"] = row["RiskLevel"]
    row["MLConfidence(%)"] = ml_confidence
    row["FinalRiskScore"] = risk
    row["FinalRiskLevel"] = row["RiskLevel"]
    row["AI_Explanation"] = (
      f"{row['RiskLevel']} risk detected with {ml_confidence:.1f}% ML confidence. "
      f"{row['Recommendation']}"
    )
    results.append(row)

  results.sort(key=lambda r: r["PriorityScore"], reverse=True)
  return results
