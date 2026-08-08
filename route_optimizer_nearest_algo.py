import pandas as pd
from math import radians, sin, cos, sqrt, atan2

# -------------------------------
# Load Dataset
# -------------------------------

df = pd.read_csv("processed_dataset.csv")

# -------------------------------
# Distance Function
# -------------------------------

def distance(point1, point2):

    lat1, lon1 = point1
    lat2, lon2 = point2

    R = 6371

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


# -------------------------------
# Calculate Route Distance
# -------------------------------

def calculate_route_distance(points):

    total = 0

    for i in range(len(points) - 1):
        total += distance(points[i], points[i + 1])

    return total


# -------------------------------
# Optimize All Routes
# -------------------------------

results = []

route_ids = df["RouteID"].unique()

print(f"Total Routes: {len(route_ids)}\n")

for route_id in route_ids:

    route = df[df["RouteID"] == route_id].copy()

    route = route.sort_values("ActualSequence")

    original_points = list(
        zip(
            route["Latitude"],
            route["Longitude"]
        )
    )

    # Skip very small routes
    if len(original_points) < 2:
        continue

    original_distance = calculate_route_distance(original_points)

    # -------------------------------
    # Nearest Neighbor
    # -------------------------------

    unvisited = original_points[1:].copy()

    optimized = [original_points[0]]

    current = original_points[0]

    while unvisited:

        next_stop = min(
            unvisited,
            key=lambda x: distance(current, x)
        )

        optimized.append(next_stop)

        current = next_stop

        unvisited.remove(next_stop)

    optimized_distance = calculate_route_distance(optimized)

    improvement = (
        (original_distance - optimized_distance)
        / original_distance
    ) * 100

    results.append({
        "RouteID": route_id,
        "Stops": len(original_points),
        "OriginalDistance(KM)": round(original_distance, 2),
        "OptimizedDistance(KM)": round(optimized_distance, 2),
        "Improvement(%)": round(improvement, 2)
    })

    print(f"Route: {route_id}")
    print(f"Stops: {len(original_points)}")
    print(f"Original Distance : {original_distance:.2f} KM")
    print(f"Optimized Distance: {optimized_distance:.2f} KM")
    print(f"Improvement       : {improvement:.2f}%")
    print("-" * 60)

# -------------------------------
# Save Results
# -------------------------------

results_df = pd.DataFrame(results)

results_df.to_csv(
    "nearest_neighbor_results.csv",
    index=False
)

print("\nOptimization Complete!")
print(results_df.head())

average_improvement = results_df["Improvement(%)"].mean()

print(f"\nAverage Improvement: {average_improvement:.2f}%")