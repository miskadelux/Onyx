import sys
from client import ConsiditionClient
from own_logic import get_all_customers, get_all_stations, create_graph, find_avalible_stations, get_all_zones, make_choice, create_recommendation, load_total_production, save_ticks

def generate_customer_recommendations(end_map, customers_with_recommendation, graph, stations, zones, zone_logs):
    customers = get_all_customers(end_map)
    recommendations = []

    for customer in customers:
        if customer['id'] not in customers_with_recommendation:
            reachable_stations = find_avalible_stations(customer, graph, stations, zones, zone_logs)
            customer['reachableStations'] = reachable_stations

    customerWithLeast = customers[0]

    for customer in customers:
        if len(customerWithLeast['reachableStations']) > len(customer['reachableStations']):
            customerWithLeast = customer
    
    
    for c in customers:
        print(c)
    print(customerWithLeast)




            # if len(reachable_stations) != 0:
            #     stations_choice = make_choice(reachable_stations, customer, graph)
            #     recommendations.append(create_recommendation(stations_choice['inNode'], customer['id'], 1))
            #     customers_with_recommendation.append(customer['id'])
            # else:
            #     print(customer['id'], 'did not find an avalible station') # 0.73


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



    if not start_map:
        print("Failed to fetch map!")
        sys.exit(1)

    # Updating every tick
    #toTick = 288 ###Test
    ticks = generate_tick(1, start_map, customers_with_recommendation, graph, stations, zones, zone_logs)
    input_payload = {
        "mapName": map_name,
        "ticks": [ticks], # end_map is start_map in test case, will change!
        #"playToTick":  toTick
    }
    # 9760 highscore
    game_response = client.post_game(input_payload)
    end_map = game_response.get("map", 0)
    









    #save_ticks(ticks)



    # Prioritera personer med minst val
    # koppla bookningsystemet
    # gör så att nya customers också får en rekkomendation, sker inte just nu då jag bar ger recomendationer till folk på tick 1
    # optimera valet
    # Ta med folk som inte klarar det från första charging station, (de kan charga två gånger)




    final_score = (
        + game_response.get("score", 0)
    )


    print('Final score:', final_score)

if __name__ == "__main__":
    main()