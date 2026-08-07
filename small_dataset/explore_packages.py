import json

with open("small_dataset/package_data.json") as f:
    packages = json.load(f)

first_route = next(iter(packages))

print(first_route)

print(packages[first_route])