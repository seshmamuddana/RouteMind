
# RouteMind

### Adaptive Route Optimization for the Supply Chain

> AI-powered route optimization and dynamic route replanning system for first-mile, middle-mile, and last-mile logistics.

---

# Project Overview

RouteMind is an AI-powered route optimization system that improves first-mile, middle-mile, and last-mile logistics. The project utilizes the Amazon Last Mile Routing Research Challenge Dataset to preprocess delivery data, generate optimized routes, validate operational constraints, and support intelligent route replanning.

---

# Objectives

- Optimize delivery routes.
- Reduce travel distance and delivery time.
- Improve route quality prediction.
- Support dynamic route replanning.
- Compare optimized routes with baseline routes.

---

# Dataset

## Amazon Last Mile Routing Research Challenge (2021)

The project uses Amazon's real-world delivery dataset consisting of:

- Route Information
- Package Information
- Travel Time Matrix
- Actual Delivery Sequences

### Dataset Files

| File | Description |
|------|-------------|
| route_data.json | Route metadata and stop information |
| package_data.json | Package details |
| travel_times.json | Travel time between stops |
| actual_sequences.json | Actual delivery sequence |

---

# Project Workflow

```text
Amazon Dataset
        │
        ▼
Data Collection
        │
        ▼
Data Exploration
        │
        ▼
Data Preprocessing
        │
        ▼
Feature Engineering
        │
        ▼
Model Training
        │
        ▼
Route Optimization
        │
        ▼
Constraint Validation
        │
        ▼
Dynamic Route Replanning
        │
        ▼
AI Explanation
        │
        ▼
Dashboard & Visualization
```

---

# System Architecture

```text
                Amazon Dataset
                       │
                       ▼
             Data Preprocessing
                       │
                       ▼
            Feature Engineering
                       │
                       ▼
         Machine Learning Model
                       │
                       ▼
        Route Optimization Engine
                       │
                       ▼
       Constraint Validation
                       │
                       ▼
      Dynamic Route Replanning
                       │
                       ▼
        AI Route Explanation
                       │
                       ▼
     Dashboard & Visualization
```

---

# Step 1: Data Collection

Collected the Amazon Last Mile Routing Research Challenge Dataset containing real-world delivery operations.

### Tasks Performed

- Downloaded the routing dataset.
- Collected route information.
- Collected package information.
- Collected travel time data.
- Collected actual delivery sequences.

### Output

- route_data.json
- package_data.json
- travel_times.json
- actual_sequences.json

---

# Step 2: Data Preprocessing

The raw JSON files were cleaned and transformed into a structured dataset.

### Tasks Performed

- Loaded all routing datasets.
- Extracted route information.
- Extracted stop information.
- Mapped delivery sequences.
- Combined data into a single DataFrame.
- Sorted the dataset.
- Generated processed_dataset.csv.

### Output

- processed_dataset.csv

---

# Step 3: Feature Engineering

Generated meaningful features from the processed dataset to support machine learning and optimization.

### Tasks Performed

- Generated time-based features.
- Calculated stop-to-stop distances.
- Created route-level statistics.
- Derived optimization metrics.
- Encoded categorical features.
- Generated route_features.csv.

### Output

- route_features.csv

---

# Step 4: Model Training

Trained a machine learning model to predict route quality using the engineered features.

### Tasks Performed

- Loaded the feature dataset.
- Encoded the target variable.
- Selected training features.
- Split data into training and testing sets.
- Trained a Random Forest model.
- Evaluated model performance.
- Saved the trained model.

### Model Used

- Random Forest Classifier

### Output

- route_model.pkl
- label_encoder.pkl

---

# Step 5: Route Optimization

Generated optimized delivery routes using route optimization techniques.

### Tasks Performed

- Loaded route data.
- Optimized delivery sequences.
- Reduced travel distance.
- Improved route efficiency.
- Compared optimized and baseline routes.

### Output

- Optimized routes
- Route comparison metrics

---

# Step 6: Constraint Validation

Validated optimized routes against delivery constraints.

### Tasks Performed

- Verified vehicle capacity.
- Checked delivery time windows.
- Applied operational constraints.
- Validated optimized routes.

### Output

- Constraint-compliant routes

---

# Step 7: Dynamic Route Replanning

Generated updated routes whenever delivery conditions changed.

### Tasks Performed

- Detected delivery disruptions.
- Processed new delivery requests.
- Recalculated affected routes.
- Generated updated delivery sequences.

### Output

- Replanned routes

---

# Step 8: AI Route Explanation

Generated explanations for optimized and replanned routes.

### Tasks Performed

- Compared original and optimized routes.
- Identified reasons for route changes.
- Calculated performance improvements.
- Generated human-readable explanations.

### Output

- Route comparison summary
- AI explanation report

---

# Step 9: Dashboard & Visualization

Developed an interactive dashboard for monitoring routes and optimization results.

### Features

- Dashboard Overview
- Route Explorer
- Interactive Route Map
- Route Optimization Comparison
- Disruption Monitoring
- AI Decision Insights
- Analytics Dashboard
- Backend API Integration

---

# Tech Stack

## Frontend

- React
- Tailwind CSS
- Leaflet.js
- Recharts

## Backend

- Python
- FastAPI

## Machine Learning

- Scikit-learn
- Random Forest

## Route Optimization

- Google OR-Tools

## Data Processing

- Pandas
- NumPy

---
