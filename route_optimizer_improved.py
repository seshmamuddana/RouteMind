import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2


# ============================================================
# CONFIGURATION
# ============================================================

DATA_FILE = "processed_dataset.csv"
BASELINE_FILE = "constrained_optimizer_results.csv"
OUTPUT_FILE = "improved_optimizer_results.csv"

AVERAGE_SPEED_KMPH = 30
MAX_ROUTE_TIME_HOURS = 8
MAX_STOPS = 150

# Maximum number of 2-opt improvement rounds
MAX_2OPT_ITERATIONS = 50


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_FILE)

baseline_df = pd.read_csv(BASELINE_FILE)


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def haversine(point1, point2):

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
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return R * c


# ============================================================
# DISTANCE MATRIX
# ============================================================

def create_distance_matrix(points):

    n = len(points)

    matrix = np.zeros((n, n))

    for i in range(n):

        lat1 = radians(points[i][0])
        lon1 = radians(points[i][1])

        for j in range(i + 1, n):

            lat2 = radians(points[j][0])
            lon2 = radians(points[j][1])

            dlat = lat2 - lat1
            dlon = lon2 - lon1

            a = (
                sin(dlat / 2) ** 2
                + cos(lat1)
                * cos(lat2)
                * sin(dlon / 2) ** 2
            )

            c = 2 * atan2(
                sqrt(a),
                sqrt(1 - a)
            )

            d = 6371 * c

            matrix[i][j] = d
            matrix[j][i] = d

    return matrix


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
# ROUTE TIME
# ============================================================

def route_time(distance):

    return distance / AVERAGE_SPEED_KMPH


# ============================================================
# CONSTRAINED NEAREST NEIGHBOR
# ============================================================

def constrained_nearest_neighbor(
    route_df,
    distance_matrix
):

    total_stops = len(route_df)

    # Station/depot is index 0
    route = [0]

    unvisited = set(
        range(1, total_stops)
    )

    current = 0

    current_distance = 0

    while unvisited:

        # Stop constraint
        if len(route) >= MAX_STOPS:
            break

        candidates = []

        for stop in unvisited:

            added_distance = distance_matrix[
                current,
                stop
            ]

            new_distance = (
                current_distance
                + added_distance
            )

            new_time = route_time(
                new_distance
            )

            # Time constraint
            if new_time <= MAX_ROUTE_TIME_HOURS:

                candidates.append(
                    (
                        added_distance,
                        stop
                    )
                )

        # No valid candidate
        if not candidates:
            break

        # Nearest valid stop
        candidates.sort(
            key=lambda x: x[0]
        )

        added_distance, next_stop = (
            candidates[0]
        )

        route.append(next_stop)

        unvisited.remove(next_stop)

        current = next_stop

        current_distance += added_distance

    return route


# ============================================================
# 2-OPT IMPROVEMENT
# ============================================================

def two_opt(route, distance_matrix):

    if len(route) < 4:
        return route

    best_route = route.copy()

    best_distance = route_distance(
        best_route,
        distance_matrix
    )

    iteration = 0

    improved = True

    while improved and iteration < MAX_2OPT_ITERATIONS:

        improved = False

        iteration += 1

        # Keep the first stop fixed
        # because it is the station/depot.

        for i in range(
            1,
            len(best_route) - 2
        ):

            for j in range(
                i + 1,
                len(best_route) - 1
            ):

                a = best_route[i - 1]
                b = best_route[i]

                c = best_route[j]
                d = best_route[j + 1]

                # Current edges
                old_distance = (
                    distance_matrix[a, b]
                    +
                    distance_matrix[c, d]
                )

                # New edges after reversing
                new_distance = (
                    distance_matrix[a, c]
                    +
                    distance_matrix[b, d]
                )

                # Only perform improvement
                if new_distance < old_distance:

                    candidate_route = (
                        best_route[:i]
                        +
                        best_route[i:j + 1][::-1]
                        +
                        best_route[j + 1:]
                    )

                    candidate_distance = (
                        best_distance
                        - old_distance
                        + new_distance
                    )

                    # Time constraint
                    candidate_time = route_time(
                        candidate_distance
                    )

                    if (
                        candidate_time
                        <= MAX_ROUTE_TIME_HOURS
                    ):

                        best_route = candidate_route

                        best_distance = (
                            candidate_distance
                        )

                        improved = True

                        break

            if improved:
                break

    return best_route


