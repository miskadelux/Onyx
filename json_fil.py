import json

def save_ticks(dict_):
    with open('data/Clutchfield.json', 'w') as f:
        json.dump(dict_, f)
