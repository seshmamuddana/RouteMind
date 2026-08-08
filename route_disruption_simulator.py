import pandas as pd
import random
import uuid

# ============================================================
# CONFIGURATION
# ============================================================

DATA_FILE = "processed_dataset.csv"
OPTIMIZED_FILE = "improved_optimizer_results.csv"
OUTPUT_FILE = "route_disruptions.csv"

# Number of disruptions to generate per route
DISRUPTIONS_PER_ROUTE = 2

# Make results reproducible
random.seed(42)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_FILE)

optimized_df = pd.read_csv(
    OPTIMIZED_FILE
)


# ============================================================
# DISRUPTION TYPES
# ============================================================

DISRUPTION_TYPES = [
    "TRAFFIC_DELAY",
    "ROAD_CLOSURE",
    "VEHICLE_CAPACITY_REDUCTION",
    "NEW_STOP"
]


# ============================================================
# SEVERITY LEVELS
# ============================================================

SEVERITIES = [
    "LOW",
    "MEDIUM",
    "HIGH"
]


# ============================================================
# GENERATE TRAFFIC DELAY
# ============================================================

def generate_traffic_delay(route_id, route_df):

    stop = route_df.sample(
        n=1
    ).iloc[0]

    severity = random.choice(
        SEVERITIES
    )

    if severity == "LOW":
        delay_minutes = random.randint(
            5,
            15
        )

    elif severity == "MEDIUM":
        delay_minutes = random.randint(
            15,
            30
        )

    else:
        delay_minutes = random.randint(
            30,
            60
        )

    return {

        "DisruptionID":
            "DISRUPTION_" + str(uuid.uuid4()),

        "RouteID":
            route_id,

        "DisruptionType":
            "TRAFFIC_DELAY",

        "Severity":
            severity,

        "StopID":
            stop["StopID"],

        "Latitude":
            stop["Latitude"],

        "Longitude":
            stop["Longitude"],

        "DelayMinutes":
            delay_minutes,

        "CapacityReduction":
            0,

        "Description":
            f"Traffic delay of "
            f"{delay_minutes} minutes "
            f"near stop {stop['StopID']}"
    }


# ============================================================
# GENERATE ROAD CLOSURE
# ============================================================

def generate_road_closure(route_id, route_df):

    stop = route_df.sample(
        n=1
    ).iloc[0]

    severity = random.choice(
        [
            "MEDIUM",
            "HIGH"
        ]
    )

    return {

        "DisruptionID":
            "DISRUPTION_" + str(uuid.uuid4()),

        "RouteID":
            route_id,

        "DisruptionType":
            "ROAD_CLOSURE",

        "Severity":
            severity,

        "StopID":
            stop["StopID"],

        "Latitude":
            stop["Latitude"],

        "Longitude":
            stop["Longitude"],

        "DelayMinutes":
            0,

        "CapacityReduction":
            0,

        "Description":
            f"Road closure affecting "
            f"stop {stop['StopID']}"
    }


# ============================================================
# GENERATE VEHICLE CAPACITY REDUCTION
# ============================================================

def generate_capacity_reduction(
    route_id,
    route_df
):

    stop = route_df.sample(
        n=1
    ).iloc[0]

    severity = random.choice(
        SEVERITIES
    )

    if severity == "LOW":

        reduction = random.randint(
            5,
            10
        )

    elif severity == "MEDIUM":

        reduction = random.randint(
            10,
            25
        )

    else:

        reduction = random.randint(
            25,
            50
        )

    return {

        "DisruptionID":
            "DISRUPTION_" + str(uuid.uuid4()),

        "RouteID":
            route_id,

        "DisruptionType":
            "VEHICLE_CAPACITY_REDUCTION",

        "Severity":
            severity,

        "StopID":
            stop["StopID"],

        "Latitude":
            stop["Latitude"],

        "Longitude":
            stop["Longitude"],

        "DelayMinutes":
            0,

        "CapacityReduction":
            reduction,

        "Description":
            f"Vehicle capacity reduced "
            f"by {reduction} stops"
    }


