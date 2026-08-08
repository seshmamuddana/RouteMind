import pandas as pd
import numpy as np
import joblib


# ============================================================
# ROUTEMIND ML + AI DECISION ENGINE
# ============================================================

print("=" * 70)
print("ROUTEMIND ML + AI DECISION ENGINE")
print("=" * 70)


# ============================================================
# LOAD MODEL
# ============================================================

model = joblib.load(
    "route_ai/route_risk_model.pkl"
)


# ============================================================
# LOAD DATA
# ============================================================

disruptions = pd.read_csv(
    "route_disruptions.csv"
)

rerouting = pd.read_csv(
    "realtime_rerouting_results.csv"
)

optimizer = pd.read_csv(
    "improved_optimizer_results.csv"
)

processed = pd.read_csv(
    "processed_dataset.csv"
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
        TotalStops=("StopID", "count")
    )
    .reset_index()
)


# ============================================================
# OPTIMIZER FEATURES
# ============================================================

optimizer_features = optimizer[
    [
        "RouteID",
        "Improvement(%)"
    ]
].copy()


optimizer_features = optimizer_features.rename(
    columns={
        "Improvement(%)":
        "OptimizationImprovement"
    }
)


# ============================================================
# MERGE DISRUPTION + REROUTING
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
    on=[
        "RouteID",
        "DisruptionID"
    ],
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
# ADD OPTIMIZER FEATURES
# ============================================================

data = data.merge(
    optimizer_features,
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
    "StopsLost",
    "DistanceChange(KM)",
    "TimeChange(Hours)",
    "RecoveryEfficiency(%)",
    "OptimizationImprovement"
]


for column in numeric_columns:

    if column in data.columns:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

        data[column] = data[column].fillna(0)


# ============================================================
# PREPARE FEATURES FOR ML MODEL
# ============================================================

ml_features = [
    "DisruptionType",
    "Severity",
    "DelayMinutes",
    "CapacityReduction",
    "TotalStops",
    "StopsLost",
    "DistanceChange(KM)",
    "TimeChange(Hours)",
    "RecoveryEfficiency(%)"
]


X = data[
    ml_features
].copy()


# ============================================================
# CLEAN CATEGORICAL FEATURES
# ============================================================

X["DisruptionType"] = (
    X["DisruptionType"]
    .fillna("UNKNOWN")
)


X["Severity"] = (
    X["Severity"]
    .fillna("UNKNOWN")
)


# ============================================================
# ML PREDICTION
# ============================================================

print()
print("=" * 70)
print("RUNNING ML RISK PREDICTIONS")
print("=" * 70)


ml_predictions = model.predict(
    X
)


ml_probabilities = model.predict_proba(
    X
)


# ============================================================
# GET MODEL CLASSES
# ============================================================

classes = model.named_steps[
    "model"
].classes_


# ============================================================
# ADD ML RISK
# ============================================================

data[
    "MLRisk"
] = ml_predictions


# ============================================================
# ADD CLASS PROBABILITIES
# ============================================================

for index, class_name in enumerate(classes):

    data[
        f"{class_name}_Probability"
    ] = (
        ml_probabilities[:, index] * 100
    ).round(2)


# ============================================================
# ML CONFIDENCE
# ============================================================

data[
    "MLConfidence(%)"
] = (
    np.max(
        ml_probabilities,
        axis=1
    ) * 100
).round(2)


# ============================================================
# RULE-BASED OPERATIONAL RISK
# ============================================================

def operational_risk(row):

    score = 0

    disruption = row[
        "DisruptionType"
    ]

    severity = row[
        "Severity"
    ]

    delay = row[
        "DelayMinutes"
    ]

    capacity = row[
        "CapacityReduction"
    ]

    stops_lost = row[
        "StopsLost"
    ]

    time_change = abs(
        row[
            "TimeChange(Hours)"
        ]
    )


    # --------------------------------------------------------
    # Severity
    # --------------------------------------------------------

    if severity == "HIGH":
        score += 30

    elif severity == "MEDIUM":
        score += 20

    else:
        score += 10


    # --------------------------------------------------------
    # Disruption
    # --------------------------------------------------------

    if disruption == "ROAD_CLOSURE":
        score += 25

    elif disruption == "TRAFFIC_DELAY":
        score += 20

    elif disruption == "VEHICLE_CAPACITY_REDUCTION":
        score += 22

    elif disruption == "NEW_STOP":
        score += 12


    # --------------------------------------------------------
    # Delay
    # --------------------------------------------------------

    if delay >= 40:
        score += 20

    elif delay >= 20:
        score += 12

    elif delay >= 10:
        score += 6


    # --------------------------------------------------------
    # Capacity
    # --------------------------------------------------------

    if capacity >= 30:
        score += 15

    elif capacity >= 15:
        score += 10

    elif capacity > 0:
        score += 5


    # --------------------------------------------------------
    # Stops Lost
    # --------------------------------------------------------

    if stops_lost >= 20:
        score += 15

    elif stops_lost >= 10:
        score += 10

    elif stops_lost > 0:
        score += 5


    # --------------------------------------------------------
    # Time Impact
    # --------------------------------------------------------

    if time_change >= 1:
        score += 10

    elif time_change >= 0.5:
        score += 5


    return min(
        score,
        100
    )


