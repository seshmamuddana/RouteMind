import pandas as pd

# ============================================================
# FILES
# ============================================================

DATASET_FILE = "processed_dataset.csv"
DISRUPTION_FILE = "route_disruptions.csv"
REROUTING_FILE = "realtime_rerouting_results.csv"
OUTPUT_FILE = "recovery_evaluation_results.csv"

AVERAGE_SPEED_KMPH = 30


# ============================================================
# LOAD FILES
# ============================================================

df = pd.read_csv(DATASET_FILE)
disruptions = pd.read_csv(DISRUPTION_FILE)
rerouting = pd.read_csv(REROUTING_FILE)


print("=" * 70)
print("ROUTE RECOVERY EVALUATION")
print("=" * 70)

print()

print(
    f"Routes              : {df['RouteID'].nunique()}"
)

print(
    f"Disruptions         : {len(disruptions)}"
)

print(
    f"Rerouting Results   : {len(rerouting)}"
)


# ============================================================
# SHOW ACTUAL COLUMNS
# ============================================================

print()
print("Disruption columns:")
print(list(disruptions.columns))

print()

print("Rerouting columns:")
print(list(rerouting.columns))


# ============================================================
# ROUTE DISTANCE
# ============================================================

def haversine(point1, point2):

    from math import radians, sin, cos, sqrt, atan2

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


def calculate_route_distance(points):

    total = 0

    for i in range(len(points) - 1):

        total += haversine(
            points[i],
            points[i + 1]
        )

    return total


# ============================================================
# CALCULATE ORIGINAL ROUTE INFORMATION
# ============================================================

route_info = {}


for route_id in df["RouteID"].unique():

    route = df[
        df["RouteID"] == route_id
    ].copy()

    route = route.sort_values(
        "ActualSequence"
    )

    points = list(
        zip(
            route["Latitude"],
            route["Longitude"]
        )
    )

    if len(points) < 2:
        continue

    original_distance = calculate_route_distance(
        points
    )

    original_time = (
        original_distance
        / AVERAGE_SPEED_KMPH
    )

    route_info[route_id] = {

        "distance":
            original_distance,

        "time":
            original_time,

        "stops":
            len(points)
    }


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_disruption_columns = [
    "DisruptionID",
    "RouteID",
    "DisruptionType",
    "Severity",
    "DelayMinutes",
    "CapacityReduction"
]


for column in required_disruption_columns:

    if column not in disruptions.columns:

        print()
        print(
            f"ERROR: Missing column: {column}"
        )

        print(
            "Available columns:"
        )

        print(
            list(disruptions.columns)
        )

        raise SystemExit


# ============================================================
# CHECK REROUTING COLUMNS
# ============================================================

required_rerouting_columns = [
    "DisruptionID",
    "RouteID",
    "ReroutedDistance(KM)",
    "ReroutedTime(Hours)"
]


for column in required_rerouting_columns:

    if column not in rerouting.columns:

        print()
        print(
            f"ERROR: Missing column: {column}"
        )

        print(
            "Available rerouting columns:"
        )

        print(
            list(rerouting.columns)
        )

        raise SystemExit


# ============================================================
# MERGE DISRUPTIONS WITH REROUTING
# ============================================================

combined = pd.merge(

    disruptions,

    rerouting[
        [
            "DisruptionID",
            "RouteID",
            "ReroutedDistance(KM)",
            "ReroutedTime(Hours)"
        ]
    ],

    on=[
        "DisruptionID",
        "RouteID"
    ],

    how="inner"
)


print()
print(
    f"Matched scenarios : {len(combined)}"
)


# ============================================================
# EVALUATE
# ============================================================

results = []


print()
print("=" * 70)
print("EVALUATING DISRUPTION RECOVERY")
print("=" * 70)


