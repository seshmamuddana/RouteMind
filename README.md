Track 3: RouteMind
Adaptive Route Optimization for the Supply Chain 

Project Overview

RouteMind is an AI-powered route optimization system designed to improve first-mile, middle-mile, and last-mile logistics. The project utilizes the Amazon Last Mile Routing Research Challenge Dataset to analyze delivery routes, preprocess logistics data, and prepare it for intelligent route optimization and real-time replanning.

Step-1 :  Data Collection
Amazon Last Mile Routing Research Challenge (2021)
The project uses Amazon's real-world delivery dataset containing historical delivery operations.
Dataset Files:
route_data.json : Route information, delivery stops, station details, vehicle capacity and route metadata
package_data.json : Package information for every delivery stop
travel_times.json : Travel time matrix between delivery locations
actual_sequences.json : Actual delivery sequence followed by drivers

Step 2 : Data Preprocessing
The raw Amazon dataset is distributed across multiple JSON files. The preprocessing stage transforms this data into a single structured dataset.
Preprocessing Steps
I. Loaded all routing datasets.
II. Extracted route information (Route ID, Station, Date, Vehicle Capacity, Route Score).
III. Extracted stop information (Stop ID, Latitude, Longitude, Stop Type, Zone ID).
IV. Mapped each stop to its actual delivery sequence.
V. Combined the extracted data into a single Pandas DataFrame.
VI. Sorted the dataset by Route ID and Actual Delivery Sequence.
VII. Exported the final dataset as processed_dataset.csv.
The processed dataset will serve as the input for the Route Optimization Engine.

Step 3 : Feature Engineering
Feature engineering was performed to transform the preprocessed dataset into a format suitable for route optimization and AI analysis.
Tasks Performed:
Generated time-based features (Departure Hour, Day of Week, Peak Hour).
Calculated distance between consecutive delivery stops through longitudes and latitudes.
Created route-level features such as Total Stops, Total Distance, Average Stop Distance, and Vehicle Capacity.
Derived optimization metrics including Dropoff Ratio, Distance per Stop, Capacity Utilization, and Stops per Kilometer.
Generated the final feature-engineered dataset.