data[
    "OperationalRiskScore"
] = data.apply(
    operational_risk,
    axis=1
)


# ============================================================
# FINAL RISK FUSION
# ============================================================

def final_risk(row):

    ml_risk = row[
        "MLRisk"
    ]

    operational = row[
        "OperationalRiskScore"
    ]

    confidence = row[
        "MLConfidence(%)"
    ]


    # Convert ML class into numerical score

    if ml_risk == "HIGH":
        ml_score = 85

    elif ml_risk == "MEDIUM":
        ml_score = 55

    else:
        ml_score = 25


    # --------------------------------------------------------
    # Confidence-weighted ML score
    # --------------------------------------------------------

    confidence_factor = (
        confidence / 100
    )


    weighted_ml = (
        ml_score *
        confidence_factor
    )


    # --------------------------------------------------------
    # Combine ML + operational logic
    # --------------------------------------------------------

    final_score = (
        weighted_ml * 0.70
        +
        operational * 0.30
    )


    return round(
        min(
            final_score,
            100
        ),
        2
    )


data[
    "FinalRiskScore"
] = data.apply(
    final_risk,
    axis=1
)


# ============================================================
# FINAL RISK CLASSIFICATION
# ============================================================

def classify_final_risk(score):

    if score >= 70:
        return "HIGH"

    elif score >= 40:
        return "MEDIUM"

    else:
        return "LOW"


data[
    "FinalRiskLevel"
] = data[
    "FinalRiskScore"
].apply(
    classify_final_risk
)


# ============================================================
# AI DECISION ENGINE
# ============================================================

def ai_decision(row):

    risk = row[
        "FinalRiskLevel"
    ]

    disruption = row[
        "DisruptionType"
    ]

    stops_lost = row[
        "StopsLost"
    ]

    delay = row[
        "DelayMinutes"
    ]

    capacity = row[
        "CapacityReduction"
    ]

    confidence = row[
        "MLConfidence(%)"
    ]


    # ========================================================
    # HIGH RISK
    # ========================================================

    if risk == "HIGH":

        if disruption == "ROAD_CLOSURE":

            return (
                "IMMEDIATE_REROUTE"
            )

        elif disruption == "VEHICLE_CAPACITY_REDUCTION":

            return (
                "IMMEDIATE_LOAD_REBALANCE"
            )

        elif disruption == "TRAFFIC_DELAY":

            return (
                "IMMEDIATE_TRAFFIC_REROUTE"
            )

        elif disruption == "NEW_STOP":

            return (
                "IMMEDIATE_STOP_INSERTION"
            )


    # ========================================================
    # MEDIUM RISK
    # ========================================================

    if risk == "MEDIUM":

        if disruption == "ROAD_CLOSURE":

            return (
                "REROUTE_AVOID_CLOSED_ROAD"
            )

        elif disruption == "TRAFFIC_DELAY":

            return (
                "REROUTE_TRAFFIC_AVOIDANCE"
            )

        elif disruption == "VEHICLE_CAPACITY_REDUCTION":

            return (
                "REBALANCE_LOAD_AND_REROUTE"
            )

        elif disruption == "NEW_STOP":

            return (
                "INSERT_STOP_OPTIMALLY"
            )


    # ========================================================
    # LOW RISK
    # ========================================================

    if disruption == "TRAFFIC_DELAY":

        if delay >= 20:

            return (
                "MONITOR_TRAFFIC"
            )

    if disruption == "VEHICLE_CAPACITY_REDUCTION":

        if capacity > 0:

            return (
                "MONITOR_CAPACITY"
            )

    if disruption == "NEW_STOP":

        return (
            "INSERT_STOP_OPTIMALLY"
        )


    return "MONITOR_ROUTE"


