from colorama import Fore, Style
import client

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

def find_customer(id: str, customers: list): ### testing
    for customer in customers:
        if customer['id'] == id:
            return customer


def get_all_stations(map):
    stations = []

    for node in map['nodes']:
        if node['target']['Type']!= 'Null':
            node['target']['inNode'] = node['id']
            stations.append(node['target'])

    return stations
    
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
            if edge[1] + weight < max_length: ### might want to add some legroom in case the drivers don't fint the optimal route?
                if edge[0] not in dist.keys():
                    dist[edge[0]] = edge[1] + weight
                elif dist[edge[0]] > edge[1] + weight:
                    dist[edge[0]] = edge[1] + weight
                    
                in_pq = False
                for i in pq:
                    if i[1] == edge[0]:
                        in_pq = True

                if edge[0] not in visited and not in_pq:
                    pq.append((edge[1] + weight, edge[0]))

    if end_node != None and end_node in dist.keys():
        return dist[end_node]
    elif end_node != None:
        return None
    else:
        return dist
    
def find_nearby_stations(customer, map, graph, stations):
    reachable_stations = {}
    max_length = calculate_max_lenght(customer)
    avalible_nodes = shortest_length(customer['inNode'], graph, max_length=max_length)

    for station in stations:
        if station['inNode'] in avalible_nodes.keys():
            reachable_stations[station['inNode']] = avalible_nodes[station['inNode']]

    return reachable_stations