for _, row in combined.iterrows():

    route_id = row["RouteID"]

    disruption_id = row["DisruptionID"]

    disruption_type = str(
        row["DisruptionType"]
    )

    severity = str(
        row["Severity"]
    )

    delay_minutes = float(
        row["DelayMinutes"]
    )

    capacity_reduction = float(
        row["CapacityReduction"]
    )


    # --------------------------------------------------------
    # Original route
    # --------------------------------------------------------

    original_distance = route_info[
        route_id
    ]["distance"]

    original_time = route_info[
        route_id
    ]["time"]

    total_stops = route_info[
        route_id
    ]["stops"]


    # --------------------------------------------------------
    # Disruption distance impact
    # --------------------------------------------------------

    if disruption_type == "ROAD_CLOSURE":

        distance_impact = (
            original_distance * 0.08
        )

    elif disruption_type == "NEW_STOP":

        distance_impact = (
            original_distance * 0.05
        )

    elif disruption_type == "TRAFFIC_DELAY":

        distance_impact = (
            original_distance * 0.02
        )

    elif disruption_type == "VEHICLE_CAPACITY_REDUCTION":

        distance_impact = (
            original_distance * 0.03
        )

    else:

        distance_impact = 0


    # --------------------------------------------------------
    # Disrupted distance
    # --------------------------------------------------------

    disrupted_distance = (
        original_distance
        + distance_impact
    )


    # --------------------------------------------------------
    # Disruption time impact
    # --------------------------------------------------------

    delay_hours = (
        delay_minutes / 60
    )

    disrupted_time = (
        original_time
        + delay_hours
    )


    # --------------------------------------------------------
    # Rerouted route
    # --------------------------------------------------------

    rerouted_distance = float(
        row["ReroutedDistance(KM)"]
    )

    rerouted_time = float(
        row["ReroutedTime(Hours)"]
    )


    # --------------------------------------------------------
    # Distance impact
    # --------------------------------------------------------

    distance_impact = (
        disrupted_distance
        - original_distance
    )


    # --------------------------------------------------------
    # Distance recovered
    # --------------------------------------------------------

    distance_recovered = (
        disrupted_distance
        - rerouted_distance
    )

    distance_recovered = max(
        distance_recovered,
        0
    )


    # --------------------------------------------------------
    # Time impact
    # --------------------------------------------------------

    time_impact = (
        disrupted_time
        - original_time
    )


    # --------------------------------------------------------
    # Time recovered
    # --------------------------------------------------------

    time_recovered = (
        disrupted_time
        - rerouted_time
    )

    time_recovered = max(
        time_recovered,
        0
    )


    # --------------------------------------------------------
    # Distance recovery %
    # --------------------------------------------------------

    if distance_impact > 0:

        distance_recovery = (
            distance_recovered
            / distance_impact
        ) * 100

    else:

        distance_recovery = 0


    # --------------------------------------------------------
    # Time recovery %
    # --------------------------------------------------------

    if time_impact > 0:

        time_recovery = (
            time_recovered
            / time_impact
        ) * 100

    else:

        time_recovery = 0


    # --------------------------------------------------------
    # Combined recovery efficiency
    # --------------------------------------------------------

    recovery_efficiency = (
        distance_recovery
        + time_recovery
    ) / 2


    # --------------------------------------------------------
    # Limit percentages
    # --------------------------------------------------------

    distance_recovery = min(
        max(distance_recovery, 0),
        100
    )

    time_recovery = min(
        max(time_recovery, 0),
        100
    )

    recovery_efficiency = min(
        max(recovery_efficiency, 0),
        100
    )


    # --------------------------------------------------------
    # Successful recovery
    # --------------------------------------------------------

    successful_recovery = (

        rerouted_distance
        <= disrupted_distance

        and

        rerouted_time
        <= disrupted_time
    )


    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

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

        "TotalStops":
            total_stops,

        "OriginalDistance(KM)":
            round(
                original_distance,
                2
            ),

        "DisruptedDistance(KM)":
            round(
                disrupted_distance,
                2
            ),

        "ReroutedDistance(KM)":
            round(
                rerouted_distance,
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

        "DistanceImpact(KM)":
            round(
                distance_impact,
                2
            ),

        "DistanceRecovered(KM)":
            round(
                distance_recovered,
                2
            ),

        "TimeImpact(Hours)":
            round(
                time_impact,
                2
            ),

        "TimeRecovered(Hours)":
            round(
                time_recovered,
                2
            ),

        "DistanceRecovery(%)":
            round(
                distance_recovery,
                2
            ),

        "TimeRecovery(%)":
            round(
                time_recovery,
                2
            ),

        "RecoveryEfficiency(%)":
            round(
                recovery_efficiency,
                2
            ),

        "SuccessfulRecovery":
            successful_recovery
    })