# ============================================================
# CHECK CONSTRAINTS
# ============================================================

def check_constraints(
    route,
    total_stops,
    distance_matrix
):

    optimized_stops = len(route)

    distance = route_distance(
        route,
        distance_matrix
    )

    time = route_time(distance)

    stops_valid = (
        optimized_stops <= MAX_STOPS
    )

    time_valid = (
        time <= MAX_ROUTE_TIME_HOURS
    )

    all_stops_served = (
        optimized_stops == total_stops
    )

    return (
        stops_valid,
        time_valid,
        all_stops_served,
        distance,
        time
    )


# ============================================================
# MAIN OPTIMIZATION
# ============================================================

results = []

route_ids = df["RouteID"].unique()

print("=" * 70)
print(
    f"TOTAL ROUTES: {len(route_ids)}"
)
print("=" * 70)


for route_number, route_id in enumerate(
    route_ids,
    start=1
):

    print()
    print(
        f"[{route_number}/{len(route_ids)}] "
        f"Optimizing: {route_id}"
    )

    # --------------------------------------------------------
    # GET ROUTE
    # --------------------------------------------------------

    route_df = df[
        df["RouteID"] == route_id
    ].copy()

    route_df = route_df.sort_values(
        "ActualSequence"
    ).reset_index(
        drop=True
    )

    total_stops = len(route_df)

    if total_stops < 2:

        print(
            "Skipping: insufficient stops"
        )

        continue

    # --------------------------------------------------------
    # COORDINATES
    # --------------------------------------------------------

    points = list(
        zip(
            route_df["Latitude"].values,
            route_df["Longitude"].values
        )
    )

    # --------------------------------------------------------
    # CREATE DISTANCE MATRIX
    # --------------------------------------------------------

    distance_matrix = (
        create_distance_matrix(points)
    )

    # --------------------------------------------------------
    # ORIGINAL ROUTE
    # --------------------------------------------------------

    original_route = list(
        range(total_stops)
    )

    original_distance = route_distance(
        original_route,
        distance_matrix
    )

    original_time = route_time(
        original_distance
    )

    # --------------------------------------------------------
    # STEP 1:
    # CONSTRAINED NEAREST NEIGHBOR
    # --------------------------------------------------------

    nn_route = constrained_nearest_neighbor(
        route_df,
        distance_matrix
    )

    nn_distance = route_distance(
        nn_route,
        distance_matrix
    )

    nn_time = route_time(
        nn_distance
    )

    # --------------------------------------------------------
    # STEP 2:
    # 2-OPT IMPROVEMENT
    # --------------------------------------------------------

    improved_route = two_opt(
        nn_route,
        distance_matrix
    )

    improved_distance = route_distance(
        improved_route,
        distance_matrix
    )

    improved_time = route_time(
        improved_distance
    )

    # --------------------------------------------------------
    # STOPS
    # --------------------------------------------------------

    optimized_stops = len(
        improved_route
    )

    unserved_stops = (
        total_stops
        - optimized_stops
    )

    # --------------------------------------------------------
    # IMPROVEMENT AGAINST ORIGINAL
    # --------------------------------------------------------

    if original_distance > 0:

        improvement = (
            (
                original_distance
                -
                improved_distance
            )
            /
            original_distance
        ) * 100

    else:

        improvement = 0

    # --------------------------------------------------------
    # IMPROVEMENT OVER NEAREST NEIGHBOR
    # --------------------------------------------------------

    if nn_distance > 0:

        nn_improvement = (
            (
                nn_distance
                -
                improved_distance
            )
            /
            nn_distance
        ) * 100

    else:

        nn_improvement = 0

    # --------------------------------------------------------
    # CONSTRAINTS
    # --------------------------------------------------------

    stops_valid = (
        optimized_stops <= MAX_STOPS
    )

    time_valid = (
        improved_time
        <= MAX_ROUTE_TIME_HOURS
    )

    all_stops_served = (
        unserved_stops == 0
    )

    # --------------------------------------------------------
    # BASELINE RESULT
    # --------------------------------------------------------

    baseline_row = baseline_df[
        baseline_df["RouteID"] == route_id
    ]

    if len(baseline_row) > 0:

        baseline_distance = float(
            baseline_row.iloc[0][
                "OptimizedDistance(KM)"
            ]
        )

        baseline_improvement = float(
            baseline_row.iloc[0][
                "Improvement(%)"
            ]
        )

        improvement_over_constrained = (
            (
                baseline_distance
                -
                improved_distance
            )
            /
            baseline_distance
        ) * 100

    else:

        baseline_distance = None
        baseline_improvement = None
        improvement_over_constrained = None

    # --------------------------------------------------------
    # PRINT
    # --------------------------------------------------------

    print(
        f"Total Stops              : "
        f"{total_stops}"
    )

    print(
        f"NN Distance              : "
        f"{nn_distance:.2f} KM"
    )

    print(
        f"Improved Distance        : "
        f"{improved_distance:.2f} KM"
    )

    print(
        f"Improvement vs Original  : "
        f"{improvement:.2f}%"
    )

    print(
        f"Improvement vs NN        : "
        f"{nn_improvement:.2f}%"
    )

    if improvement_over_constrained is not None:

        print(
            f"Improvement vs Constrained: "
            f"{improvement_over_constrained:.2f}%"
        )

    print(
        f"Optimized Stops          : "
        f"{optimized_stops}"
    )

    print(
        f"Unserved Stops           : "
        f"{unserved_stops}"
    )

    print(
        f"Stops Constraint         : "
        f"{stops_valid}"
    )

    print(
        f"Time Constraint          : "
        f"{time_valid}"
    )

    print(
        f"All Stops Served         : "
        f"{all_stops_served}"
    )

    print("-" * 70)

    # --------------------------------------------------------
    # SAVE RESULT
    # --------------------------------------------------------

    results.append({

        "RouteID":
            route_id,

        "TotalStops":
            total_stops,

        "NNOptimizedStops":
            len(nn_route),

        "OptimizedStops":
            optimized_stops,

        "UnservedStops":
            unserved_stops,

        "OriginalDistance(KM)":
            round(
                original_distance,
                2
            ),

        "NNDistance(KM)":
            round(
                nn_distance,
                2
            ),

        "OptimizedDistance(KM)":
            round(
                improved_distance,
                2
            ),

        "OriginalTime(Hours)":
            round(
                original_time,
                2
            ),

        "OptimizedTime(Hours)":
            round(
                improved_time,
                2
            ),

        "Improvement(%)":
            round(
                improvement,
                2
            ),

        "ImprovementVsNN(%)":
            round(
                nn_improvement,
                2
            ),

        "BaselineConstrainedDistance(KM)":
            (
                round(
                    baseline_distance,
                    2
                )
                if baseline_distance is not None
                else None
            ),

        "ImprovementVsConstrained(%)":
            (
                round(
                    improvement_over_constrained,
                    2
                )
                if improvement_over_constrained is not None
                else None
            ),

        "StopsConstraint":
            stops_valid,

        "TimeConstraint":
            time_valid,

        "AllStopsServed":
            all_stops_served
    })


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
    OUTPUT_FILE,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("=" * 70)
