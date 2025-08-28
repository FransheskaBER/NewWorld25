import requests
import random
from db_setup import connection, cursor

def draw_development_card(player_id, player_name):

    # Player draws a random development card.
    # Can give resources, features, or just a funny message.
    card_type = random.choice(["resource", "feature", "funny"])

    if card_type == "resource":

        # Randomly choose between Oxygen (1), Water (2), Energy (3)
        resource_map = {1: "Oxygen", 2: "Water", 3: "Energy"}
        resource_id = random.choice([1, 2, 3])
        resource_name = resource_map[resource_id]

        # Give it directly to the player (not from bank)
        cursor.execute("UPDATE player_resources SET amount = amount + 1 WHERE player_id = %s AND resource_id = %s", (player_id, resource_id))
        connection.commit()

        print(f"{player_name} drew a card: +1 {resource_name} (bonus resource).")

    elif card_type == "feature":

        # Randomly choose between Forest (1), Lake (2), City (3)
        feature_map = {1: "Forest", 2: "Lake", 3: "City"}
        feature_id = random.choice([1, 2, 3])
        feature_name = feature_map[feature_id]

        # Give it directly to the player (not from bank)
        cursor.execute("UPDATE player_features SET count = count + 1 WHERE player_id = %s AND feature_id = %s", (player_id, feature_id))
        connection.commit()

        print(f"{player_name} drew a card: +1 {feature_name} (bonus resource).")

    elif card_type == "funny":
        try:
            r = requests.get("https://official-joke-api.appspot.com/jokes/random", timeout=5)
            if r.status_code == 200:
                data = r.json()
                print(f"{player_name} drew a funny card: {data['setup']} ... {data['punchline']}")
            else:
                print(f"{player_name} drew a funny card, but the API failed. No joke this time.")
        except Exception as e:
            print(f"{player_name} tried to draw a funny card, but something went wrong: {e}")
