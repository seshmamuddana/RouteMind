#  RouteMind
### Adaptive Route Optimization for the Supply Chain
 AI-powered route optimization and dynamic route replanning system for first-mile, middle-mile, and last-mile logistics.

---

## 📌 Problem Statement

Traditional delivery routes are planned before vehicles leave the hub and rarely change during execution. When unexpected events such as traffic congestion, new pickup requests, or failed deliveries occur, delivery partners continue following outdated routes, leading to:

- Increased delivery delays
- Higher fuel consumption
- Reduced vehicle utilization
- Poor customer experience

RouteMind addresses these challenges by combining Machine Learning with Route Optimization to generate efficient routes and support intelligent route replanning.

---

# 🎯 Objectives

- Optimize delivery routes
- Reduce travel distance and delivery time
- Improve route quality prediction
- Support real-time route replanning
- Compare optimized routes against baseline routes

---

# 📂 Dataset

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
| actual_sequences.json | Actual delivery order |

---

# 🔄 Project Workflow

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

# 🏗 System Architecture

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
        (Random Forest Classifier)
                       │
                       ▼
          Route Optimization Engine
             (Google OR-Tools)
                       │
                       ▼
       Constraint Validation Module
                       │
                       ▼
        Dynamic Route Replanning
                       │
                       ▼
          AI Decision Explanation
```

---

# 🚀 Step 1 : Data Collection

Collected the Amazon Last Mile Routing Research Challenge Dataset.

### Files Used

- route_data.json
- package_data.json
- travel_times.json
- actual_sequences.json

---

# 🔍 Step 2 : Data Exploration

Explored the raw dataset to understand its structure and identify the important attributes required for optimization.

### Features Identified

- Route ID
- Station
- Vehicle Capacity
- Route Score
- Stop ID
- Latitude
- Longitude
- Stop Type
- Zone ID
- Actual Delivery Sequence

---

# 🧹 Step 3 : Data Preprocessing

The raw JSON files were transformed into a structured dataset.

### Tasks Performed

- Loaded all routing datasets
- Extracted route information
- Extracted stop information
- Mapped actual delivery sequence
- Combined data into a Pandas DataFrame
- Sorted routes using delivery sequence
- Generated **processed_dataset.csv**

---

# ⚙ Step 4 : Feature Engineering

Generated meaningful features to improve machine learning performance.

### Tasks Performed

- Generated time-based features
- Calculated distance between consecutive stops
- Created route-level statistics
- Derived optimization metrics
- Encoded categorical attributes
- Generated **route_features.csv**

---

# 🤖 Step 5 : Model Training

A Random Forest Classifier was trained to predict route quality.

### Tasks Performed

- Loaded feature-engineered dataset
- Encoded Route Score
- Selected important features
- Split dataset into Train/Test sets
- Trained Random Forest model
- Evaluated model performance
- Saved trained model

### Model Used

- Random Forest Classifier

### Generated Files

- route_model.pkl
- label_encoder.pkl

---

# 🗺 Step 6 : Route Optimization 

Google OR-Tools will be used to generate optimized delivery routes by minimizing:

- Total Distance
- Travel Time
- Vehicle Utilization

---

# 📋 Step 7 : Constraint Validation

The optimizer will validate routes using operational constraints such as:

- Delivery Time Windows
- Vehicle Capacity
- Driver Working Hours
- COD Cash Limits

---

# 🔄 Step 8 : Dynamic Route Replanning

When disruptions occur, the system will generate an updated route.

Example events:

- New Pickup
- Failed Delivery
- Traffic Congestion
- Road Closure

---

# 💡 Step 9 : AI Explanation

The system explains every route modification by highlighting:

- Reason for change
- Distance difference
- Time difference
- Constraint satisfied
- Expected business impact

---

# 📊 Tech Stack

## Frontend

- React
- Tailwind CSS
- Recharts

## Backend

- Python
- FastAPI

## Machine Learning

- Scikit-learn
- Random Forest

## Optimization

- Google OR-Tools

## Data Processing

- Pandas
- NumPy

---