# ============================================================
# GENERATE NEW STOP
# ============================================================

def generate_new_stop(
    route_id,
    route_df
):

    # Pick an existing stop as a geographic
    # reference point.

    reference = route_df.sample(
        n=1
    ).iloc[0]

    # Small geographic variation
    # around the existing route.

    latitude = (
        reference["Latitude"]
        + random.uniform(
            -0.01,
            0.01
        )
    )

    longitude = (
        reference["Longitude"]
        + random.uniform(
            -0.01,
            0.01
        )
    )

    severity = random.choice(
        [
            "LOW",
            "MEDIUM"
        ]
    )

    return {

        "DisruptionID":
            "DISRUPTION_" + str(uuid.uuid4()),

        "RouteID":
            route_id,

        "DisruptionType":
            "NEW_STOP",

        "Severity":
            severity,

        "StopID":
            "NEW_STOP_" + str(
                uuid.uuid4()
            ),

        "Latitude":
            latitude,

        "Longitude":
            longitude,

        "DelayMinutes":
            0,

        "CapacityReduction":
            0,

        "Description":
            "New delivery stop "
            "added to route"
    }


# ============================================================
# GENERATE DISRUPTION
# ============================================================

def generate_disruption(
    route_id,
    route_df
):

    disruption_type = random.choice(
        DISRUPTION_TYPES
    )

    if disruption_type == "TRAFFIC_DELAY":

        return generate_traffic_delay(
            route_id,
            route_df
        )

    elif disruption_type == "ROAD_CLOSURE":

        return generate_road_closure(
            route_id,
            route_df
        )

    elif disruption_type == "VEHICLE_CAPACITY_REDUCTION":

        return generate_capacity_reduction(
            route_id,
            route_df
        )

    else:

        return generate_new_stop(
            route_id,
            route_df
        )


# ============================================================
# MAIN SIMULATION
# ============================================================

print("=" * 70)

print(
    "ROUTE DISRUPTION SIMULATOR"
)

print("=" * 70)

print()

route_ids = optimized_df[
    "RouteID"
].unique()

print(
    f"Total Routes: {len(route_ids)}"
)

print(
    f"Disruptions per Route: "
    f"{DISRUPTIONS_PER_ROUTE}"
)

print()


# ============================================================
# GENERATE DISRUPTIONS
# ============================================================

disruptions = []

for route_id in route_ids:

    route_df = df[
        df["RouteID"] == route_id
    ].copy()

    if len(route_df) == 0:

        print(
            f"Skipping {route_id}: "
            "route not found"
        )

        continue

    print(
        f"Generating disruptions: "
        f"{route_id}"
    )

    for _ in range(
        DISRUPTIONS_PER_ROUTE
    ):

        disruption = generate_disruption(
            route_id,
            route_df
        )

        disruptions.append(
            disruption
        )


# ============================================================
# CREATE DATAFRAME
# ============================================================

disruptions_df = pd.DataFrame(
    disruptions
)


# ============================================================
# SAVE RESULTS
# ============================================================

disruptions_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()

print("=" * 70)

print(
    "DISRUPTION SIMULATION COMPLETED"
)

print("=" * 70)

print()

print(
    f"Total disruptions generated: "
    f"{len(disruptions_df)}"
)

print()

print(
    disruptions_df[
        [
            "DisruptionID",
            "RouteID",
            "DisruptionType",
            "Severity",
            "StopID",
            "DelayMinutes",
            "CapacityReduction"
        ]
    ].head(20)
)


# ============================================================
# DISRUPTION SUMMARY
# ============================================================

print()

print(
    "DISRUPTION TYPE SUMMARY"
)

print()

print(
    disruptions_df[
        "DisruptionType"
    ].value_counts()
)


# ============================================================
# SEVERITY SUMMARY
# ============================================================

print()

print(
    "SEVERITY SUMMARY"
)

print()

print(
    disruptions_df[
        "Severity"
    ].value_counts()
)


# ============================================================
# OUTPUT
# ============================================================

print()

print(
    "Results saved to:"
)

print(
    OUTPUT_FILE
)