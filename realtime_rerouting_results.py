import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2

# ============================================================
# CONFIGURATION
# ============================================================

DATASET_FILE = "processed_dataset.csv"
DISRUPTION_FILE = "route_disruptions.csv"
OUTPUT_FILE = "realtime_rerouting_results.csv"

AVERAGE_SPEED_KMPH = 30
MAX_ROUTE_TIME_HOURS = 8
MAX_STOPS = 150

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATASET_FILE)
disruptions = pd.read_csv(DISRUPTION_FILE)

print("=" * 70)
print("REAL-TIME ROUTE REROUTING")
print("=" * 70)

print(f"\nTotal Routes       : {df['RouteID'].nunique()}")
print(f"Total Disruptions  : {len(disruptions)}")

# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def haversine(point1, point2):

    lat1, lon1 = point1
    lat2, lon2 = point2

    R = 6371.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)

    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        +
        cos(lat1)
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
# Calculated once for speed.
# This avoids repeatedly calculating Haversine distances.

def create_distance_matrix(points):

    n = len(points)

    matrix = np.zeros((n, n))

    for i in range(n):

        for j in range(i + 1, n):

            d = haversine(
                points[i],
                points[j]
            )

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
# GET DISRUPTION STOP
# ============================================================

def get_disruption_stop(disruption):

    possible_columns = [
        "StopID",
        "AffectedStopID",
        "DisruptedStopID",
        "NewStopID"
    ]

    for column in possible_columns:

        if column in disruption.index:

            value = disruption[column]

            if pd.notna(value):
                return value

    return None


# ============================================================
# GET DISRUPTION SEGMENT
# ============================================================

def get_segment(disruption):

    from_columns = [
        "FromStopID",
        "AffectedFromStopID"
    ]

    to_columns = [
        "ToStopID",
        "AffectedToStopID"
    ]

    from_stop = None
    to_stop = None

    for column in from_columns:

        if column in disruption.index:

            if pd.notna(disruption[column]):

                from_stop = disruption[column]
                break

    for column in to_columns:

        if column in disruption.index:

            if pd.notna(disruption[column]):

                to_stop = disruption[column]
                break

    return from_stop, to_stop


# ============================================================
# CREATE INITIAL ROUTE
# ============================================================

def nearest_neighbor_route(
    route_df,
    distance_matrix
):

    n = len(route_df)

    if n == 0:
        return []

    current = 0

    route = [current]

    unvisited = set(
        range(1, n)
    )

    while unvisited:

        next_stop = min(
            unvisited,
            key=lambda x:
            distance_matrix[current][x]
        )

        route.append(next_stop)

        unvisited.remove(
            next_stop
        )

        current = next_stop

    return route


# ============================================================
# APPLY ROAD CLOSURE
# ============================================================

def apply_road_closure(
    route,
    route_df,
    disruption,
    distance_matrix
):

    affected_stop = get_disruption_stop(
        disruption
    )

    from_stop, to_stop = get_segment(
        disruption
    )

    blocked_edges = set()

    # --------------------------------------------------------
    # If a specific segment is provided
    # --------------------------------------------------------

    if from_stop is not None and to_stop is not None:

        stop_to_index = {
            str(row["StopID"]): i
            for i, (_, row)
            in enumerate(route_df.iterrows())
        }

        if (
            str(from_stop) in stop_to_index
            and
            str(to_stop) in stop_to_index
        ):

            a = stop_to_index[
                str(from_stop)
            ]

            b = stop_to_index[
                str(to_stop)
            ]

            blocked_edges.add(
                tuple(sorted((a, b)))
            )

    # --------------------------------------------------------
    # If only an affected stop exists,
    # avoid using that stop.
    # --------------------------------------------------------

    affected_index = None

    if affected_stop is not None:

        matches = route_df.index[
            route_df["StopID"].astype(str)
            ==
            str(affected_stop)
        ].tolist()

        if matches:

            affected_index = matches[0]

    # --------------------------------------------------------
    # Build new route
    # --------------------------------------------------------

    if affected_index is None and not blocked_edges:

        return route

    available = set(
        range(len(route_df))
    )

    if affected_index is not None:

        available.discard(
            affected_index
        )

    if len(available) == 0:

        return route[:1]

    new_route = [0]

    if 0 not in available:

        new_route = []

    current = new_route[0] if new_route else None

    if current is not None:

        available.discard(current)

    while available:

        candidates = []

        for candidate in available:

            edge = tuple(
                sorted(
                    (current, candidate)
                )
            )

            if edge in blocked_edges:
                continue

            candidates.append(
                candidate
            )

        if not candidates:

            break

        next_stop = min(
            candidates,
            key=lambda x:
            distance_matrix[current][x]
        )

        new_route.append(
            next_stop
        )

        available.remove(
            next_stop
        )

        current = next_stop

    return new_route


# ============================================================
# RE-ROUTE AFTER DISRUPTION
# ============================================================

