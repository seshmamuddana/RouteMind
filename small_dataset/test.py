import json

with open("small_dataset/route_data.json", "r") as f:
    data = json.load(f)

print("Routes:", len(data))