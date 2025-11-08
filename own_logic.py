from colorama import Fore, Style
import client

def print_map_UI(map_obj):
    class tile:
        def __init__(self, color, symbol):
            self.color = color
            self.symbol = symbol

    state = map_obj

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




def get_all_customers(map_obj):
    customers = []

    for node in map_obj['nodes']:
        if len(node['customers']) > 0:
            for customer in node['customers']:
                customer['inNode'] = node['id']
                customers.append(customer)
                
    for edge in map_obj['edges']:
        if len(edge['customers']) > 0:
            for customer in edge['customers']:
                customer['inNode'] = edge['toNode']
                customers.append(customer)

    return customers


def get_all_stations(map_obj):
    stations = []

    for node in map_obj['nodes']:
        if node['target']['Type']!= 'Null':
            node['target']['inNode'] = node['id']
            stations.append(node['target'])

    return stations
    

def create_graph(map_obj):
    graph = {}
    map = map_obj.copy()
    for node in map['nodes']:
        graph[node['id']] = []
        for edge in map['edges']:
            if edge['fromNode'] == node['id']:
                graph[node['id']].append((edge['toNode'], edge['length']))

    return graph






def shortest_lenght(start_node: str, graph, end_node=None, max_lenght=float('inf')) -> float|dict:
    visited = []
    dist = {}

    pq = [(0, start_node)]
    while end_node not in visited and len(pq) > 0:
        weight, node = pq.pop(0)
        visited.append(node)

        for edge in graph[node]:
            if edge[1] + weight < max_lenght:
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

    if end_node != None:
        return dist[end_node]
    else:
        return dist