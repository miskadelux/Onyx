import sys
from client import ConsiditionClient
from own_logic import print_map_UI, get_all_customers, get_all_stations, create_graph, find_customer, find_avalible_stations, get_all_zones, find_station, make_choice, create_recommendation, load_total_production, find_dumb_stations

def generate_customer_recommendations(map_obj, current_tick):
    return [
            # {
            #   "customerId": '0.24',
            #   "chargingRecommendations": [
            #     {
            #       "nodeId": '5.7', # 7.13
            #       "chargeTo": 1
            #     }
            #   ]
            # }
          ]

def generate_customer_recommendationsa(map_obj, current_tick):
    return [
            # {
            #   "customerId": "0.131",
            #   "chargingRecommendations": [
            #     {
            #       "nodeId": '2.4', # 7.13
            #       "chargeTo": 1
            #     }
            #   ]
            # }
          ]

def generate_tick(map_obj, current_tick):
    return {
        "tick": current_tick,
        "customerRecommendations": generate_customer_recommendations(map_obj, current_tick),
    }
def generate_ticka(map_obj, current_tick):
    return {
        "tick": current_tick,
        "customerRecommendations": generate_customer_recommendationsa(map_obj, current_tick),
    }

def main():
    api_key = "1546ce68-d586-461a-9534-add93e4daacf"
    base_url = "http://localhost:8080/api" #"https://api.considition.com/api"
    map_name = "Thunderroad"



    zone_logs = load_total_production()
    client = ConsiditionClient(base_url, api_key)

    # config = client.get_config(map_name)
    # input(config)
    map_obj = client.get_map(map_name)
    zones = get_all_zones(zone_logs[1], map_obj['zones'])

    if not map_obj:
        print("Failed to fetch map!")
        sys.exit(1)

    toTick = 4
    input_payload = {
        "mapName": map_name,
        "ticks": [generate_tick(map_obj, 0), generate_ticka(map_obj, 85)],
        "playToTick":  toTick
    }

    config = client.get_config(map_name)
    game_response = client.post_game(input_payload)
    end_state_map = game_response.get("map")
    stations = get_all_stations(end_state_map)
    s_customers = get_all_customers(map_obj)
    e_customers = get_all_customers(end_state_map)
    cmrs_nearby_stations = []
    #print(s_customers)

    graph = create_graph(map_obj) 

    final_score = (
        + game_response.get("score", 0)
    )

    cmr = find_customer('0.24', e_customers)
    l = find_dumb_stations(cmr, graph, stations, zones, zone_logs)
    #choice = make_choice(l)
    # # rec = create_recommendation(choice['inNode'], cmr['id'], 1)
    # print(rec)
    #print_map_UI(end_state_map)


    print_map_UI(end_state_map, config)

    print(cmr['state'], cmr['inNode'], cmr['toNode'], cmr['departureTick'], 'maxCharge: ', cmr['maxCharge'], 'chargeRemaining: ', cmr['chargeRemaining'])

    print(l)

    # for i in l:
    #     print(i)


  #0.131
  #0.24 #
  #0.157
  #0.90
  #0.15



    #print(stations)



    print(final_score)

if __name__ == "__main__":
    main()