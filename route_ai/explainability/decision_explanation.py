import pandas as pd
import numpy as np

# ============================================================
# ROUTEMIND AI DECISION EXPLAINABILITY ENGINE
# ============================================================

print("=" * 70)
print("ROUTEMIND AI DECISION EXPLAINABILITY ENGINE")
print("=" * 70)

# ============================================================
# LOAD DATA
# ============================================================

input_file = "route_ai/ml_ai_route_decisions.csv"

data = pd.read_csv(input_file)

print()
print("Decision records :", len(data))

print()
print("Available columns:")
print(data.columns.tolist())

# ============================================================
# CLEAN NUMERIC COLUMNS
# ============================================================

numeric_columns = [
    "DelayMinutes",
    "CapacityReduction",
    "TotalStops",
    "StopsLost",
    "DistanceChange(KM)",
    "TimeChange(Hours)",
    "RecoveryEfficiency(%)",
    "HIGH_Probability",
    "MEDIUM_Probability",
    "LOW_Probability",
    "MLConfidence(%)",
    "OperationalRiskScore",
    "FinalRiskScore",
    "PriorityScore"
]

for column in numeric_columns:

    if column in data.columns:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

        data[column] = data[column].fillna(0)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_number(value, decimals=2):

    try:
        return f"{float(value):.{decimals}f}"
    except:
        return "0.00"


def get_severity_text(severity):

    severity = str(severity).upper()

    if severity == "HIGH":
        return "high severity"

    elif severity == "MEDIUM":
        return "medium severity"

    elif severity == "LOW":
        return "low severity"

    return "unspecified severity"


# ============================================================
# GENERATE EXPLANATION
# ============================================================