# ============================================================
# CREATE DATAFRAME
# ============================================================

results_df = pd.DataFrame(
    results
)


# ============================================================
# SAVE
# ============================================================

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("RECOVERY EVALUATION COMPLETED")
print("=" * 70)

print()

print(
    f"Total disruption scenarios : "
    f"{len(results_df)}"
)


if len(results_df) > 0:

    successful = (
        results_df[
            "SuccessfulRecovery"
        ]
        .sum()
    )

    success_rate = (
        successful
        / len(results_df)
    ) * 100


    avg_distance_impact = (
        results_df[
            "DistanceImpact(KM)"
        ]
        .mean()
    )


    avg_distance_recovered = (
        results_df[
            "DistanceRecovered(KM)"
        ]
        .mean()
    )


    avg_time_impact = (
        results_df[
            "TimeImpact(Hours)"
        ]
        .mean()
    )


    avg_time_recovered = (
        results_df[
            "TimeRecovered(Hours)"
        ]
        .mean()
    )


    avg_efficiency = (
        results_df[
            "RecoveryEfficiency(%)"
        ]
        .mean()
    )


    print(
        f"Successful recoveries      : "
        f"{successful}/{len(results_df)}"
    )

    print(
        f"Recovery success rate      : "
        f"{success_rate:.2f}%"
    )

    print(
        f"Average distance impact    : "
        f"{avg_distance_impact:.2f} KM"
    )

    print(
        f"Average distance recovered : "
        f"{avg_distance_recovered:.2f} KM"
    )

    print(
        f"Average time impact        : "
        f"{avg_time_impact:.2f} Hours"
    )

    print(
        f"Average time recovered     : "
        f"{avg_time_recovered:.2f} Hours"
    )

    print(
        f"Average recovery efficiency: "
        f"{avg_efficiency:.2f}%"
    )


# ============================================================
# DISRUPTION TYPE PERFORMANCE
# ============================================================

if len(results_df) > 0:

    print()
    print("DISRUPTION RECOVERY PERFORMANCE")
    print()

    performance = (
        results_df
        .groupby("DisruptionType")
        .agg(

            Scenarios=(
                "DisruptionID",
                "count"
            ),

            Successful=(
                "SuccessfulRecovery",
                "sum"
            ),

            AvgDistanceImpact=(
                "DistanceImpact(KM)",
                "mean"
            ),

            AvgDistanceRecovered=(
                "DistanceRecovered(KM)",
                "mean"
            ),

            AvgTimeImpact=(
                "TimeImpact(Hours)",
                "mean"
            ),

            AvgTimeRecovered=(
                "TimeRecovered(Hours)",
                "mean"
            ),

            AvgRecoveryEfficiency=(
                "RecoveryEfficiency(%)",
                "mean"
            )
        )
        .reset_index()
    )


    performance[
        "SuccessRate(%)"
    ] = (

        performance["Successful"]
        /
        performance["Scenarios"]

    ) * 100


    performance = performance.round(2)

    print(performance)


# ============================================================
# SEVERITY PERFORMANCE
# ============================================================

if len(results_df) > 0:

    print()
    print("SEVERITY RECOVERY PERFORMANCE")
    print()

    severity = (
        results_df
        .groupby("Severity")
        .agg(

            Scenarios=(
                "DisruptionID",
                "count"
            ),

            Successful=(
                "SuccessfulRecovery",
                "sum"
            ),

            AvgDistanceImpact=(
                "DistanceImpact(KM)",
                "mean"
            ),

            AvgTimeImpact=(
                "TimeImpact(Hours)",
                "mean"
            ),

            AvgRecoveryEfficiency=(
                "RecoveryEfficiency(%)",
                "mean"
            )
        )
        .reset_index()
    )


    severity[
        "SuccessRate(%)"
    ] = (

        severity["Successful"]
        /
        severity["Scenarios"]

    ) * 100


    severity = severity.round(2)

    print(severity)


# ============================================================
# OUTPUT
# ============================================================

print()
print("Results saved to:")
print(OUTPUT_FILE)

print("=" * 70)