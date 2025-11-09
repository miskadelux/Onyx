from colorama import Fore, Style

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
        if node['target']['Type']!= 'Null':
            node['target']['inNode'] = node['id']
            node['target']['posX'] = node['posX']
            node['target']['posY'] = node['posY']
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

def shortest_length(start_node: str, graph, end_node=None, max_length=float('inf')) -> float|dict: #Cant predict correctly, not sure why
    visited = []
    dist = {start_node:0}

    pq = [(0, start_node)]
    while end_node not in visited and len(pq) > 0:
        weight, node = pq.pop(0)
        visited.append(node)

        for edge in graph[node]:
            if edge[1] + weight < max_length * 1: ### might want to add some legroom in case the drivers don't fint the optimal route?
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
    
def find_avalible_stations(customer, map, graph, stations):
    speed = {'Car': 4, 'Truck': 2.6} #Tested and got: car travel speed = 4km/tick, truck speed avg = 2.6km / tick, might change
    reachable_stations = {}
    length = calculate_max_lenght(customer)
    avalible_nodes = shortest_length(customer['inNode'], graph, max_length=length)

    for station in stations:
        if station['inNode'] in avalible_nodes.keys():
            reachable_stations[station['inNode']] = avalible_nodes[station['inNode']]

    rem = []
    for node in reachable_stations: 
        end_point_length = shortest_length(node, graph, end_node=customer['toNode'])
         
        charge_at_station = length - reachable_stations[node] # to figure out how long it needs to stay there. Also good if I calculate how long it takes to reach so i know not to send people using them at the same time because: too many people, to few chargers or: production cannot handle
        reach_in_ticks = reachable_stations[node] / speed[customer['type']]

        if (customer['maxCharge'] / customer['energyConsumptionPerKm']) < end_point_length:### if customer does not make it to end_point from station it gets removed
            rem.append(node)

    for node in rem:
        del reachable_stations[node]

    return reachable_stations

def get_zone_production(zone_log, map, stations): ### updaterar stations med produktion av el info
    zones_log = zone_log['zones']
    zone_log = {}
    for zone in zones_log:
        zone_log[zone['zoneId']] = [zone['totalProduction'], zone['totalDemand']]



    zones = {}
    for zone in map['zones']:
        zones[zone['id']] = {}
        zones[zone['id']]['topLeftY'] = zone['topLeftY']
        zones[zone['id']]['topLeftX'] = zone['topLeftX']
        zones[zone['id']]['bottomRightX'] = zone['bottomRightX']
        zones[zone['id']]['bottomRightY'] = zone['bottomRightY']

    for station in stations:
        for zone in zones:
            if station['posX'] <= zones[zone]['bottomRightX'] and station['posX'] >= zones[zone]['topLeftX'] and station['posY'] <= zones[zone]['bottomRightY'] and station['posY'] >= zones[zone]['topLeftY']:
                station['totalProduction'] = zone_log[zone][0] * 1000
                station['totalDemand'] = zone_log[zone][1] * 1000

    return stations
    
