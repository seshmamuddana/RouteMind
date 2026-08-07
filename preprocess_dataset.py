import json
import pandas as pd

print("Loading datasets...")

with open("small_dataset/route_data.json", "r") as f:
    route_data = json.load(f)

with open("small_dataset/package_data.json", "r") as f:
    package_data = json.load(f)

with open("small_dataset/travel_times.json", "r") as f:
    travel_data = json.load(f)

with open("small_dataset/actual_sequences.json", "r") as f:
    actual_sequences = json.load(f)

rows = []

total_routes = len(route_data)

for count, route_id in enumerate(route_data.keys(), start=1):

    print(f"Processing Route {count}/{total_routes}")

    route = route_data[route_id]

    station = route["station_code"]
    date = route["date_YYYY_MM_DD"]
    departure = route["departure_time_utc"]
    capacity = route["executor_capacity_cm3"]
    score = route["route_score"]

    stops = route["stops"]

    sequence = actual_sequences[route_id]["actual"]

    for stop_id, stop in stops.items():

        rows.append({
            "RouteID": route_id,
            "Station": station,
            "Date": date,
            "DepartureTime": departure,
            "Capacity": capacity,
            "RouteScore": score,

            "StopID": stop_id,
            "Latitude": stop["lat"],
            "Longitude": stop["lng"],
            "StopType": stop["type"],
            "ZoneID": stop["zone_id"],

            "ActualSequence": sequence.get(stop_id, None)
        })

df = pd.DataFrame(rows)

# Sort by route and actual delivery order
df = df.sort_values(["RouteID", "ActualSequence"])

# Reset index
df.reset_index(drop=True, inplace=True)

# Save
df.to_csv("processed_dataset.csv", index=False)

print()
print("===================================")
print("Preprocessing Complete!")
print("===================================")
print("Routes Processed :", total_routes)
print("Total Stops      :", len(df))
print("Saved File       : processed_dataset.csv")
print("===================================")

print("\nFirst 10 rows:\n")
print(df.head(30))