def reroute(
    route_df,
    distance_matrix,
    disruption
):

    disruption_type = str(
        disruption["DisruptionType"]
    )

    # --------------------------------------------------------
    # Start with nearest-neighbor route
    # --------------------------------------------------------

    route = nearest_neighbor_route(
        route_df,
        distance_matrix
    )

    # --------------------------------------------------------
    # ROAD CLOSURE
    # --------------------------------------------------------

    if disruption_type == "ROAD_CLOSURE":

        route = apply_road_closure(
            route,
            route_df,
            disruption,
            distance_matrix
        )

    # --------------------------------------------------------
    # TRAFFIC DELAY
    # --------------------------------------------------------

    elif disruption_type == "TRAFFIC_DELAY":

        delay = float(
            disruption.get(
                "DelayMinutes",
                0
            )
        )

        # Remove unnecessary tail stops if
        # disruption pushes route beyond time limit.

        base_distance = route_distance(
            route,
            distance_matrix
        )

        delay_hours = delay / 60

        total_time = (
            base_distance
            / AVERAGE_SPEED_KMPH
        ) + delay_hours

        if total_time > MAX_ROUTE_TIME_HOURS:

            while (
                len(route) > 1
                and
                total_time > MAX_ROUTE_TIME_HOURS
            ):

                route.pop()

                new_distance = route_distance(
                    route,
                    distance_matrix
                )

                total_time = (
                    new_distance
                    / AVERAGE_SPEED_KMPH
                ) + delay_hours

    # --------------------------------------------------------
    # VEHICLE CAPACITY REDUCTION
    # --------------------------------------------------------

    elif (
        disruption_type
        ==
        "VEHICLE_CAPACITY_REDUCTION"
    ):

        reduction = float(
            disruption.get(
                "CapacityReduction",
                0
            )
        )

        allowed_stops = max(
            1,
            int(
                MAX_STOPS
                * (
                    1
                    -
                    reduction / 100
                )
            )
        )

        if len(route) > allowed_stops:

            route = route[
                :allowed_stops
            ]

    # --------------------------------------------------------
    # NEW STOP
    # --------------------------------------------------------

    elif disruption_type == "NEW_STOP":

        new_stop = get_disruption_stop(
            disruption
        )

        if new_stop is not None:

            matches = route_df.index[
                route_df["StopID"].astype(str)
                ==
                str(new_stop)
            ].tolist()

            if matches:

                new_index = matches[0]

                if new_index not in route:

                    best_position = None
                    best_extra_distance = float(
                        "inf"
                    )

                    for i in range(
                        len(route) - 1
                    ):

                        a = route[i]
                        b = route[i + 1]

                        extra = (
                            distance_matrix[a][new_index]
                            +
                            distance_matrix[new_index][b]
                            -
                            distance_matrix[a][b]
                        )

                        if extra < best_extra_distance:

                            best_extra_distance = extra
                            best_position = i + 1

                    if best_position is not None:

                        route.insert(
                            best_position,
                            new_index
                        )

    # --------------------------------------------------------
    # ENFORCE MAX STOPS
    # --------------------------------------------------------

    if len(route) > MAX_STOPS:

        route = route[
            :MAX_STOPS
        ]

    return route


# ============================================================
# PROCESS DISRUPTIONS
# ============================================================

results = []

route_ids = disruptions[
    "RouteID"
].unique()

print("\n" + "=" * 70)

