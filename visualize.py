import json
import matplotlib.pyplot as plt

with open("onyx/turbohill.json") as f:
    data = json.data(f)


nodes = data["nodes"]
x_nodes = [n["posX"] for n in nodes]
y_nodes = [n["posY"] for n in nodes]


plt.scatter(x_nodes, y_nodes, s=20, color="red", label="nodes")

x_customers = []
y_customers = []

labels = []


for n in nodes:
    for c in n.get("customers", []):
        x_customers.append(n["posX"])
        y_customers.append(n["posY"])
        labels.append(c["persona"])



plt.scatter(x_customers, y_customers, s=100, color="red", label="Customers")

# Annotate customer persona
for i, txt in enumerate(labels):
    plt.annotate(txt, (x_customers[i]+0.1, y_customers[i]+0.1), fontsize=8)

# Plot charging stations
x_stations = []
y_stations = []

for zone in data.get("zones", []):
    # approximate charging station positions as corners of zone
    x_stations.append(zone["topLeftX"])
    y_stations.append(zone["topLeftY"])
    x_stations.append(zone["bottomRightX"])
    y_stations.append(zone["bottomRightY"])

plt.scatter(x_stations, y_stations, s=150, color="blue", marker="s", label="Charging Stations (zone corners)")

# Labels and legend
plt.title("Turbohill Map Overview")
plt.xlabel("X")
plt.ylabel("Y")
plt.legend()
plt.grid(True)
plt.show()