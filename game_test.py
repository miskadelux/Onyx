import sys
import time
from client import ConsiditionClient
from own_logic import print_map_UI, get_all_customers

def generate_customer_recommendations(map_obj, current_tick):
    return [
            {
              "customerId": "0.9",
              "chargingRecommendations": [
                {
                  "nodeId": "7.6",
                  "chargeTo": 0.786
                }
              ]
            }
          ]

def generate_tick(map_obj, current_tick):
    return {
        "tick": current_tick,
        "customerRecommendations": generate_customer_recommendations(map_obj, current_tick),
    }

def main():
    api_key = "1546ce68-d586-461a-9534-add93e4daacf"
    base_url = "http://localhost:8080/api" #"https://api.considition.com/api"
    map_name = "Turbohill"

    client = ConsiditionClient(base_url, api_key)
    map_obj = client.get_map(map_name)

    if not map_obj:
        print("Failed to fetch map!")
        sys.exit(1)

    current_tick = generate_tick(map_obj, 0)

    input_payload = {
        "mapName": map_name,
        "ticks": [current_tick],
        "playToTick": 4
    }

    game_response = client.post_game(input_payload)

    final_score = (
        game_response.get("customerCompletionScore", 0)
        + game_response.get("kwhRevenue", 0)
        + game_response.get("score", 0)
    )

    print(f"Final score: {final_score}")


    end_state_map = game_response.get("map")
    
    customers = get_all_customers(end_state_map)
    print(customers)
    print(len(customers))
    print_map_UI(end_state_map)

if __name__ == "__main__":
    main()