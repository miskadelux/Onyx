import sys
import time
from client import ConsiditionClient
from own_logic import print_map_UI, get_all_customers, get_all_stations, create_graph, shortest_lenght, calculate_max_lenght, find_customer

def generate_customer_recommendations(map_obj, current_tick):
    return [
            {
              "customerId": "0.19", #0.9
              "chargingRecommendations": [
                {
                  "nodeId": "2.4", #7.6
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

    input_payload = {
        "mapName": map_name,
        "ticks": [generate_tick(map_obj, 0)],
        "playToTick": 50
    }

    game_response = client.post_game(input_payload)
    end_state_map = game_response.get("map")
    s_customers = get_all_customers(map_obj)
    e_customers = get_all_customers(end_state_map)
    graph = create_graph(map_obj)

    final_score = (
        game_response.get("customerCompletionScore", 0)
        + game_response.get("kwhRevenue", 0)
        + game_response.get("score", 0)
    )


    
    cmr = find_customer('0.19', s_customers)
    lenght = calculate_max_lenght(cmr)
    k = shortest_lenght('0.0', graph, max_lenght=lenght)

    e_cmr = find_customer('0.19', e_customers)
    

    print_map_UI(end_state_map)
    print(k)
    print(e_cmr['state'], e_cmr['inNode'])
            

    

if __name__ == "__main__":
    main()