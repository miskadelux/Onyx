from colorama import Fore, Style
import math
import json

def print_map_UI(map, config):
    class tile:
        def __init__(self, color, symbol):
            self.color = color
            self.symbol = symbol

    state = map

    map = [[tile(Fore.BLACK, 'O') for i in range(config['dimX'])] for j in range(config['dimY'])]

    for node in state['nodes']:
        if len(node['customers']) > 0:
            map[node['posX']][node['posY']].symbol = str(len(node['customers']))
            map[node['posX']][node['posY']].color = Fore.GREEN
        else:
            map[node['posX']][node['posY']].symbol = '0'
            map[node['posX']][node['posY']].color = Fore.RED

        if node['target']['Type'] == 'ChargingStation':
            map[node['posX']][node['posY']].color = Fore.YELLOW

    for y in range(len(map)):
        for x in range(len(map[y])):
            print(map[x][y].color, map[x][y].symbol, end="    ")
            print(Style.RESET_ALL, end="")

        print()
        print()

def get_all_customers(map):
    customer_speeds = load_speed()
    customers = []

    for node in map['nodes']:
        if len(node['customers']) > 0:
            for customer in node['customers']:
                if customer['id'] in customer_speeds.keys(): ### Det var någon patch en förare med en viss id spawnade in ifall man skickade rekomendation men sedan försvann. Tror det var en bugg. Detta löser buggen tills de hittar buggen!
                    customer['inNode'] = node['id']
                    customer['speed'] = customer_speeds[customer['id']]
                    customers.append(customer)
                
    for edge in map['edges']:
        if len(edge['customers']) > 0:
            for customer in edge['customers']:
                if customer['id'] in customer_speeds.keys():### Det var någon patch en förare med en viss id spawnade in ifall man skickade rekomendation men sedan försvann. Tror det var en bugg. Detta löser buggen tills de hittar buggen!
                    customer['inNode'] = node['id']
                    customer['speed'] = customer_speeds[customer['id']]
                    customers.append(customer)
    return customers

def get_all_customers_without_speed(map):
    customers = []

    for node in map['nodes']:
        if len(node['customers']) > 0:
            for customer in node['customers']:
                customer['inNode'] = node['id']
                customers.append(customer)
                
    for edge in map['edges']:
        if len(edge['customers']) > 0:
            for customer in edge['customers']:
                customer['inNode'] = edge['toNode']
                customers.append(customer)
    return customers

def find_customer(id: str, customers: list):
    for customer in customers:
        if customer['id'] == id:
            return customer

def get_all_stations(map):
    stations = []

    for node in map['nodes']:
        if node['target']['Type'] == 'ChargingStation':
            node['target']['inNode'] = node['id']
            node['target']['bookings'] = {}
            node['target']['posX'] = node['posX']
            node['target']['posY'] = node['posY']

            for zone in map['zones']:
                if node['target']['posX'] <= zone['bottomRightX'] and node['target']['posX'] >= zone['topLeftX'] and node['target']['posY'] <= zone['bottomRightY'] and node['target']['posY'] >= zone['topLeftY']:
                    node['target']['zoneId'] = zone['id']

            stations.append(node['target'])
    return stations

def find_station(id: str, stations):
    for station in stations:
        if station['inNode'] == id:
            return station
    
def calculate_max_length(customer):
    charge = customer['chargeRemaining'] * customer['maxCharge']
    consumption = customer['energyConsumptionPerKm']
    return charge / consumption
    
def create_graph(map):
    graph = {}
    map = map.copy()
    for node in map['nodes']:
        graph[node['id']] = []
        for edge in map['edges']:
            if edge['fromNode'] == node['id']:
                graph[node['id']].append((edge['toNode'], edge['length']))

    return graph

def shortest_length(start_node: str, graph, end_node=None, max_length=float('inf')) -> float|dict:
    visited = []
    dist = {start_node:{'length': 0, 'numNodesTo':0}}

    pq = [(0, start_node)]
    while end_node not in visited and len(pq) > 0:
        weight, node = pq.pop(0)
        visited.append(node)

        for edge in graph[node]:
            if edge[1] + weight < max_length * 1: ### might want to add some legroom in case the drivers don't find the optimal route
                if edge[0] not in dist.keys():
                    dist[edge[0]] = {'length': edge[1] + dist[node]['length'], 'numNodesTo': 1 + dist[node]['numNodesTo']}
                elif dist[edge[0]]['length'] > edge[1] + dist[node]['length']:
                    dist[edge[0]] = {'length': edge[1] + dist[node]['length'], 'numNodesTo': 1 + dist[node]['numNodesTo']}
                    
                in_pq = False
                for i in pq:
                    if i[1] == edge[0]:
                        in_pq = True

                if edge[0] not in visited and not in_pq:
                    pq.append((edge[1] + weight, edge[0]))

        pq.sort()

    if end_node != None and end_node in dist.keys():
        return dist[end_node]
    elif end_node != None:
        return None
    else:
        return dist
    
