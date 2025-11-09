import sys
import json
from client import ConsiditionClient
from own_logic import get_all_customers, find_customer

def main():
    api_key = "1546ce68-d586-461a-9534-add93e4daacf"
    base_url = "http://localhost:8080/api" #"https://api.considition.com/api"
    map_name = "Turbohill"

    
    client = ConsiditionClient(base_url, api_key)
    start_map = client.get_map(map_name)
    max_ticks = 288

    if not start_map:
        print("Failed to fetch map!")
        sys.exit(1)

    delta_charge = {}

    for i in range(max_ticks):
        input_payload = {
            "mapName": map_name,
            "ticks": [],
            "playToTick":  i
        }

        game_response = client.post_game(input_payload)
        end_map = game_response.get("map")
        e_customers = get_all_customers(end_map)
        for customer in e_customers:
            if customer['state'] == 'Traveling':
                if not customer['id'] in delta_charge.keys():
                    delta_charge[customer['id']] = [customer['chargeRemaining'] * customer['maxCharge']]
                elif len(delta_charge[customer['id']]) < 3:
                    delta_charge[customer['id']].append(customer['chargeRemaining'] * customer['maxCharge'])
            elif customer['state'] == 'TransitioningToNode' and len(delta_charge[customer['id']]) < 3:
                delta_charge[customer['id']] == []

    customer_speeds = {}
    for customer in delta_charge:
        customer_speeds[customer] = (delta_charge[customer][0] - delta_charge[customer][1]) / find_customer(customer, e_customers)['energyConsumptionPerKm']

    with open('data/speeds.txt', 'w') as f:
        json.dump(customer_speeds, f)

if __name__ == "__main__":
    main()