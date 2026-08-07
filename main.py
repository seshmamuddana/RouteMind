import json

# Load the route data file
with open('small_dataset/route_data.json') as f:
    route_data = json.load(f)

# See how many routes are in the file
print("Number of routes:", len(route_data))

# Look at the first route's ID and its details
first_route_id = list(route_data.keys())[0]
print("\nFirst route ID:", first_route_id)
print("\nWhat's inside it:")
print(json.dumps(route_data[first_route_id], indent=2)[:1000])  # just first 1000 characters so it's not overwhelming