def find_avalible_stations(customer, graph, stations, zones, zones_log):
    reachable_stations = {}
    length = calculate_max_length(customer)
    avalible_nodes = shortest_length(customer['inNode'], graph, max_length=length)

    for station in stations:
        if station['inNode'] in avalible_nodes.keys():
            reachable_stations[station['inNode']] = station
            reachable_stations[station['inNode']]['length'] = avalible_nodes[station['inNode']]['length']
            reachable_stations[station['inNode']]['numNodesTo'] = avalible_nodes[station['inNode']]['numNodesTo']

    rem = []
    for node in reachable_stations: 

        ticks_charging = charging_ticks(customer['maxCharge'], customer['energyConsumptionPerKm'], reachable_stations[node], length) #How long it will charge
        reach_in_ticks = math.ceil(reachable_stations[node]['length'] / customer['speed']) + (3 * (reachable_stations[node]['numNodesTo']- 1) + 2) #Amount of ticks, mostly accurate, I think might differ sometimes by -1 +2 max (from experiment) I think because some edges are weird

        customer['ticksToCharge'] = ticks_charging
        customer['ticksToReach'] = reach_in_ticks

        #What happens if they become full? - bug
        if reach_in_ticks + customer['departureTick'] in reachable_stations[node]['bookings'].keys() and reachable_stations[node]['bookings'][reach_in_ticks + customer['departureTick']] == station['totalAmountOfChargers'] - station['totalAmountOfBrokenChargers']: # removes if bookings of chargers are full on arrival
            rem.append(node)

        #What happens if they become full? - bug
        for zone in zones:
            if reachable_stations[node]['zoneId'] == zone['id'] and reach_in_ticks + customer['departureTick'] in zone['bookings'].keys():
                for zone_ in zones_log[reach_in_ticks  + customer['departureTick']]['zones']:
                    if zone_['zoneId'] == reachable_stations[node]['zoneId'] and zone['bookings'][reach_in_ticks + customer['departureTick']] + reachable_stations[node]['chargeSpeedPerCharger'] > zone_['totalProduction'] and node not in rem: # removes if bookings of totalDemand are full on arrival
                        rem.append(node)
                break


        if shortest_length(node, graph, customer['toNode'], customer['maxCharge'] / customer['energyConsumptionPerKm']) == None and node not in rem:# Removes if endpoint not reachable from station
            rem.append(node)

    for node in rem:
        del reachable_stations[node]

    return reachable_stations

def charging_ticks(customer_max_charge, customer_energy_consumption, station_info, length) -> int:
    length_left = length - station_info['length']
    charge_at_station = length_left * customer_energy_consumption
    charge_needed =  customer_max_charge - charge_at_station  #assuming you want filled
    ticks_charging = math.ceil(charge_needed / ((station_info['chargeSpeedPerCharger'] / 60) * 5)) # might be better to // and + 1
    
    return ticks_charging

def get_all_zones(zone_log, zones): # Uppdaterar stations med produktion av el info

    zones_log = zone_log['zones']
    zone_log = {}
    for zone in zones_log:
        zone_log[zone['zoneId']] = [zone['totalProduction'], zone['totalDemand']]

    for zone in zones:
        zone['totalProduction'] = zone_log[zone['id']][0]
        zone['totalDemand'] = zone_log[zone['id']][1]
        if 'bookings' not in zone.keys():
            zone['bookings'] = {}

    return zones

def check_for_juice(customers) -> dict:
    ran_out = {}
    for customer in customers:
        if customer['state'] == 'RanOutOfJuice':
            ran_out[customer['id']] = customer['inNode']
    return ran_out

def load_speed() -> dict:
    with open('data/speeds.txt', 'r') as f:
        customer_speeds = json.load(f)
    return customer_speeds

def load_total_production() -> dict:
    with open('data/totalProduction.txt', 'r') as f:
        total_production = json.load(f)
    return total_production

def load_ticks():
    with open('data/ticks.txt', 'r') as f:
        ticks = json.load(f)
    return ticks

def save_ticks(ticks):
    with open('data/ticks.txt', 'w') as f:
        json.dump(ticks, f)

def make_choice(reachable_stations, customer, graph):
    if len(reachable_stations) == 0:
        raise ValueError('NoAvalibleStation', customer, reachable_stations)

    chosen_station = reachable_stations[tuple(reachable_stations.keys())[0]]
    #print('starting:',chosen_station)
    #print('customer:',customer)
    
    for station in reachable_stations: # Kortaste sträckan till endpoint
        if reachable_stations[station]['length'] + shortest_length(reachable_stations[station]['inNode'], graph, customer['toNode'], customer['maxCharge'] / customer['energyConsumptionPerKm'])['length'] < chosen_station['length'] + shortest_length(chosen_station['inNode'], graph, customer['toNode'], customer['maxCharge'] / customer['energyConsumptionPerKm'])['length']:
            chosen_station = reachable_stations[station]
    
    #persona

    return chosen_station



def create_recommendation(station_id, customer_id, charge_to):
    return  {
            "customerId": customer_id,
            "chargingRecommendations": [
                {
                    "nodeId": station_id,
                    "chargeTo": charge_to
                }
            ]
            }
        
def find_dumb_stations(customer, graph, stations, zones, zones_log):
    reachable_stations = {}
    length = calculate_max_length(customer)
    avalible_nodes = shortest_length(customer['inNode'], graph, max_length=length)

    for station in stations:
        if station['inNode'] in avalible_nodes.keys():
            reachable_stations[station['inNode']] = station
            reachable_stations[station['inNode']]['length'] = avalible_nodes[station['inNode']]['length']
            reachable_stations[station['inNode']]['numNodesTo'] = avalible_nodes[station['inNode']]['numNodesTo']
            return reachable_stations

    return None
    

