from colorama import Fore, Style

def print_map_UI(map_obj):
    state = map_obj


    map = [['0' for i in range(10)] for j in range(10)]

    for node in state['nodes']:
        if len(node['customers']) > 0:
            map[node['posX']][node['posY']] = str(len(node['customers']))
        elif node['target']['Type'] == 'ChargingStation':
            map[node['posY']][node['posX']] = 'O'
        else:
            map[node['posX']][node['posY']] = 'X'

    for y in range(len(map)):
        for x in range(len(map[y])):
            if map[x][y] == 'X':
                print(Fore.RED, end="")
            elif map[x][y] == '0':
                print(Fore.BLACK, end="")
            elif map[x][y] == 'O':
                print(Fore.YELLOW, end="")
            else:
                print(Fore.GREEN, end="")


            print(map[x][y], end="    ")
            print(Style.RESET_ALL, end="")

        print()
        print()