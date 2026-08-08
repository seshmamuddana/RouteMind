import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv("processed_dataset.csv")

# ============================================================
# CONSTRAINTS
# ============================================================

AVERAGE_SPEED_KMPH = 30
MAX_ROUTE_TIME_HOURS = 8
MAX_STOPS = 150

# Maximum distance allowed by the time constraint
MAX_ROUTE_DISTANCE = (
    AVERAGE_SPEED_KMPH * MAX_ROUTE_TIME_HOURS
)

# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def haversine_matrix(latitudes, longitudes):

    lat = np.radians(latitudes)
    lon = np.radians(longitudes)

    lat1 = lat[:, None]
    lat2 = lat[None, :]

    lon1 = lon[:, None]
    lon2 = lon[None, :]

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        +
        np.cos(lat1)
        * np.cos(lat2)
        * np.sin(dlon / 2) ** 2
    )

    return 2 * 6371 * np.arctan2(
        np.sqrt(a),
        np.sqrt(1 - a)
    )


# ============================================================
# ROUTE DISTANCE
# ============================================================

def route_distance(route, distance_matrix):

    if len(route) < 2:
        return 0

    total = 0

    for i in range(len(route) - 1):
        total += distance_matrix[
            route[i],
            route[i + 1]
        ]

    return total


# ============================================================
# CONSTRAINED NEAREST NEIGHBOR
# ============================================================

def constrained_nearest_neighbor(route, distance_matrix):

    total_stops = len(route)

    # Station/depot is index 0
    current = 0

    optimized = [current]

    unvisited = set(
        range(1, total_stops)
    )

    current_distance = 0

    # --------------------------------------------------------
    # Continue until no valid stop remains
    # --------------------------------------------------------

    while unvisited:

        # Stop limit
        if len(optimized) >= MAX_STOPS:
            break

        best_stop = None
        best_distance = float("inf")

        # ----------------------------------------------------
        # Find nearest stop that keeps route within distance
        # ----------------------------------------------------

        for stop in unvisited:

            travel_distance = distance_matrix[
                current,
                stop
            ]

            new_total_distance = (
                current_distance
                + travel_distance
            )

            # Time constraint
            if new_total_distance > MAX_ROUTE_DISTANCE:
                continue

            if travel_distance < best_distance:

                best_distance = travel_distance
                best_stop = stop

        # ----------------------------------------------------
        # No valid stop remaining
        # ----------------------------------------------------

        if best_stop is None:
            break

        # Add selected stop
        optimized.append(best_stop)

        unvisited.remove(best_stop)

        current_distance += best_distance

        current = best_stop

    return optimized


# ============================================================
# PROCESS ROUTES
# ============================================================

results = []

route_ids = df["RouteID"].unique()

print("=" * 70)
print(f"TOTAL ROUTES: {len(route_ids)}")
print("=" * 70)

