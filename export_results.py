import psycopg2
import json

connection = psycopg2.connect(
    database = "NewWorld25",
    user = 'postgres',
    password = 'Franshsk19',
    host = 'localhost',
    port = '5432'
    )
cursor = connection.cursor()

def export_game_results():

    results = {
        "date": None,
        "winner": None,
        "players": []
        }

    cursor.execute("SELECT player_id, name, points, date FROM players")
    players = cursor.fetchall()

    max_points = 0
    winner = None

    for player_id, name, points, date in players:
        if points > max_points:
            max_points = points
            winner = name

        #  collect resources
        resources = {}
        cursor.execute(f'''SELECT a.name, b.amount
                       FROM player_resources b
                       JOIN bank_resources a ON b.resource_id = a.resource_id
                       WHERE b.player_id = %s''', (player_id,))
        rows = cursor.fetchall()
        for name, amount in rows:
            resources[name] = amount

        # collect features
        features = {}
        cursor.execute(f'''SELECT a.name, b.count
                       FROM player_features b
                       JOIN features a ON b.feature_id = a.feature_id
                       WHERE b.player_id = %s''', (player_id,))
        rows = cursor.fetchall()
        for name, count in rows:
            features[name] = count

        # collect milestones
        milestones = {}
        cursor.execute(f'''SELECT a.name, b.count
                       FROM player_milestones b
                       JOIN milestones a ON b.milestone_id = a.milestone_id
                       WHERE b.player_id = %s''', (player_id,))
        rows = cursor.fetchall()
        for name, count in rows:
            milestones[name] = count
        
        results['players'].append({
            "name": name,
            "points": points,
            "resources": resources,
            "features": features,
            "milestones": milestones})
    
    results["winner"] = winner
    results["date"] = date