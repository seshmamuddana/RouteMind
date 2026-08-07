import json

# Load files
with open("small_dataset/route_data.json") as f:
    routes = json.load(f)

with open("small_dataset/package_data.json") as f:
    packages = json.load(f)

with open("small_dataset/travel_times.json") as f:
    travel = json.load(f)

with open("small_dataset/actual_sequences.json") as f:
    actual = json.load(f)

print("Number of routes:", len(routes))

# Take first route
route_id = list(routes.keys())[0]

print("\nRoute ID:", route_id)

print("\nRoute Information")
print(routes[route_id])

print("\nPackages:", len(packages[route_id]))

print("\nStops in travel matrix:", len(travel[route_id]))

print("\nActual delivery sequence:")
print(actual[route_id])