import pandas as pd
import numpy as np

# ============================================================
# ROUTEMIND ML TRAINING DATA GENERATOR
# ============================================================

print("=" * 70)
print("ROUTEMIND ML TRAINING DATA GENERATOR")
print("=" * 70)

# ============================================================
# LOAD EXISTING AI DECISIONS
# ============================================================

data = pd.read_csv(
    "ai_route_decisions.csv"
)

print()
print("Original scenarios :", len(data))

# ============================================================
# SET RANDOM SEED
# ============================================================

np.random.seed(42)

# ============================================================
# CREATE EXPANDED DATASET
#
# Each original scenario generates multiple realistic
# variations so the ML model has more training examples.
# ============================================================

expanded = []

VARIATIONS_PER_SCENARIO = 20

for _, row in data.iterrows():

    for _ in range(VARIATIONS_PER_SCENARIO):

        new_row = row.copy()

        # ----------------------------------------------------
        # Delay variation
        # ----------------------------------------------------

        original_delay = float(
            row["DelayMinutes"]
        )

        if original_delay > 0:

            new_delay = original_delay * np.random.uniform(
                0.75,
                1.25
            )

        else:

            new_delay = np.random.choice(
                [0, 0, 0, 5, 10]
            )

        new_row["DelayMinutes"] = round(
            max(0, new_delay),
            2
        )

        # ----------------------------------------------------
        # Capacity variation
        # ----------------------------------------------------

        original_capacity = float(
            row["CapacityReduction"]
        )

        if original_capacity > 0:

            new_capacity = original_capacity * np.random.uniform(
                0.80,
                1.20
            )

        else:

            new_capacity = np.random.choice(
                [0, 0, 0, 5]
            )

        new_row["CapacityReduction"] = round(
            max(0, new_capacity),
            2
        )

        # ----------------------------------------------------
        # Stops lost variation
        # ----------------------------------------------------

        original_stops_lost = float(
            row["StopsLost"]
        )

        if original_stops_lost > 0:

            new_stops_lost = original_stops_lost * np.random.uniform(
                0.80,
                1.20
            )

        else:

            new_stops_lost = np.random.choice(
                [0, 0, 0, 1]
            )

        new_row["StopsLost"] = int(
            max(0, round(new_stops_lost))
        )

        # ----------------------------------------------------
        # Distance impact variation
        # ----------------------------------------------------

        original_distance = float(
            row["DistanceChange(KM)"]
        )

        new_distance = original_distance * np.random.uniform(
            0.85,
            1.15
        )

        new_row["DistanceChange(KM)"] = round(
            new_distance,
            2
        )

        # ----------------------------------------------------
        # Time impact variation
        # ----------------------------------------------------

        original_time = float(
            row["TimeChange(Hours)"]
        )

        new_time = original_time * np.random.uniform(
            0.85,
            1.15
        )

        new_row["TimeChange(Hours)"] = round(
            new_time,
            3
        )

        # ----------------------------------------------------
        # Recovery efficiency variation
        # ----------------------------------------------------

        original_recovery = float(
            row["RecoveryEfficiency(%)"]
        )

        new_recovery = original_recovery * np.random.uniform(
            0.90,
            1.05
        )

        new_row["RecoveryEfficiency(%)"] = round(
            np.clip(new_recovery, 0, 100),
            2
        )

        # ----------------------------------------------------
        # Route size variation
        # ----------------------------------------------------

        original_stops = float(
            row["TotalStops"]
        )

        new_stops = original_stops * np.random.uniform(
            0.95,
            1.05
        )

        new_row["TotalStops"] = int(
            max(1, round(new_stops))
        )

        # ----------------------------------------------------
        # Calculate ML target risk score
        #
        # We use the existing AI rule engine as the
        # baseline label generator.
        # ----------------------------------------------------

        score = 0

        # Severity
        severity = str(
            new_row["Severity"]
        ).upper()

        if severity == "HIGH":
            score += 35

        elif severity == "MEDIUM":
            score += 20

        elif severity == "LOW":
            score += 5

        # Disruption type
        disruption = new_row["DisruptionType"]

        if disruption == "ROAD_CLOSURE":
            score += 25

        elif disruption == "TRAFFIC_DELAY":
            score += 15

        elif disruption == "VEHICLE_CAPACITY_REDUCTION":
            score += 20

        elif disruption == "NEW_STOP":
            score += 10

        # Delay
        delay = new_row["DelayMinutes"]

        if delay >= 40:
            score += 20

        elif delay >= 20:
            score += 12

        elif delay >= 10:
            score += 6

        # Capacity
        capacity = new_row["CapacityReduction"]

        if capacity >= 30:
            score += 20

        elif capacity >= 15:
            score += 12

        elif capacity > 0:
            score += 5

        # Stops lost
        stops_lost = new_row["StopsLost"]

        if stops_lost >= 10:
            score += 15

        elif stops_lost >= 5:
            score += 8

        elif stops_lost > 0:
            score += 3

        # Time impact
        time_change = abs(
            new_row["TimeChange(Hours)"]
        )

        if time_change >= 1:
            score += 15

        elif time_change >= 0.5:
            score += 8

        elif time_change > 0.2:
            score += 3

        # Route size
        total_stops = new_row["TotalStops"]

        if total_stops >= 180:
            score += 8

        elif total_stops >= 150:
            score += 5

        elif total_stops >= 120:
            score += 2

        # Recovery efficiency
        recovery = new_row[
            "RecoveryEfficiency(%)"
        ]

        if recovery < 80:
            score += 10

        elif recovery < 90:
            score += 5

        score = min(
            score,
            100
        )

        new_row["MLRiskScore"] = score

        # ----------------------------------------------------
        # ML TARGET
        # ----------------------------------------------------

        if score >= 70:

            new_row["MLRiskLevel"] = "HIGH"

        elif score >= 40:

            new_row["MLRiskLevel"] = "MEDIUM"

        else:

            new_row["MLRiskLevel"] = "LOW"

        expanded.append(
            new_row
        )

# ============================================================
# CREATE DATAFRAME
# ============================================================

training_data = pd.DataFrame(
    expanded
)

# ============================================================
# REMOVE IDENTIFIERS
#
# IDs are not useful predictive features.
# ============================================================

drop_columns = [
    "RouteID",
    "DisruptionID",
    "AI_Decision",
    "Recommendation",
    "RiskScore",
    "RiskLevel",
    "PriorityScore",
    "RecoverySuccessful"
]

for column in drop_columns:

    if column in training_data.columns:

        training_data = training_data.drop(
            columns=column
        )

# ============================================================
# SAVE DATASET
# ============================================================

training_data.to_csv(
    "route_ml_training_data.csv",
    index=False
)

# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("ML TRAINING DATASET CREATED")
print("=" * 70)

print()

print(
    "Original scenarios :",
    len(data)
)

print(
    "Generated samples  :",
    len(training_data)
)

print()

print("Risk Distribution")

print(
    training_data[
        "MLRiskLevel"
    ].value_counts()
)

print()

print(
    "Average ML Risk Score :",
    round(
        training_data[
            "MLRiskScore"
        ].mean(),
        2
    )
)

print()

print(
    "Training columns :"
)

print(
    list(
        training_data.columns
    )
)

print()

print("=" * 70)

print(
    "Training dataset saved to:"
)

print(
    "route_ml_training_data.csv"
)

print("=" * 70)