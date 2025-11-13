from client import ConsiditionClient
from own_logic import load_ticks

def main():
    api_key = "1546ce68-d586-461a-9534-add93e4daacf"
    base_url = "https://api.considition.com/api" #"https://api.considition.com/api"
    map_name = "Thunderroad"
    client = ConsiditionClient(base_url, api_key)
    ticks = load_ticks()

    input_payload = {
        "mapName": map_name,
        "ticks": ticks,
    }
    # 27725 highscore # id 019a7ac4-db7b-7a2b-a1a4-a59c35fd2cc3 # Clutchfield
    # 36202 highscore # id 019a7ac8-6f38-7b80-b689-014e9ef27686 # Batterytown
    # 34429 highscore # id 019a7a8f-1d05-7e1c-b28d-5867702f87cb # Thunderroad

    game_response = client.post_game(input_payload)
    game_id = game_response.get('gameId', 0)
    print(game_id)
    

    final_score = (
        + game_response.get("score", 0)
    )

    print(final_score)

if __name__ == "__main__":
    main()