data[
    "AI_Decision"
] = data.apply(
    ai_decision,
    axis=1
)


# ============================================================
# PRIORITY SCORE
# ============================================================

data[
    "PriorityScore"
] = (
    data[
        "FinalRiskScore"
    ] * 0.70
    +
    data[
        "MLConfidence(%)"
    ] * 0.15
    +
    data[
        "StopsLost"
    ].clip(
        upper=20
    ) * 0.75
    +
    data[
        "DelayMinutes"
    ].clip(
        upper=60
    ) * 0.25
)


data[
    "PriorityScore"
] = (
    data[
        "PriorityScore"
    ]
    .clip(
        upper=100
    )
    .round(2)
)


# ============================================================
# AI EXPLANATION
# ============================================================

def explanation(row):

    risk = row[
        "FinalRiskLevel"
    ]

    disruption = row[
        "DisruptionType"
    ]

    confidence = row[
        "MLConfidence(%)"
    ]

    if disruption == "ROAD_CLOSURE":

        reason = (
            "Closed road requires alternative routing"
        )

    elif disruption == "TRAFFIC_DELAY":

        reason = (
            "Traffic delay requires congestion avoidance"
        )

    elif disruption == "VEHICLE_CAPACITY_REDUCTION":

        reason = (
            "Reduced vehicle capacity requires load balancing"
        )

    elif disruption == "NEW_STOP":

        reason = (
            "New stop requires route insertion optimization"
        )

    else:

        reason = (
            "Route should be continuously monitored"
        )


    return (
        f"{risk} risk detected with "
        f"{confidence:.1f}% ML confidence. "
        f"{reason}."
    )


data[
    "AI_Explanation"
] = data.apply(
    explanation,
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
    "AI_Explanation"
]


# ============================================================
# HANDLE PROBABILITY COLUMN NAMES
# ============================================================

probability_columns = [
    "HIGH_Probability",
    "MEDIUM_Probability",
    "LOW_Probability"
]


for column in probability_columns:

    if column not in data.columns:

        data[column] = 0


final_results = data[
    output_columns
].copy()


# ============================================================
# SAVE RESULTS
# ============================================================

final_results.to_csv(
    "ml_ai_route_decisions.csv",
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("ML + AI DECISION SUMMARY")
print("=" * 70)


print()

print(
    "Total scenarios :",
    len(final_results)
)


print()

print("ML Risk Distribution")

print(
    final_results[
        "MLRisk"
    ].value_counts()
)


print()

print("Final Risk Distribution")

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


print()

print(
    "Average ML Confidence :",
    f"{final_results['MLConfidence(%)'].mean():.2f}%"
)


print()

print(
    "Average Final Risk Score :",
    f"{final_results['FinalRiskScore'].mean():.2f}"
)


print()

print(
    "Average Priority Score :",
    f"{final_results['PriorityScore'].mean():.2f}"
)


print()

print(
    "High Risk Scenarios :",
    (
        final_results[
            "FinalRiskLevel"
        ] == "HIGH"
    ).sum()
)


print(
    "Medium Risk Scenarios :",
    (
        final_results[
            "FinalRiskLevel"
        ] == "MEDIUM"
    ).sum()
)


print(
    "Low Risk Scenarios :",
    (
        final_results[
            "FinalRiskLevel"
        ] == "LOW"
    ).sum()
)


# ============================================================
# TOP PRIORITY SCENARIOS
# ============================================================

print()
print("=" * 70)
print("TOP PRIORITY SCENARIOS")
print("=" * 70)

print()

print(
    final_results[
        [
            "RouteID",
            "DisruptionType",
            "Severity",
            "MLRisk",
            "MLConfidence(%)",
            "FinalRiskScore",
            "FinalRiskLevel",
            "PriorityScore",
            "AI_Decision"
        ]
    ].head(10)
)


# ============================================================
# SAVE HIGH PRIORITY ROUTES
# ============================================================

high_priority = final_results[
    final_results[
        "FinalRiskLevel"
    ] == "HIGH"
].copy()


high_priority.to_csv(
    "high_priority_route_decisions.csv",
    index=False
)


# ============================================================
# FINAL MESSAGE
# ============================================================

print()
print("=" * 70)
print("ML + AI DECISION ENGINE COMPLETED")
print("=" * 70)

print()

print(
    "Results saved to:"
)

print(
    "ml_ai_route_decisions.csv"
)

print()

print(
    "High-priority routes saved to:"
)

print(
    "high_priority_route_decisions.csv"
)

print("=" * 70)
