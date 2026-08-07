import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2


# -------------------------------
# Load Preprocessed Dataset
# -------------------------------

df = pd.read_csv("processed_dataset.csv")

print("Dataset Loaded")
print(df.head())


# -------------------------------
# Clean Data
# -------------------------------

df["Date"] = pd.to_datetime(df["Date"])

df["DepartureTime"] = pd.to_datetime(
    df["DepartureTime"],
    format="%H:%M:%S"
)

df = df.sort_values(
    ["RouteID", "ActualSequence"]
)


# -------------------------------
# Time Features
# -------------------------------

df["DepartureHour"] = df["DepartureTime"].dt.hour

df["DayOfWeek"] = df["Date"].dt.dayofweek


df["PeakHour"] = df["DepartureHour"].apply(
    lambda x: 1 if x in [8,9,10,17,18,19] else 0
)


# -------------------------------
# Distance Calculation Function
# -------------------------------

def calculate_distance(lat1, lon1, lat2, lon2):

    R = 6371  # Earth radius in KM

    lat1 = radians(lat1)
    lon1 = radians(lon1)

    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1


    a = (
        sin(dlat/2)**2 +
        cos(lat1) *
        cos(lat2) *
        sin(dlon/2)**2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1-a)
    )

    return R*c



# -------------------------------
# Calculate Distance Between Stops
# -------------------------------

df["SegmentDistance"] = 0.0


for route, group in df.groupby("RouteID"):

    indexes = group.index.tolist()

    for i in range(len(indexes)-1):

        current = indexes[i]
        nxt = indexes[i+1]


        distance = calculate_distance(
            df.loc[current,"Latitude"],
            df.loc[current,"Longitude"],
            df.loc[nxt,"Latitude"],
            df.loc[nxt,"Longitude"]
        )


        df.loc[current,"SegmentDistance"] = distance



# -------------------------------
# Generate Route Level Features
# -------------------------------


route_features = df.groupby("RouteID").agg(

    # Route complexity
    TotalStops = (
        "StopID",
        "count"
    ),


    # Distance
    TotalDistance = (
        "SegmentDistance",
        "sum"
    ),


    AverageStopDistance = (
        "SegmentDistance",
        "mean"
    ),


    # Vehicle information
    VehicleCapacity = (
        "Capacity",
        "first"
    ),


    # Starting location
    Station = (
        "Station",
        "first"
    ),


    # Time features
    DepartureHour = (
        "DepartureHour",
        "first"
    ),


    DayOfWeek = (
        "DayOfWeek",
        "first"
    ),


    PeakHour = (
        "PeakHour",
        "first"
    ),


    # Delivery features
    DropoffCount = (
        "StopType",
        lambda x: sum(x=="Dropoff")
    ),


    # Target information
    RouteScore = (
        "RouteScore",
        "first"
    )

).reset_index()



# -------------------------------
# Additional Features
# -------------------------------


route_features["DropoffRatio"] = (
    route_features["DropoffCount"] /
    route_features["TotalStops"]
)


route_features["DistancePerStop"] = (
    route_features["TotalDistance"] /
    route_features["TotalStops"]
)


route_features["CapacityUtilization"] = (
    route_features["DropoffCount"] /
    (route_features["VehicleCapacity"] / 1000)
)


route_features["StopsPerKM"] = (
    route_features["TotalStops"] /
    route_features["TotalDistance"]
)



# -------------------------------
# Encode Categorical Features
# -------------------------------


categorical_columns = [
    "Station"
]


for col in categorical_columns:

    route_features[col] = (
        route_features[col]
        .astype("category")
        .cat.codes
    )



# -------------------------------
# Save Final Features
# -------------------------------

route_features.to_csv(
    "route_features.csv",
    index=False
)


print("\nFeature Engineering Completed!")

print(
    route_features.head()
)

print(
    "\nFinal Shape:",
    route_features.shape
)