for route_id in route_ids:

    print(
        f"\nOptimizing Route: {route_id}"
    )

    # --------------------------------------------------------
    # Get route
    # --------------------------------------------------------

    route = df[
        df["RouteID"] == route_id
    ].copy()

    route = route.sort_values(
        "ActualSequence"
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # Coordinates
    # --------------------------------------------------------

    latitudes = route[
        "Latitude"
    ].values

    longitudes = route[
        "Longitude"
    ].values

    total_stops = len(route)

    # Skip invalid routes
    if total_stops < 2:
        continue

    # --------------------------------------------------------
    # Create distance matrix ONCE
    # --------------------------------------------------------

    distance_matrix = haversine_matrix(
        latitudes,
        longitudes
    )

    # ========================================================
    # ORIGINAL ROUTE
    # ========================================================

    original_route = list(
        range(total_stops)
    )

    original_distance = route_distance(
        original_route,
        distance_matrix
    )

    original_time = (
        original_distance
        / AVERAGE_SPEED_KMPH
    )

    # ========================================================
    # CONSTRAINED OPTIMIZATION
    # ========================================================

    optimized_route = (
        constrained_nearest_neighbor(
            route,
            distance_matrix
        )
    )

    optimized_distance = route_distance(
        optimized_route,
        distance_matrix
    )

    optimized_time = (
        optimized_distance
        / AVERAGE_SPEED_KMPH
    )

    # ========================================================
    # STOP ANALYSIS
    # ========================================================

    optimized_stops = len(
        optimized_route
    )

    unserved_stops = (
        total_stops
        - optimized_stops
    )

    # ========================================================
    # IMPROVEMENT
    # ========================================================

    if original_distance > 0:

        improvement = (
            (
                original_distance
                - optimized_distance
            )
            / original_distance
        ) * 100

    else:
        improvement = 0

    # ========================================================
    # CONSTRAINT CHECKS
    # ========================================================

    stops_constraint = (
        optimized_stops <= MAX_STOPS
    )

    time_constraint = (
        optimized_time
        <= MAX_ROUTE_TIME_HOURS
    )

    all_stops_served = (
        unserved_stops == 0
    )

    # ========================================================
    # SAVE RESULT
    # ========================================================

    results.append({

        "RouteID":
            route_id,

        "TotalStops":
            total_stops,

        "OptimizedStops":
            optimized_stops,

        "UnservedStops":
            unserved_stops,

        "OriginalDistance(KM)":
            round(
                original_distance,
                2
            ),

        "OptimizedDistance(KM)":
            round(
                optimized_distance,
                2
            ),

        "OriginalTime(Hours)":
            round(
                original_time,
                2
            ),

        "OptimizedTime(Hours)":
            round(
                optimized_time,
                2
            ),

        "Improvement(%)":
            round(
                improvement,
                2
            ),

        "StopsConstraint":
            stops_constraint,

        "TimeConstraint":
            time_constraint,

        "AllStopsServed":
            all_stops_served
    })

    # ========================================================
    # DISPLAY
    # ========================================================

    print(
        f"Total Stops       : {total_stops}"
    )

    print(
        f"Optimized Stops   : {optimized_stops}"
    )

    print(
        f"Unserved Stops    : {unserved_stops}"
    )

    print(
        f"Original Distance : "
        f"{original_distance:.2f} KM"
    )

    print(
        f"Optimized Distance: "
        f"{optimized_distance:.2f} KM"
    )

    print(
        f"Original Time     : "
        f"{original_time:.2f} Hours"
    )

    print(
        f"Optimized Time    : "
        f"{optimized_time:.2f} Hours"
    )

    print(
        f"Improvement       : "
        f"{improvement:.2f}%"
    )

    print(
        f"Stops Constraint  : "
        f"{stops_constraint}"
    )

    print(
        f"Time Constraint   : "
        f"{time_constraint}"
    )

    print(
        f"All Stops Served  : "
        f"{all_stops_served}"
    )

    print("-" * 70)


# ============================================================
# RESULTS DATAFRAME
# ============================================================

results_df = pd.DataFrame(
    results
)

# ============================================================
# SAVE RESULTS
# ============================================================

results_df.to_csv(
    "constrained_optimizer_results.csv",
    index=False
)

# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 70)
print("CONSTRAINED OPTIMIZATION COMPLETE")
print("=" * 70)

print()

print(results_df)

# ============================================================
# AVERAGE IMPROVEMENT
# ============================================================

if len(results_df) > 0:

    average_improvement = (
        results_df[
            "Improvement(%)"
        ].mean()
    )

    print()

    print(
        f"Average Improvement: "
        f"{average_improvement:.2f}%"
    )

# ============================================================
# CONSTRAINT SUCCESS
# ============================================================

if len(results_df) > 0:

    valid_routes = (
        (
            results_df[
                "StopsConstraint"
            ]
        )
        &
        (
            results_df[
                "TimeConstraint"
            ]
        )
        &
        (
            results_df[
                "AllStopsServed"
            ]
        )
    ).sum()

    print()

    print(
        f"Routes satisfying constraints: "
        f"{valid_routes}/{len(results_df)}"
    )

# ============================================================
# OUTPUT FILE
# ============================================================

print()

print(
    "Results saved to:"
)

print(
    "constrained_optimizer_results.csv"
)