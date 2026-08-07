import json

with open("small_dataset/travel_times.json") as f:
    travel = json.load(f)

first_route = next(iter(travel))

print("Route ID:")
print(first_route)

print("\nTravel Times:")

route = travel[first_route]

print(route)