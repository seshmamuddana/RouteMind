import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

import joblib


# ============================================================
# ROUTEMIND ML RISK MODEL
# ============================================================

print("=" * 70)
print("ROUTEMIND ML RISK PREDICTION MODEL")
print("=" * 70)


# ============================================================
# LOAD TRAINING DATA
# ============================================================

data = pd.read_csv(
    "route_ai/route_ml_training_data.csv"
)

print()
print("Training samples :", len(data))


# ============================================================
# FEATURES
# ============================================================

features = [
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


target = "MLRiskLevel"


X = data[features].copy()
y = data[target].copy()


# ============================================================
# CLEAN NUMERIC FEATURES
# ============================================================

numeric_features = [
    "DelayMinutes",
    "CapacityReduction",
    "TotalStops",
    "StopsLost",
    "DistanceChange(KM)",
    "TimeChange(Hours)",
    "RecoveryEfficiency(%)"
]


for column in numeric_features:

    X[column] = pd.to_numeric(
        X[column],
        errors="coerce"
    )

    X[column] = X[column].fillna(
        X[column].median()
    )


# ============================================================
# CATEGORICAL FEATURES
# ============================================================

categorical_features = [
    "DisruptionType",
    "Severity"
]


for column in categorical_features:

    X[column] = X[column].fillna(
        "UNKNOWN"
    )


# ============================================================
# DATASET SUMMARY
# ============================================================

print()
print("Risk Distribution")
print(
    y.value_counts()
)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print()
print("Training records :", len(X_train))
print("Testing records  :", len(X_test))


# ============================================================
# PREPROCESSING
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        ),
        (
            "numeric",
            "passthrough",
            numeric_features
        )
    ]
)


# ============================================================
# RANDOM FOREST MODEL
# ============================================================

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=12,
    min_samples_split=4,
    min_samples_leaf=2,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)


# ============================================================
# COMPLETE ML PIPELINE
# ============================================================

pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            model
        )
    ]
)


# ============================================================
# TRAIN MODEL
# ============================================================

print()
print("=" * 70)
print("TRAINING RANDOM FOREST")
print("=" * 70)

pipeline.fit(
    X_train,
    y_train
)

print()
print("Training completed.")


# ============================================================
# PREDICTIONS
# ============================================================

y_pred = pipeline.predict(
    X_test
)

y_probability = pipeline.predict_proba(
    X_test
)


# ============================================================
# MODEL EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    average="weighted",
    zero_division=0
)


print()
print("=" * 70)
print("MODEL PERFORMANCE")
print("=" * 70)

print()

print(
    f"Accuracy  : {accuracy * 100:.2f}%"
)

print(
    f"Precision : {precision * 100:.2f}%"
)

print(
    f"Recall    : {recall * 100:.2f}%"
)

print(
    f"F1 Score  : {f1 * 100:.2f}%"
)


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print()
print("=" * 70)
print("CLASSIFICATION REPORT")
print("=" * 70)

print()

print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0
    )
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

labels = [
    "HIGH",
    "MEDIUM",
    "LOW"
]


matrix = confusion_matrix(
    y_test,
    y_pred,
    labels=labels
)


confusion_df = pd.DataFrame(
    matrix,
    index=labels,
    columns=labels
)


print()
print("=" * 70)
print("CONFUSION MATRIX")
print("=" * 70)

print()

print(
    confusion_df
)


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

trained_model = pipeline.named_steps[
    "model"
]

trained_preprocessor = pipeline.named_steps[
    "preprocessor"
]


feature_names = (
    trained_preprocessor
    .get_feature_names_out()
)


importance = trained_model.feature_importances_


importance_df = pd.DataFrame(
    {
        "Feature": feature_names,
        "Importance": importance
    }
)


importance_df = importance_df.sort_values(
    "Importance",
    ascending=False
)


print()
print("=" * 70)
print("TOP FEATURE IMPORTANCE")
print("=" * 70)

print()

print(
    importance_df.head(15)
)


# ============================================================
# SAVE FEATURE IMPORTANCE
# ============================================================

importance_df.to_csv(
    "risk_model_feature_importance.csv",
    index=False
)


# ============================================================
# GENERATE PREDICTIONS FOR COMPLETE DATASET
# ============================================================

all_predictions = pipeline.predict(
    X
)

all_probabilities = pipeline.predict_proba(
    X
)


# ============================================================
# GET CLASS ORDER
# ============================================================

classes = pipeline.named_steps[
    "model"
].classes_


# ============================================================
# CREATE PREDICTION DATAFRAME
# ============================================================

prediction_results = data.copy()


prediction_results[
    "PredictedRisk"
] = all_predictions


# ============================================================
# ADD PROBABILITIES
# ============================================================

for index, class_name in enumerate(classes):

    prediction_results[
        f"{class_name}_Probability"
    ] = (
        all_probabilities[:, index] * 100
    ).round(2)


# ============================================================
# MODEL CONFIDENCE
# ============================================================

prediction_results[
    "PredictionConfidence(%)"
] = (
    np.max(
        all_probabilities,
        axis=1
    ) * 100
).round(2)


# ============================================================
# SAVE PREDICTIONS
# ============================================================

prediction_results.to_csv(
    "ml_risk_predictions.csv",
    index=False
)


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(
    pipeline,
    "route_risk_model.pkl"
)


# ============================================================
# SAVE MODEL METRICS
# ============================================================

metrics = pd.DataFrame(
    {
        "Metric": [
            "Accuracy",
            "Precision",
            "Recall",
            "F1 Score"
        ],
        "Score": [
            round(accuracy * 100, 2),
            round(precision * 100, 2),
            round(recall * 100, 2),
            round(f1 * 100, 2)
        ]
    }
)


metrics.to_csv(
    "risk_model_metrics.csv",
    index=False
)


# ============================================================
# PREDICTION DISTRIBUTION
# ============================================================

print()
print("=" * 70)
print("ML PREDICTION DISTRIBUTION")
print("=" * 70)

print()

print(
    prediction_results[
        "PredictedRisk"
    ].value_counts()
)


# ============================================================
# AVERAGE CONFIDENCE
# ============================================================

print()

print(
    "Average Prediction Confidence :",
    f"{prediction_results['PredictionConfidence(%)'].mean():.2f}%"
)


# ============================================================
# TOP RISK SCENARIOS
# ============================================================

print()
print("=" * 70)
print("TOP ML RISK PREDICTIONS")
print("=" * 70)

display_columns = [
    "DisruptionType",
    "Severity",
    "DelayMinutes",
    "CapacityReduction",
    "TotalStops",
    "StopsLost",
    "PredictedRisk",
    "PredictionConfidence(%)"
]


print()

print(
    prediction_results[
        display_columns
    ]
    .sort_values(
        "PredictionConfidence(%)",
        ascending=False
    )
    .head(10)
)


# ============================================================
# FINAL OUTPUT
# ============================================================

print()
print("=" * 70)
print("ML RISK MODEL COMPLETED")
print("=" * 70)

print()

print(
    "Model saved to:"
)

print(
    "route_risk_model.pkl"
)

print()

print(
    "Predictions saved to:"
)

print(
    "ml_risk_predictions.csv"
)

print()

print(
    "Metrics saved to:"
)

print(
    "risk_model_metrics.csv"
)

print()

print(
    "Feature importance saved to:"
)

print(
    "risk_model_feature_importance.csv"
)

print()

print("=" * 70)