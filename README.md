#  Track 3: RouteMind
## Adaptive Route Optimization for the Supply Chain

## 📌 Project Overview

RouteMind is an AI-powered route optimization system designed to improve first-mile, middle-mile, and last-mile logistics. The project utilizes the Amazon Last Mile Routing Research Challenge Dataset to analyze delivery routes, preprocess logistics data, and prepare it for intelligent route optimization and real-time replanning.

---

##  Workflow

```text
route_features.csv
        │
        ▼
Load Dataset
        │
        ▼
Preprocessing of data
        │
        ▼
Feature Selection
        │
        ▼
Train-Test Split
(80% Train | 20% Test)
        │
        ▼
Random Forest Classifier
        │
        ▼
Model Evaluation
(Accuracy & Classification Report)
        │
        ▼
Save Trained Model
(route_model.pkl)
```

---

# Step 1: Data Collection

### Dataset Used

**Amazon Last Mile Routing Research Challenge (2021)**

The project uses Amazon's real-world delivery dataset containing historical delivery operations.

### Dataset Files

- **route_data.json** – Route information, delivery stops, station details, vehicle capacity, and route metadata.
- **package_data.json** – Package information for every delivery stop.
- **travel_times.json** – Travel time matrix between delivery locations.
- **actual_sequences.json** – Actual delivery sequence followed by drivers.

---

# Step 2: Data Preprocessing

The raw Amazon dataset is distributed across multiple JSON files. The preprocessing stage transforms this data into a single structured dataset.

### Tasks Performed

- Loaded all routing datasets.
- Extracted route information (Route ID, Station, Date, Vehicle Capacity, Route Score).
- Extracted stop information (Stop ID, Latitude, Longitude, Stop Type, Zone ID).
- Mapped each stop to its actual delivery sequence.
- Combined the extracted data into a single Pandas DataFrame.
- Sorted the dataset by Route ID and Actual Delivery Sequence.
- Exported the final dataset as **processed_dataset.csv**.

---

# Step 3: Feature Engineering

Feature engineering was performed to transform the preprocessed dataset into a format suitable for route optimization and AI analysis.

### Tasks Performed

- Generated time-based features (Departure Hour, Day of Week, Peak Hour).
- Calculated distance between consecutive delivery stops using latitude and longitude.
- Created route-level features such as Total Stops, Total Distance, Average Stop Distance, and Vehicle Capacity.
- Derived optimization metrics including Dropoff Ratio, Distance per Stop, Capacity Utilization, and Stops per Kilometer.
- Generated the final feature-engineered dataset (**route_features.csv**).

---

# Step 4: Model Training

A Machine Learning model was trained to predict the **Route Score** using the engineered route features.

### Tasks Performed

- Loaded the feature-engineered dataset (**route_features.csv**).
- Encoded the target variable (**RouteScore**) using Label Encoding.
- Selected relevant route features for training.
- Split the dataset into training and testing sets (80% Train | 20% Test).
- Trained a Random Forest Classifier.
- Evaluated the model using Accuracy Score and Classification Report.
- Saved the trained model and label encoder.

### Model Used

-  Random Forest Classifier

---
