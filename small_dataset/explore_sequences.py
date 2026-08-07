import json

with open("small_dataset/actual_sequences.json", "r") as f:
    sequences = json.load(f)

first_route = next(iter(sequences))

print("Route ID:", first_route)
print()
print(sequences[first_route])