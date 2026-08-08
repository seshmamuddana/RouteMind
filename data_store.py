from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from api.config import CSV_FILES, ROOT


class DataStore:
  """Loads project CSVs on demand with simple mtime-based cache."""

  def __init__(self) -> None:
    self._cache: dict[str, tuple[float, pd.DataFrame]] = {}

  def _read_csv(self, key: str) -> pd.DataFrame:
    path = CSV_FILES[key]
    if not path.exists():
      raise FileNotFoundError(f"Missing data file: {path.name}")

    mtime = path.stat().st_mtime
    cached = self._cache.get(key)
    if cached and cached[0] == mtime:
      return cached[1].copy()

    df = pd.read_csv(path)
    self._cache[key] = (mtime, df)
    return df.copy()

  def optional_csv(self, key: str) -> pd.DataFrame | None:
    path = CSV_FILES[key]
    if not path.exists():
      return None
    return self._read_csv(key)

  def processed(self) -> pd.DataFrame:
    return self._read_csv("processed")

  def optimizer(self) -> pd.DataFrame:
    return self._read_csv("optimizer")

  def features(self) -> pd.DataFrame:
    return self._read_csv("features")

  def route_ids(self) -> list[str]:
    return sorted(self.processed()["RouteID"].unique().tolist())

  def route_stops(self, route_id: str) -> dict[str, Any]:
    df = self.processed()
    route_df = df[df["RouteID"] == route_id].sort_values("ActualSequence")
    if route_df.empty:
      raise KeyError(route_id)

    meta = route_df.iloc[0]
    stops = []
    for _, row in route_df.iterrows():
      zone = row["ZoneID"]
      stops.append(
        {
          "StopID": row["StopID"],
          "Latitude": float(row["Latitude"]),
          "Longitude": float(row["Longitude"]),
          "StopType": row["StopType"],
          "ActualSequence": int(row["ActualSequence"]),
          "ZoneID": None if pd.isna(zone) else str(zone),
        }
      )

    return {
      "routeId": route_id,
      "station": str(meta["Station"]),
      "date": str(meta["Date"]),
      "departureTime": str(meta["DepartureTime"]),
      "capacity": float(meta["Capacity"]),
      "routeScore": str(meta["RouteScore"]),
      "totalStops": len(stops),
      "stops": stops,
    }

  def records(self, key: str) -> list[dict[str, Any]]:
    df = self._read_csv(key)
    return json.loads(df.to_json(orient="records"))

  def dataframe_records(self, df: pd.DataFrame) -> list[dict[str, Any]]:
    clean = df.replace({np.nan: None})
    return json.loads(clean.to_json(orient="records"))


store = DataStore()
