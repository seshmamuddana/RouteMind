import pandas as pd
import numpy as np

# ============================================================
# ROUTEMIND AI DECISION LAYER
# ============================================================

print("=" * 70)
print("ROUTEMIND AI DECISION ENGINE")
print("=" * 70)

# ============================================================
# LOAD DATA
# ============================================================

processed = pd.read_csv(
    "processed_dataset.csv"
)

disruptions = pd.read_csv(
    "route_disruptions.csv"
)

rerouting = pd.read_csv(
    "realtime_rerouting_results.csv"
)

optimizer = pd.read_csv(
    "improved_optimizer_results.csv"
)

print()
print("Processed records  :", len(processed))
print("Disruptions        :", len(disruptions))
print("Rerouting results  :", len(rerouting))
print("Optimizer results  :", len(optimizer))

# ============================================================
# PREPARE ROUTE FEATURES
# ============================================================

route_features = (
    processed
    .groupby("RouteID")
    .agg(
        TotalStops=("StopID", "count"),
        AvgLatitude=("Latitude", "mean"),
        AvgLongitude=("Longitude", "mean")
    )
    .reset_index()
)

# ============================================================
# ADD OPTIMIZER PERFORMANCE
# ============================================================

optimizer_features = optimizer[
    [
        "RouteID",
        "TotalStops",
        "Improvement(%)"
    ]
].copy()

optimizer_features = optimizer_features.rename(
    columns={
        "TotalStops": "OptimizerStops",
        "Improvement(%)": "OptimizationImprovement"
    }
)

route_features = route_features.merge(
    optimizer_features,
    on="RouteID",
    how="left"
)

# ============================================================
# MERGE DISRUPTION + REROUTING DATA
# ============================================================

data = disruptions.merge(
    rerouting[
        [
            "RouteID",
            "DisruptionID",
            "ReroutedStops",
            "StopsLost",
            "OriginalDistance(KM)",
            "ReroutedDistance(KM)",
            "DistanceChange(KM)",
            "OriginalTime(Hours)",
            "DisruptedTime(Hours)",
            "ReroutedTime(Hours)",
            "TimeChange(Hours)",
            "RecoveryEfficiency(%)",
            "RecoverySuccessful"
        ]
    ],
    on=["RouteID", "DisruptionID"],
    how="left"
)

# ============================================================
# ADD ROUTE FEATURES
# ============================================================

data = data.merge(
    route_features,
    on="RouteID",
    how="left"
)

# ============================================================
# CLEAN NUMERIC VALUES
# ============================================================

numeric_columns = [
    "DelayMinutes",
    "CapacityReduction",
    "TotalStops",
    "OptimizerStops",
    "OptimizationImprovement",
    "StopsLost",
    "DistanceChange(KM)",
    "TimeChange(Hours)",
    "RecoveryEfficiency(%)"
]

for column in numeric_columns:

    if column in data.columns:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

        data[column] = data[column].fillna(0)

# ============================================================
# AI RISK SCORE
#
# Maximum score = 100
#
# Factors:
#   1. Severity
#   2. Disruption type
#   3. Traffic delay
#   4. Capacity reduction
#   5. Stops lost
#   6. Time impact
#   7. Route size
#   8. Recovery efficiency
#
# Route size has intentionally LOWER weight so that
# large routes do not automatically become HIGH risk.
# ============================================================

