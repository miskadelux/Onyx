import json

def explore(obj, indent=0):
    """Recursively print the structure of a JSON object"""
    prefix = "  " * indent
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                print(f"{prefix}{k}: ({type(v).__name__}, len={len(v) if hasattr(v, '__len__') else 'n/a'})")
                explore(v, indent + 1)
            else:
                print(f"{prefix}{k}: {v}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:3]):  # only show first 3 items
            print(f"{prefix}[{i}] ({type(v).__name__})")
            explore(v, indent + 1)
        if len(obj) > 3:
            print(f"{prefix}... ({len(obj)} total items)")
    else:
        print(f"{prefix}{obj}")

# Load the JSON
with open("turbohill.json", "r") as f:
    data = json.load(f)

# Print top-level info
print(f"\nTop-level keys: {list(data.keys())}\n")

# Explore full structure
explore(data)


for node in data["nodes"]:
    for c in node["customers"]:
        print(f"Customers {c['id']} from {c['fromNode']} to {c['toNode']} ({c['persona']}) departs at tick {c['departureTick']}")



for e in data["edges"][:10]:
    print(f"{e["fromNode"]} -- {e["toNode"]} (length {e["length"]:.2f})")