def generate_explanation(row):

    disruption = str(row["DisruptionType"])
    severity = str(row["Severity"]).upper()

    delay = float(row.get("DelayMinutes", 0))
    capacity = float(row.get("CapacityReduction", 0))
    total_stops = int(row.get("TotalStops", 0))
    stops_lost = int(row.get("StopsLost", 0))

    distance_change = float(
        row.get("DistanceChange(KM)", 0)
    )

    time_change = abs(
        float(row.get("TimeChange(Hours)", 0))
    )

    recovery_efficiency = float(
        row.get("RecoveryEfficiency(%)", 0)
    )

    ml_risk = str(
        row.get("MLRisk", "UNKNOWN")
    ).upper()

    ml_confidence = float(
        row.get("MLConfidence(%)", 0)
    )

    operational_score = float(
        row.get("OperationalRiskScore", 0)
    )

    final_score = float(
        row.get("FinalRiskScore", 0)
    )

    final_risk = str(
        row.get("FinalRiskLevel", "UNKNOWN")
    ).upper()

    priority = float(
        row.get("PriorityScore", 0)
    )

    decision = str(
        row.get("AI_Decision", "MONITOR_ROUTE")
    )

    explanation_parts = []

    # ========================================================
    # DISRUPTION EXPLANATION
    # ========================================================

    if disruption == "TRAFFIC_DELAY":

        explanation_parts.append(
            f"A traffic delay of {int(delay)} minutes was detected "
            f"with {get_severity_text(severity)}."
        )

        explanation_parts.append(
            "The delay can increase travel time and reduce "
            "delivery reliability."
        )

    elif disruption == "ROAD_CLOSURE":

        explanation_parts.append(
            f"A road closure was detected with "
            f"{get_severity_text(severity)}."
        )

        explanation_parts.append(
            "The affected road may become unavailable, "
            "requiring the route to avoid the disrupted segment."
        )

    elif disruption == "VEHICLE_CAPACITY_REDUCTION":

        explanation_parts.append(
            f"Vehicle capacity was reduced by "
            f"{format_number(capacity, 0)}%."
        )

        explanation_parts.append(
            "This can prevent the vehicle from serving all "
            "planned stops and may require load redistribution "
            "or rerouting."
        )

    elif disruption == "NEW_STOP":

        explanation_parts.append(
            "A new delivery stop was introduced into the route."
        )

        explanation_parts.append(
            "The additional stop must be inserted while "
            "maintaining route efficiency and delivery constraints."
        )

    else:

        explanation_parts.append(
            f"A {disruption.lower()} disruption was detected."
        )

    # ========================================================
    # ROUTE SIZE
    # ========================================================

    if total_stops >= 180:

        explanation_parts.append(
            f"The route contains {total_stops} stops, making it "
            "operationally complex and more sensitive to disruptions."
        )

    elif total_stops >= 150:

        explanation_parts.append(
            f"The route contains {total_stops} stops, indicating "
            "a relatively high delivery workload."
        )

    else:

        explanation_parts.append(
            f"The route contains {total_stops} planned stops."
        )

    # ========================================================
    # STOPS AFFECTED
    # ========================================================

    if stops_lost > 0:

        explanation_parts.append(
            f"{stops_lost} stops were affected during the "
            "disruption scenario."
        )

    # ========================================================
    # TIME IMPACT
    # ========================================================

    if time_change >= 1:

        explanation_parts.append(
            f"The rerouting scenario produced a significant "
            f"time impact of {format_number(time_change)} hours."
        )

    elif time_change >= 0.5:

        explanation_parts.append(
            f"The rerouting scenario produced a moderate "
            f"time impact of {format_number(time_change)} hours."
        )

    elif time_change > 0:

        explanation_parts.append(
            f"The rerouting scenario produced a relatively small "
            f"time impact of {format_number(time_change)} hours."
        )

    else:

        explanation_parts.append(
            "The rerouting scenario produced minimal time impact."
        )

    # ========================================================
    # DISTANCE IMPACT
    # ========================================================

    if distance_change < 0:

        explanation_parts.append(
            f"Route distance was reduced by approximately "
            f"{format_number(abs(distance_change))} KM."
        )

    elif distance_change > 0:

        explanation_parts.append(
            f"Route distance increased by approximately "
            f"{format_number(distance_change)} KM."
        )

    else:

        explanation_parts.append(
            "Route distance remained approximately unchanged."
        )

    # ========================================================
    # RECOVERY EFFICIENCY
    # ========================================================

    if recovery_efficiency > 0:

        explanation_parts.append(
            f"The rerouting process achieved a recovery "
            f"efficiency of {format_number(recovery_efficiency)}%."
        )

    # ========================================================
    # ML EXPLANATION
    #
    # IMPORTANT:
    # Do NOT display MLRiskScore here.
    # Use MLRisk + MLConfidence instead.
    # ========================================================

    explanation_parts.append(
        f"The machine learning model classified this scenario "
        f"as {ml_risk} risk with {format_number(ml_confidence)}% "
        f"confidence."
    )

    # ========================================================
    # COMBINED RISK
    # ========================================================

    if final_risk == "HIGH":

        explanation_parts.append(
            "The combined ML prediction and operational factors "
            "indicate a high-risk scenario requiring immediate action."
        )

    elif final_risk == "MEDIUM":

        explanation_parts.append(
            "The combined ML prediction and operational factors "
            "indicate a moderate-risk scenario requiring active monitoring "
            "and route adjustment where necessary."
        )

    else:

        explanation_parts.append(
            "The combined ML prediction and operational factors "
            "indicate a relatively low-risk scenario."
        )

    # ========================================================
    # FINAL SCORES
    # ========================================================

    explanation_parts.append(
        f"Operational risk score: "
        f"{format_number(operational_score)}."
    )

    explanation_parts.append(
        f"Final risk score: "
        f"{format_number(final_score)}."
    )

    explanation_parts.append(
        f"Priority score: "
        f"{format_number(priority)}."
    )

    # ========================================================
    # AI DECISION
    # ========================================================

    if decision == "IMMEDIATE_TRAFFIC_REROUTE":

        explanation_parts.append(
            "RouteMind recommends immediate traffic rerouting "
            "to avoid the affected congestion and protect "
            "delivery time performance."
        )

    elif decision == "IMMEDIATE_LOAD_REBALANCE":

        explanation_parts.append(
            "RouteMind recommends immediate load rebalancing "
            "because vehicle capacity has been reduced. "
            "The remaining delivery workload should be "
            "redistributed before continuing the route."
        )

    elif decision == "IMMEDIATE_REROUTE":

        explanation_parts.append(
            "RouteMind recommends immediate dynamic rerouting "
            "to minimize disruption impact and protect "
            "delivery performance."
        )

    elif decision == "REROUTE_AVOID_CLOSED_ROAD":

        explanation_parts.append(
            "RouteMind recommends rerouting to avoid the "
            "closed road segment and maintain route feasibility."
        )

    elif decision == "REROUTE_TRAFFIC_AVOIDANCE":

        explanation_parts.append(
            "RouteMind recommends traffic-aware rerouting "
            "to reduce congestion-related delays."
        )

    elif decision == "REBALANCE_LOAD_AND_REROUTE":

        explanation_parts.append(
            "RouteMind recommends redistributing the delivery "
            "load and rerouting the affected vehicle."
        )

    elif decision == "INSERT_STOP_OPTIMALLY":

        explanation_parts.append(
            "RouteMind recommends inserting the new stop at "
            "the most efficient position while maintaining "
            "route constraints."
        )

    else:

        explanation_parts.append(
            "RouteMind recommends monitoring the route and "
            "continuing the current plan unless conditions worsen."
        )

    return " ".join(explanation_parts)