for route_id in route_ids:

    print(
        f"\nProcessing Route: {route_id}"
    )

    route_df = df[
        df["RouteID"] == route_id
    ].copy()

    route_df = route_df.sort_values(
        "ActualSequence"
    ).reset_index(
        drop=True
    )

    if len(route_df) < 2:

        continue

    points = list(
        zip(
            route_df["Latitude"],
            route_df["Longitude"]
        )
    )

    # --------------------------------------------------------
    # Distance matrix calculated once per route
    # --------------------------------------------------------

    distance_matrix = create_distance_matrix(
        points
    )

    # --------------------------------------------------------
    # Original route
    # --------------------------------------------------------

    original_route = list(
        range(len(route_df))
    )

    original_distance = route_distance(
        original_route,
        distance_matrix
    )

    original_time = route_time(
        original_distance
    )

    # --------------------------------------------------------
    # Process every disruption
    # --------------------------------------------------------

    route_disruptions = disruptions[
        disruptions["RouteID"]
        ==
        route_id
    ]

    for _, disruption in route_disruptions.iterrows():

        disruption_id = disruption[
            "DisruptionID"
        ]

        disruption_type = disruption[
            "DisruptionType"
        ]

        severity = disruption[
            "Severity"
        ]

        print(
            f"  Rerouting: "
            f"{disruption_id} | "
            f"{disruption_type}"
        )

        # ----------------------------------------------------
        # Apply disruption and reroute
        # ----------------------------------------------------

        rerouted = reroute(
            route_df,
            distance_matrix,
            disruption
        )

        # ----------------------------------------------------
        # Metrics
        # ----------------------------------------------------

        rerouted_distance = route_distance(
            rerouted,
            distance_matrix
        )

        rerouted_time = route_time(
            rerouted_distance
        )

        delay_minutes = float(
            disruption.get(
                "DelayMinutes",
                0
            )
        )

        capacity_reduction = float(
            disruption.get(
                "CapacityReduction",
                0
            )
        )

        # ----------------------------------------------------
        # Simulated disrupted time
        # ----------------------------------------------------

        disrupted_time = (
            original_time
            +
            delay_minutes / 60
        )

        # Capacity effect
        if (
            disruption_type
            ==
            "VEHICLE_CAPACITY_REDUCTION"
        ):

            capacity_factor = (
                1
                +
                capacity_reduction / 100
            )

            disrupted_time *= (
                capacity_factor
            )

        # ----------------------------------------------------
        # Constraint checks
        # ----------------------------------------------------

        stops_valid = (
            len(rerouted)
            <= MAX_STOPS
        )

        time_valid = (
            rerouted_time
            <= MAX_ROUTE_TIME_HOURS
        )

        recovery_successful = (
            stops_valid
            and
            time_valid
        )

        # ----------------------------------------------------
        # Distance change
        # ----------------------------------------------------

        distance_change = (
            rerouted_distance
            -
            original_distance
        )

        if original_distance > 0:

            recovery_efficiency = (
                (
                    original_distance
                    -
                    rerouted_distance
                )
                /
                original_distance
            ) * 100

        else:

            recovery_efficiency = 0

        # ----------------------------------------------------
        # Time change
        # ----------------------------------------------------

        time_change = (
            rerouted_time
            -
            original_time
        )

        # ----------------------------------------------------
        # Stops
        # ----------------------------------------------------

        stops_before = len(
            original_route
        )

        stops_after = len(
            rerouted
        )

        stops_lost = (
            stops_before
            -
            stops_after
        )

        # ----------------------------------------------------
        # Save result
        # ----------------------------------------------------

        results.append({

            "RouteID":
                route_id,

            "DisruptionID":
                disruption_id,

            "DisruptionType":
                disruption_type,

            "Severity":
                severity,

            "DelayMinutes":
                delay_minutes,

            "CapacityReduction":
                capacity_reduction,

            "OriginalStops":
                stops_before,

            "ReroutedStops":
                stops_after,

            "StopsLost":
                stops_lost,

            "OriginalDistance(KM)":
                round(
                    original_distance,
                    2
                ),

            "ReroutedDistance(KM)":
                round(
                    rerouted_distance,
                    2
                ),

            "DistanceChange(KM)":
                round(
                    distance_change,
                    2
                ),

            "OriginalTime(Hours)":
                round(
                    original_time,
                    2
                ),

            "DisruptedTime(Hours)":
                round(
                    disrupted_time,
                    2
                ),

            "ReroutedTime(Hours)":
                round(
                    rerouted_time,
                    2
                ),

            "TimeChange(Hours)":
                round(
                    time_change,
                    2
                ),

            "RecoveryEfficiency(%)":
                round(
                    recovery_efficiency,
                    2
                ),

            "StopsConstraint":
                stops_valid,

            "TimeConstraint":
                time_valid,

            "RecoverySuccessful":
                recovery_successful
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
# SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("REAL-TIME REROUTING COMPLETED")
print("=" * 70)

print(
    f"\nTotal disruption scenarios : "
    f"{len(results_df)}"
)

if len(results_df) > 0:

    successful = (
        results_df[
            "RecoverySuccessful"
        ] == True
    ).sum()

    print(
        f"Successful recoveries      : "
        f"{successful}/"
        f"{len(results_df)}"
    )

    success_rate = (
        successful
        /
        len(results_df)
    ) * 100

    print(
        f"Recovery success rate      : "
        f"{success_rate:.2f}%"
    )

    average_distance_change = (
        results_df[
            "DistanceChange(KM)"
        ].mean()
    )

    print(
        f"Average distance change    : "
        f"{average_distance_change:.2f} KM"
    )

    average_time_change = (
        results_df[
            "TimeChange(Hours)"
        ].mean()
    )

    print(
        f"Average time change        : "
        f"{average_time_change:.2f} Hours"
    )

    average_recovery = (
        results_df[
            "RecoveryEfficiency(%)"
        ].mean()
    )

    print(
        f"Average recovery efficiency: "
        f"{average_recovery:.2f}%"
    )

    print("\nDISRUPTION PERFORMANCE")

    summary = (
        results_df
        .groupby("DisruptionType")
        .agg(
            Scenarios=(
                "DisruptionID",
                "count"
            ),

            Successful=(
                "RecoverySuccessful",
                "sum"
            ),

            AvgDistanceChange=(
                "DistanceChange(KM)",
                "mean"
            ),

            AvgTimeChange=(
                "TimeChange(Hours)",
                "mean"
            )
        )
        .reset_index()
    )

    summary["SuccessRate(%)"] = (
        summary["Successful"]
        /
        summary["Scenarios"]
        *
        100
    ).round(2)

    summary[
        "AvgDistanceChange"
    ] = summary[
        "AvgDistanceChange"
    ].round(2)

    summary[
        "AvgTimeChange"
    ] = summary[
        "AvgTimeChange"
    ].round(2)

    print()
    print(summary)

# ============================================================
# OUTPUT
# ============================================================

print("\n")
print("Results saved to:")
print(OUTPUT_FILE)

print("=" * 70)