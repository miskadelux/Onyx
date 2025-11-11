import sys
import time
from client import ConsiditionClient
from own_logic import get_all_customers, get_all_stations, create_graph, find_avalible_stations, get_all_zones, make_choice, create_recommendation, load_total_production, save_ticks, check_for_juice

def should_move_on_to_next_tick(response):
    return True

def generate_customer_recommendations(end_map, customers_with_recommendation, graph, stations, zones, zone_logs):
    customers = get_all_customers(end_map)
    recommendations = []
    i = 0

    for customer in customers:
        
        if customer['id'] not in customers_with_recommendation:
            reachable_stations = find_avalible_stations(customer, graph, stations, zones, zone_logs)

            if len(reachable_stations) != 0:
                stations_choice = make_choice(reachable_stations, customer, graph)
                for zone in zones:
                    if zone['id'] == stations_choice['zoneId']:
                        break

                for i in range(customer['ticksToCharge']):
                    if customer['ticksToReach'] + customer['departureTick'] + i not in stations_choice['bookings'].keys():
                        zone['bookings'][customer['ticksToReach'] + customer['departureTick'] + i] = 1
                        stations_choice['bookings'][customer['ticksToReach'] + customer['departureTick'] + i] = 1
                    else:
                        stations_choice['bookings'][customer['ticksToReach'] + customer['departureTick'] + i] += 1
                        zone['bookings'][customer['ticksToReach'] + customer['departureTick'] + i] += 1

                recommendations.append(create_recommendation(stations_choice['inNode'], customer['id'], 1))
                customers_with_recommendation.append(customer['id'])
            else:
                print(customer['id'], 'did not find an avalible station') # 0.73
                i += 1
    print(i, ' didnt find a station')
    return recommendations

def generate_tick(current_tick, end_map, customers_with_recommendation, graph, stations, zones, zone_logs):
    return {
        "tick": current_tick,
        "customerRecommendations": generate_customer_recommendations(end_map, customers_with_recommendation, graph, stations, zones, zone_logs),
    }

def main():
    api_key = "1546ce68-d586-461a-9534-add93e4daacf"
    base_url = "http://localhost:8080/api"
    map_name = "Clutchfield"

    zone_logs = load_total_production()
    client = ConsiditionClient(base_url, api_key)
    config = client.get_config(map_name)
    start_map = client.get_map(map_name)
    stations = get_all_stations(start_map)
    zones = get_all_zones(zone_logs[1], start_map['zones'])
    graph = create_graph(start_map) 
    customers_with_recommendation = []


    final_score = 0
    good_ticks = []

    current_tick = generate_tick(0, start_map, customers_with_recommendation, graph, stations, zones, zone_logs)
    input_payload = {
        "mapName": map_name,
        "ticks": [current_tick],
    }

    total_ticks = int(start_map.get("ticks", 0))

    for i in range(total_ticks):
        while True:
            game_response = client.post_game(input_payload)

            # Sum the scores directly (assuming they are numbers)
            final_score = game_response.get("score", 0)

            if should_move_on_to_next_tick(game_response):
                good_ticks.append(current_tick)
                updated_map = game_response.get("map")

                current_tick = generate_tick(i + 1, updated_map, customers_with_recommendation, graph, stations, zones, zone_logs)
                input_payload = {
                    "mapName": map_name,
                    "playToTick": i + 1,
                    "ticks": [*good_ticks, current_tick],
                }
                break

            updated_map = game_response.get("map")
            current_tick = generate_tick(i, updated_map, customers_with_recommendation, graph, stations, zones, zone_logs)
            input_payload = {
                "mapName": map_name,
                "playToTick": i,
                "ticks": [*good_ticks, current_tick],
            }
    
    # Prioritera personer med minst val när jag implementerat bookningsystemet
    # se om folk kan hitta flera chargingstations de kan nå för att nå slutdestination
    # optimera valet


    c = get_all_customers(updated_map)
    k = check_for_juice(c)
    print(len(k), 'ran out of juice')

    #save_ticks(input_payload["ticks"]) ###9169

    print(f"Final score: {final_score}")

if __name__ == "__main__":
    main()