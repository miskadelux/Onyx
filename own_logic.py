from colorama import Fore, Style
import math
import json

def print_map_UI(map):
    class tile:
        def __init__(self, color, symbol):
            self.color = color
            self.symbol = symbol

    state = map

    map = [[tile(Fore.BLACK, 'O') for i in range(10)] for j in range(10)]

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
                customer['inNode'] = node['id']
                customer['speed'] = customer_speeds[customer['id']]
                customers.append(customer)
                
    for edge in map['edges']:
        if len(edge['customers']) > 0:
            for customer in edge['customers']:
                customer['inNode'] = edge['toNode']
                customer['speed'] = customer_speeds[customer['id']]
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
    
def calculate_max_lenght(customer):
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
    dist = {start_node:0}

    pq = [(0, start_node)]
    while end_node not in visited and len(pq) > 0:
        weight, node = pq.pop(0)
        visited.append(node)

        for edge in graph[node]:
            if edge[1] + weight < max_length * 1: ### might want to add some legroom in case the drivers don't find the optimal route
                if edge[0] not in dist.keys():
                    dist[edge[0]] = edge[1] + dist[node]
                elif dist[edge[0]] > edge[1] + dist[node]:
                    dist[edge[0]] = edge[1] + dist[node]
                    
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
    
def find_avalible_stations(customer, map, graph, stations, zones):
    speed = {'Car': 4, 'Truck': 2.3} #Tested and got: car travel speed = 4km/tick, truck speed avg = 2.6km / tick, might change ####### Not working properly
    reachable_stations = {}
    length = calculate_max_lenght(customer)
    avalible_nodes = shortest_length(customer['inNode'], graph, max_length=length)

    for station in stations:
        if station['inNode'] in avalible_nodes.keys():
            reachable_stations[station['inNode']] = station
            reachable_stations[station['inNode']]['lenght'] = avalible_nodes[station['inNode']]

    rem = []
    for node in reachable_stations: 
        end_point_length = shortest_length(node, graph, end_node=customer['toNode'])

        ticks_charging = charging_ticks(customer['maxCharge'], customer['energyConsumptionPerKm'], reachable_stations[node], length) #How long it will charge #3
        reach_in_ticks = math.ceil(reachable_stations[node]['lenght'] / speed[customer['type']]) # When will reach ###assuming speed ## - 1 is margin #18
        reachable_stations[node]['ticksToCharge'] = ticks_charging
        reachable_stations[node]['ticksToReach'] = reach_in_ticks
        

        if reach_in_ticks in reachable_stations[node]['bookings'].keys() and reachable_stations[node]['bookings'][reach_in_ticks] == station['totalAmountOfChargers'] - station['totalAmountOfBrokenChargers']: # removes if bookings of chargers are full on arrival
            rem.append(node)

        for zone in zones:
            if reachable_stations[node]['zoneId'] == zone['id']:
                if reach_in_ticks in zone['bookings'].keys() and zone['bookings'][reach_in_ticks] + reachable_stations['chargeSpeedPerCharger'] > zone['totalProduction'] and node not in rem: # removes if bookings of totalDemand are full on arrival
                    rem.append(node)
                break

        if (customer['maxCharge'] / customer['energyConsumptionPerKm']) < end_point_length and node not in rem:# Removes if endpoint not reachable from station
            rem.append(node)

    # for node in rem:
    #     del reachable_stations[node]

    return reachable_stations

def charging_ticks(customer_max_charge, customer_energy_consumption, station_info, length) -> int:
    length_left = length - station_info['lenght']
    charge_at_station = length_left * customer_energy_consumption
    charge_needed =  customer_max_charge - charge_at_station  #assuming you want filled
    ticks_charging = math.ceil(charge_needed / ((station_info['chargeSpeedPerCharger'] / 60) * 5)) # might be better to // and + 1
    #ticks_charging += 1 ### margin
    
    return ticks_charging

def get_all_zones(zone_log, map): # Uppdaterar stations med produktion av el info
    zones = map['zones']

    zones_log = zone_log['zones']
    zone_log = {}
    for zone in zones_log:
        zone_log[zone['zoneId']] = [zone['totalProduction'], zone['totalDemand']]

    for zone in zones:
        zone['totalProduction'] = zone_log[zone['id']][0]
        zone['totalDemand'] = zone_log[zone['id']][1]
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