def calculate_risk(row):

    score = 0

    # --------------------------------------------------------
    # 1. DISRUPTION SEVERITY
    # --------------------------------------------------------

    severity = str(
        row["Severity"]
    ).upper()

    if severity == "HIGH":
        score += 35

    elif severity == "MEDIUM":
        score += 20

    elif severity == "LOW":
        score += 5

    # --------------------------------------------------------
    # 2. DISRUPTION TYPE
    # --------------------------------------------------------

    disruption = row["DisruptionType"]

    if disruption == "ROAD_CLOSURE":

        score += 25

    elif disruption == "TRAFFIC_DELAY":

        score += 15

    elif disruption == "VEHICLE_CAPACITY_REDUCTION":

        score += 20

    elif disruption == "NEW_STOP":

        score += 10

    # --------------------------------------------------------
    # 3. TRAFFIC DELAY
    # --------------------------------------------------------

    delay = row["DelayMinutes"]

    if delay >= 40:

        score += 20

    elif delay >= 20:

        score += 12

    elif delay >= 10:

        score += 6

    # --------------------------------------------------------
    # 4. VEHICLE CAPACITY REDUCTION
    # --------------------------------------------------------

    capacity = row["CapacityReduction"]

    if capacity >= 30:

        score += 20

    elif capacity >= 15:

        score += 12

    elif capacity > 0:

        score += 5

    # --------------------------------------------------------
    # 5. STOPS LOST
    # --------------------------------------------------------

    stops_lost = row["StopsLost"]

    if stops_lost >= 10:

        score += 15

    elif stops_lost >= 5:

        score += 8

    elif stops_lost > 0:

        score += 3

    # --------------------------------------------------------
    # 6. TIME IMPACT
    # --------------------------------------------------------

    time_change = abs(
        row["TimeChange(Hours)"]
    )

    if time_change >= 1:

        score += 15

    elif time_change >= 0.5:

        score += 8

    elif time_change > 0.2:

        score += 3

    # --------------------------------------------------------
    # 7. ROUTE SIZE
    #
    # Lower influence than the previous version.
    # --------------------------------------------------------

    total_stops = row["TotalStops"]

    if total_stops >= 180:

        score += 8

    elif total_stops >= 150:

        score += 5

    elif total_stops >= 120:

        score += 2

    # --------------------------------------------------------
    # 8. RECOVERY EFFICIENCY
    #
    # Poor recovery capability increases risk.
    # --------------------------------------------------------

    recovery = row["RecoveryEfficiency(%)"]

    if recovery < 80:

        score += 10

    elif recovery < 90:

        score += 5

    # --------------------------------------------------------
    # LIMIT SCORE TO 100
    # --------------------------------------------------------

    return min(score, 100)


data["RiskScore"] = data.apply(
    calculate_risk,
    axis=1
)

# ============================================================
# RISK CLASSIFICATION
# ============================================================

def classify_risk(score):

    if score >= 70:

        return "HIGH"

    elif score >= 40:

        return "MEDIUM"

    else:

        return "LOW"


data["RiskLevel"] = data[
    "RiskScore"
].apply(
    classify_risk
)

# ============================================================
# AI ROUTING DECISION
# ============================================================

def routing_decision(row):

    risk = row["RiskLevel"]
    disruption = row["DisruptionType"]
    severity = str(
        row["Severity"]
    ).upper()

    # --------------------------------------------------------
    # HIGH RISK
    # --------------------------------------------------------

    if risk == "HIGH":

        return "IMMEDIATE_REROUTE"

    # --------------------------------------------------------
    # MEDIUM RISK
    # --------------------------------------------------------

    if risk == "MEDIUM":

        if disruption == "ROAD_CLOSURE":

            return "REROUTE_AVOID_CLOSED_ROAD"

        elif disruption == "TRAFFIC_DELAY":

            return "REROUTE_TRAFFIC_AVOIDANCE"

        elif disruption == "VEHICLE_CAPACITY_REDUCTION":

            return "REBALANCE_LOAD_AND_REROUTE"

        elif disruption == "NEW_STOP":

            return "INSERT_STOP_OPTIMALLY"

    # --------------------------------------------------------
    # LOW RISK
    # --------------------------------------------------------

    if risk == "LOW":

        if disruption == "NEW_STOP":

            return "INSERT_STOP_OPTIMALLY"

        elif disruption == "TRAFFIC_DELAY":

            return "MONITOR_TRAFFIC"

        elif disruption == "ROAD_CLOSURE":

            return "MONITOR_CLOSED_ROAD"

        elif disruption == "VEHICLE_CAPACITY_REDUCTION":

            return "MONITOR_CAPACITY"

    return "MONITOR_ROUTE"


data["AI_Decision"] = data.apply(
    routing_decision,
    axis=1
)

# ============================================================
# PRIORITY SCORE
#
# Risk is the main factor.
# Delay and lost stops increase operational priority.
# ============================================================

data["PriorityScore"] = (
    data["RiskScore"] * 0.70
    + data["DelayMinutes"] * 0.20
    + data["StopsLost"] * 0.10
)

data["PriorityScore"] = (
    data["PriorityScore"]
    .clip(upper=100)
    .round(2)
)

# ============================================================
# RECOVERY RECOMMENDATION
# ============================================================