print("IMPROVED ROUTE OPTIMIZER COMPLETED")
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

    average_nn_improvement = (
        results_df[
            "ImprovementVsNN(%)"
        ].mean()
    )

    print()

    print(
        f"Average Improvement vs Original: "
        f"{average_improvement:.2f}%"
    )

    print(
        f"Average Improvement vs NN: "
        f"{average_nn_improvement:.2f}%"
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
            == True
        )
        &
        (
            results_df[
                "TimeConstraint"
            ]
            == True
        )
        &
        (
            results_df[
                "AllStopsServed"
            ]
            == True
        )
    ).sum()

    print()

    print(
        f"Routes satisfying all constraints: "
        f"{valid_routes}/{len(results_df)}"
    )


# ============================================================
# ROUTES IMPROVED OVER CONSTRAINED VERSION
# ============================================================

if len(results_df) > 0:

    comparison = results_df[
        "ImprovementVsConstrained(%)"
    ].dropna()

    if len(comparison) > 0:

        better_routes = (
            comparison > 0
        ).sum()

        print()

        print(
            f"Routes improved over constrained optimizer: "
            f"{better_routes}/{len(comparison)}"
        )


# ============================================================
# OUTPUT FILE
# ============================================================

print()

print(
    "Results saved to:"
)

print(
    OUTPUT_FILE
)