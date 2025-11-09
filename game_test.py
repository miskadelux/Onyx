import sys
import time
from client import ConsiditionClient
from own_logic import print_map_UI, get_all_customers, get_all_stations, create_graph, find_customer, find_avalible_stations, get_zone_production, find_station

def generate_customer_recommendations(map_obj, current_tick):
    return [
            {
              "customerId": "0.19", #0.14
              "chargingRecommendations": [
                {
                  "nodeId": "1.1", #4.1
                  "chargeTo": 1
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

    toTick = 0
    input_payload = {
        "mapName": map_name,
        "ticks": [generate_tick(map_obj, 0)],
        "playToTick":  toTick
    }

    game_response = client.post_game(input_payload)
    stations = get_all_stations(map_obj)
    end_state_map = game_response.get("map")
    zones = end_state_map['zones']
    s_customers = get_all_customers(map_obj)
    e_customers = get_all_customers(end_state_map)
    cmrs_nearby_stations = []
    zone_log = game_response.get('zoneLogs', 0)
    #print(zone_log[20])
    zones = get_zone_production(zone_log[toTick - 1], zones)
    #print(zones)

    graph = create_graph(map_obj) 

    final_score = (
        game_response.get("customerCompletionScore", 0)
        + game_response.get("kwhRevenue", 0)
        + game_response.get("score", 0)
    )

    
    cmr = find_customer('0.19', e_customers)
    l = find_avalible_stations(cmr, map_obj, graph, stations, zones)
    #print_map_UI(end_state_map)

    # length = calculate_max_lenght(cmr)
    # k = shortest_length('0.0', graph, max_length=length)
    #print(end_state_map['zones'])
    
    print_map_UI(end_state_map)
    #print(zone_kw[45]['zones'][0])
    print(cmr['state'], cmr['inNode'], cmr['toNode'], cmr['chargeRemaining'])
    print(find_station('1.1', stations)['chargeSpeedPerCharger'])
    print(l)



    #print(final_score)
            

    ### fixa så att alla i samma zone har samma referens, så om du ändrar på en, så ändras alla!

if __name__ == "__main__":
    main()