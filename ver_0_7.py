from client import ConsiditionClient
from own_logic import get_all_customers, get_all_stations, create_graph, find_avalible_stations, get_all_zones, create_recommendation, load_total_production, save_ticks, check_for_juice, find_dumb_stations, customer_book, find_possible_multi_station, make_choicev6

def should_move_on_to_next_tick(response):
    return True

def generate_customer_recommendations(end_map, customers_with_direct_rec,  customers_with_multi_rec, bad_customers, graph, stations, zones, zone_logs):
    customers = get_all_customers(end_map)
    recommendations = []

    for customer in customers:
        if customer['id'] in customers_with_multi_rec and customer['state'] == 'Charging':
            customers_with_multi_rec.remove(customer['id'])




        if customer['id'] not in customers_with_direct_rec and customer['id'] not in customers_with_multi_rec and customer['id'] not in bad_customers:
            reachable_stations = find_avalible_stations(customer, graph, stations, zones, zone_logs)
            multi_reachable_stations = find_possible_multi_station(customer, graph, stations, zones, zone_logs) # does not check bookings right now, the bookings need to be made different because I am adding the departure tick plus arrival tick, but arrival tick needs to be extended every time it finds a new station

            if len(reachable_stations) != 0:
                stations_choice = make_choicev6(reachable_stations, customer, graph)
                customer_book(customer, zones, stations_choice)

                recommendations.append(create_recommendation(stations_choice['inNode'], customer['id'], 1))
                customers_with_direct_rec.append(customer['id'])

            elif len(multi_reachable_stations) != 0:
                #print(customer['id'], 'did not find an good avalible station')
                
                stations_choice = make_choicev6(multi_reachable_stations, customer, graph) ### need to make a smarter choice for multi

                customer_book(customer, zones, stations_choice)

                recommendations.append(create_recommendation(stations_choice['inNode'], customer['id'], 1))
                customers_with_multi_rec.append(customer['id'])

            else:
                #print(customer['id'], 'did not find an good avalible station at all')
                bad_customers.append(customer['id'])


    return recommendations

def generate_tick(current_tick, end_map, customers_with_direct_rec,  customers_with_multi_rec, bad_customers, graph, stations, zones, zone_logs):
    return {
        "tick": current_tick,
        "customerRecommendations": generate_customer_recommendations(end_map, customers_with_direct_rec,  customers_with_multi_rec, bad_customers, graph, stations, zones, zone_logs),
    }

def main():
    api_key = "1546ce68-d586-461a-9534-add93e4daacf"
    base_url = "http://localhost:8080/api"
    map_name = "Thunderroad"

    zone_logs = load_total_production()
    client = ConsiditionClient(base_url, api_key)
    config = client.get_config(map_name)
    start_map = client.get_map(map_name)
    stations = get_all_stations(start_map)
    zones = get_all_zones(zone_logs[1], start_map['zones'])
    graph = create_graph(start_map) 
    customers_with_direct_rec = []
    customers_with_multi_rec = []
    bad_customers = []


    final_score = None
    good_ticks = []

    current_tick = generate_tick(0, start_map, customers_with_direct_rec, customers_with_multi_rec, bad_customers, graph, stations, zones, zone_logs)
    input_payload = {
        "mapName": map_name,
        "ticks": [current_tick],
    }

    total_ticks = int(start_map.get("ticks", 0))

    for i in range(total_ticks):
        print('tick:', i)
        while True:
            game_response = client.post_game(input_payload)

            # Sum the scores directly (assuming they are numbers)
            final_score = ('Total: ' + str(game_response.get("score", 0)), 'Sold: ' + str(game_response.get("kwhRevenue", 0)), 'Happy: ' + str(game_response.get("customerCompletionScore", 0)))

            if should_move_on_to_next_tick(game_response):
                good_ticks.append(current_tick)
                updated_map = game_response.get("map")

                current_tick = generate_tick(i + 1, updated_map, customers_with_direct_rec, customers_with_multi_rec, bad_customers, graph, stations, zones, zone_logs)
                input_payload = {
                    "mapName": map_name,
                    "playToTick": i + 1,
                    "ticks": [*good_ticks, current_tick],
                }
                break

            updated_map = game_response.get("map")
            current_tick = generate_tick(i, updated_map, customers_with_direct_rec, customers_with_multi_rec, bad_customers, graph, stations, zones, zone_logs)
            input_payload = {
                "mapName": map_name,
                "playToTick": i,
                "ticks": [*good_ticks, current_tick],
            }



    print(len(bad_customers), ': had to go nowhere (bad)')
    print(len(customers_with_multi_rec), ': had to go farther (multi)')
    print(len(customers_with_direct_rec), ': had to go closer (direct)') # They all end up here at the end

    c = get_all_customers(updated_map)
    k = check_for_juice(c)
    print(len(k), 'ran out of juice')

    save_ticks(input_payload["ticks"])

    print(f"Final score: {final_score}")

if __name__ == "__main__":
    main()