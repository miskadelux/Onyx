import json
from client import ConsiditionClient

api_key = "1546ce68-d586-461a-9534-add93e4daacf"
base_url = "http://localhost:8080/api"
map_name = "Batterytown"

client = ConsiditionClient(base_url, api_key)
start_map = client.get_map(map_name)

def save_map(dict_):
    with open('data/' + map_name + '.json', 'w') as f:
        json.dump(dict_, f, indent=4)


save_map(start_map)