# ============================================================
# EXPLANATION CATEGORY
# ============================================================

def explanation_category(row):

    risk = str(
        row["FinalRiskLevel"]
    ).upper()

    decision = str(
        row["AI_Decision"]
    ).upper()

    if risk == "HIGH":

        return "URGENT_ACTION"

    if "REROUTE" in decision:

        return "REROUTE_RECOMMENDED"

    if "INSERT" in decision or "REBALANCE" in decision:

        return "ROUTE_OPTIMIZATION"

    return "MONITORING"


# ============================================================
# GENERATE EXPLANATIONS
# ============================================================

print()
print("Generating explanations...")

data["CompleteExplanation"] = data.apply(
    generate_explanation,
    axis=1
)

data["ExplanationCategory"] = data.apply(
    explanation_category,
    axis=1
)

# ============================================================
# OUTPUT COLUMNS
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
    "MLRisk",
    "HIGH_Probability",
    "MEDIUM_Probability",
    "LOW_Probability",
    "MLConfidence(%)",
    "OperationalRiskScore",
    "FinalRiskScore",
    "FinalRiskLevel",
    "PriorityScore",
    "AI_Decision",
    "ExplanationCategory",
    "CompleteExplanation"
]

# Keep only columns that actually exist
output_columns = [
    column
    for column in output_columns
    if column in data.columns
]

final_results = data[
    output_columns
].copy()

# ============================================================
# SORT BY PRIORITY
# ============================================================

if "PriorityScore" in final_results.columns:

    final_results = final_results.sort_values(
        "PriorityScore",
        ascending=False
    )

# ============================================================
# SAVE RESULTS
# ============================================================

output_file = (
    "route_ai/explainability/"
    "ai_decision_explanations.csv"
)

final_results.to_csv(
    output_file,
    index=False
)

# ============================================================
# SUMMARY
# ============================================================

print()
print("Total explanations :", len(final_results))

print()
print("Explanation Categories")

print(
    final_results[
        "ExplanationCategory"
    ].value_counts()
)

print()
print("Risk Distribution")

print(
    final_results[
        "FinalRiskLevel"
    ].value_counts()
)

print()
print("AI Decision Distribution")

print(
    final_results[
        "AI_Decision"
    ].value_counts()
)

# ============================================================
# AVERAGES
# ============================================================

if "MLConfidence(%)" in final_results.columns:

    print()
    print(
        "Average ML Confidence :",
        round(
            final_results[
                "MLConfidence(%)"
            ].mean(),
            2
        ),
        "%"
    )

if "FinalRiskScore" in final_results.columns:

    print(
        "Average Final Risk Score :",
        round(
            final_results[
                "FinalRiskScore"
            ].mean(),
            2
        )
    )

if "PriorityScore" in final_results.columns:

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
# TOP EXPLANATIONS
# ============================================================

print()
print("=" * 70)
print("TOP PRIORITY EXPLANATIONS")
print("=" * 70)

preview_columns = [
    "RouteID",
    "DisruptionType",
    "Severity",
    "FinalRiskLevel",
    "PriorityScore",
    "AI_Decision",
    "CompleteExplanation"
]

preview_columns = [
    column
    for column in preview_columns
    if column in final_results.columns
]

print(
    final_results[
        preview_columns
    ].head(10).to_string(
        index=False
    )
)

# ============================================================
# FINAL MESSAGE
# ============================================================

print()
print("=" * 70)
print("EXPLAINABILITY ENGINE COMPLETED")
print("=" * 70)

print()
print("Results saved to:")
print(output_file)