def recommendation(row):

    risk = row["RiskLevel"]
    disruption = row["DisruptionType"]

    # --------------------------------------------------------
    # HIGH RISK
    # --------------------------------------------------------

    if risk == "HIGH":

        return (
            "Trigger immediate dynamic rerouting "
            "and notify fleet operator"
        )

    # --------------------------------------------------------
    # MEDIUM RISK
    # --------------------------------------------------------

    elif risk == "MEDIUM":

        if disruption == "ROAD_CLOSURE":

            return (
                "Avoid affected road and "
                "recalculate route"
            )

        elif disruption == "TRAFFIC_DELAY":

            return (
                "Recalculate route using "
                "traffic-aware alternatives"
            )

        elif disruption == "VEHICLE_CAPACITY_REDUCTION":

            return (
                "Rebalance vehicle load and "
                "recalculate route"
            )

        elif disruption == "NEW_STOP":

            return (
                "Insert new stop at the "
                "most efficient position"
            )

        return (
            "Recalculate route and monitor "
            "constraint violations"
        )

    # --------------------------------------------------------
    # LOW RISK
    # --------------------------------------------------------

    else:

        return (
            "Continue current route and "
            "monitor disruption"
        )


data["Recommendation"] = data.apply(
    recommendation,
    axis=1
)

# ============================================================
# SORT BY PRIORITY
# ============================================================

data = data.sort_values(
    "PriorityScore",
    ascending=False
)

# ============================================================
# SELECT OUTPUT COLUMNS
# ============================================================

output_columns = [

    "RouteID",

    "DisruptionID",

    "DisruptionType",

    "Severity",

    "DelayMinutes",

    "CapacityReduction",

    "TotalStops",

    "StopsLost",

    "DistanceChange(KM)",

    "TimeChange(Hours)",

    "RecoveryEfficiency(%)",

    "RecoverySuccessful",

    "RiskScore",

    "RiskLevel",

    "PriorityScore",

    "AI_Decision",

    "Recommendation"
]

final_results = data[
    output_columns
].copy()

# ============================================================
# SAVE AI DECISIONS
# ============================================================

final_results.to_csv(
    "ai_route_decisions.csv",
    index=False
)

# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("AI DECISION SUMMARY")
print("=" * 70)

print()

print(
    "Total scenarios :",
    len(final_results)
)

# ------------------------------------------------------------
# RISK DISTRIBUTION
# ------------------------------------------------------------

print()

print("Risk Distribution")

print(
    final_results[
        "RiskLevel"
    ].value_counts()
)

# ------------------------------------------------------------
# AI DECISION DISTRIBUTION
# ------------------------------------------------------------

print()

print("AI Decision Distribution")

print(
    final_results[
        "AI_Decision"
    ].value_counts()
)

# ------------------------------------------------------------
# AVERAGE RISK
# ------------------------------------------------------------

print()

print(
    "Average Risk Score :",
    round(
        final_results[
            "RiskScore"
        ].mean(),
        2
    )
)

# ------------------------------------------------------------
# RISK COUNTS
# ------------------------------------------------------------

print()

print(
    "High Risk Routes :",
    (
        final_results[
            "RiskLevel"
        ] == "HIGH"
    ).sum()
)

print(
    "Medium Risk Routes :",
    (
        final_results[
            "RiskLevel"
        ] == "MEDIUM"
    ).sum()
)

print(
    "Low Risk Routes :",
    (
        final_results[
            "RiskLevel"
        ] == "LOW"
    ).sum()
)

# ============================================================
# AVERAGE PRIORITY
# ============================================================

print()

print(
    "Average Priority Score :",
    round(
        final_results[
            "PriorityScore"
        ].mean(),
        2
    )
)

# ============================================================
# TOP PRIORITY DISRUPTIONS
# ============================================================

print()
print("=" * 70)
print("TOP PRIORITY DISRUPTIONS")
print("=" * 70)

print()

print(
    final_results[
        [
            "RouteID",
            "DisruptionType",
            "Severity",
            "RiskScore",
            "RiskLevel",
            "PriorityScore",
            "AI_Decision"
        ]
    ].head(10)
)

# ============================================================
# FINAL MESSAGE
# ============================================================

print()
print("=" * 70)
print(
    "AI DECISION ENGINE COMPLETED"
)
print("=" * 70)

print()

print(
    "Results saved to:"
)

print(
    "ai_route_decisions.csv"
)