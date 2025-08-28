import psycopg2
import json
import datetime

connection = psycopg2.connect(
    database = "NewWorld25",
    user = 'postgres',
    password = 'Franshsk19',
    host = 'localhost',
    port = '5432'
    )
cursor = connection.cursor()

def export_game_results(current_player_ids=None):

    results = {
        "date": None,
        "winner": None,
        "players": []
        }
    
    if current_player_ids:
        cursor.execute("SELECT player_id, name, points, date FROM players WHERE player_id = ANY(%s);", (current_player_ids,))
    else:
        # fallback: only today's players
        cursor.execute("SELECT player_id, name, points, date FROM players WHERE date = CURRENT_DATE;")

    players = cursor.fetchall()

    max_points = -1
    winner = None

    for player_id, player_name, points, date in players:
        if points > max_points:
            max_points = points
            winner = player_name

        #  collect resources
        resources = {}
        cursor.execute(f'''SELECT br.name AS resource_name, pr.amount
                        FROM player_resources pr
                        JOIN bank_resources br ON pr.resource_id = br.resource_id
                        WHERE pr.player_id = %s;''', (player_id,))
        rows = cursor.fetchall()
        for r_name, amount in rows:
            resources[r_name] = amount

        # collect features
        features = {}
        cursor.execute(f'''SELECT f.name AS feature_name, pf.count
                        FROM player_features pf
                        JOIN features f ON pf.feature_id = f.feature_id
                        WHERE pf.player_id = %s;''', (player_id,))
        rows = cursor.fetchall()
        for f_name, count in rows:
            features[f_name] = count

        # collect milestones
        milestones = {}
        cursor.execute(f'''SELECT m.name AS milestone_name, pm.count
                        FROM player_milestones pm
                        JOIN milestones m ON pm.milestone_id = m.milestone_id
                        WHERE pm.player_id = %s;''', (player_id,))
        rows = cursor.fetchall()
        for m_name, count in rows:
            milestones[m_name] = count
        
        results['players'].append({
            "name": player_name,
            "points": points,
            "resources": resources,
            "features": features,
            "milestones": milestones})
        
        if results["date"] is None:
            results["date"] = str(date)
    
    results["winner"] = winner
    return results