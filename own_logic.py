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
                customers.append(customer)

    return customers

def get_all_stations(map_obj):
    stations = []

    for node in map_obj['nodes']:
        if node['target']['Type']!= 'Null':
            stations.append(node['target'])

    return stations
    



# clients = client.ConsiditionClient("http://localhost:8080/api", None)
# map_obj = clients.get_map('Turbohill')
# k = get_all_customers(map_obj)

# # print_map_UI(map_obj)
# # for i in map_obj['nodes']:
# #     if i['id'] == '7.6':
# #         l = i
# print(k)
# print(len(k))