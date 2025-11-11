from client import ConsiditionClient
from own_logic import load_ticks

def main():
    api_key = "1546ce68-d586-461a-9534-add93e4daacf"
    base_url = "https://api.considition.com/api" #"https://api.considition.com/api"
    map_name = "Clutchfield"
    client = ConsiditionClient(base_url, api_key)
    ticks = load_ticks()

    input_payload = {
        "mapName": map_name,
        "ticks": ticks,
    }
    # 12843 highscore # id 019a74e8-ceda-746e-af85-f0dcd5cdb9c2
    # 16193 # id 019a74e3-da5b-7294-b076-8a3b526ebd05

    game_response = client.post_game(input_payload)
    game_id = game_response.get('gameId', 0)
    print(game_id)
    

    final_score = (
        + game_response.get("score", 0)
    )

    print(final_score)

if __name__ == "__main__":
    main()