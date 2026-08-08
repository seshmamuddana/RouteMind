"""Export RouteMind CSV data to frontend JSON (NaN-safe). Run from project root."""
import json
import os

import pandas as pd

OUT = os.path.join("frontend", "public", "data")
os.makedirs(OUT, exist_ok=True)

for name, file in [
    ("optimizer-results", "improved_optimizer_results.csv"),
    ("nearest-neighbor", "nearest_neighbor_results.csv"),
    ("constrained-optimizer", "constrained_optimizer_results.csv"),
    ("route-features", "route_features.csv"),
]:
    path = os.path.join(OUT, f"{name}.json")
    pd.read_csv(file).to_json(path, orient="records", indent=2)

df = pd.read_csv("processed_dataset.csv")
route = df["RouteID"].iloc[0]
stops_df = df[df["RouteID"] == route][
    ["StopID", "Latitude", "Longitude", "StopType", "ActualSequence", "ZoneID"]
]
meta = df[df["RouteID"] == route].iloc[0]

stops = []
for _, row in stops_df.iterrows():
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

payload = {
    "routeId": route,
    "station": str(meta["Station"]),
    "date": str(meta["Date"]),
    "stops": stops,
}

with open(os.path.join(OUT, "sample-route.json"), "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)

print(f"Exported data to {OUT}/")
