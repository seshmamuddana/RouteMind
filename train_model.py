import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib


# ----------------------------
# Load dataset
# ----------------------------

df = pd.read_csv("route_features.csv")

print("Dataset loaded")
print(df.head())


# ----------------------------
# Encode target
# ----------------------------

encoder = LabelEncoder()

df["RouteScore"] = encoder.fit_transform(
    df["RouteScore"]
)


# ----------------------------
# Select features
# ----------------------------

features = [
    "TotalStops",
    "TotalDistance",
    "AverageStopDistance",
    "VehicleCapacity",
    "DepartureHour",
    "DayOfWeek",
    "PeakHour",
    "DropoffCount",
    "DropoffRatio",
    "CapacityUtilization",
    "StopsPerKM"
]


X = df[features]

y = df["RouteScore"]



# ----------------------------
# Train-test split
# ----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)



# ----------------------------
# Train model
# ----------------------------

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)


model.fit(
    X_train,
    y_train
)



# ----------------------------
# Evaluate
# ----------------------------

prediction = model.predict(
    X_test
)


accuracy = accuracy_score(
    y_test,
    prediction
)


print("\nAccuracy:")
print(accuracy)


print("\nClassification Report:")
print(
    classification_report(
        y_test,
        prediction,
        target_names=encoder.classes_
    )
)



# ----------------------------
# Save model
# ----------------------------

joblib.dump(
    model,
    "route_model.pkl"
)


joblib.dump(
    encoder,
    "label_encoder.pkl"
)


print("\nModel saved successfully!")