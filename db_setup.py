import psycopg2

connection = psycopg2.connect(
    database = "NewWorld25",
    user = 'postgres',
    password = 'Franshsk19',
    host = 'localhost',
    port = '5432'
    )
cursor = connection.cursor()

# cursor.execute('''CREATE TABLE players (
#                player_id SERIAL PRIMARY KEY,
#                name VARCHAR(50) NOT NULL,
#                date DATE DEFAULT CURRENT_DATE,
#                winner BOOLEAN DEFAULT FALSE,
#                points INT DEFAULT 0);''')

# cursor.execute('''CREATE TABLE features (
#                feature_id SERIAL PRIMARY KEY,
#                name VARCHAR(50) UNIQUE,
#                cost_oxygen INT DEFAULT 0,
#                cost_water INT DEFAULT 0,
#                cost_energy INT DEFAULT 0);''')

# cursor.execute('''CREATE TABLE milestones (
#                milestone_id SERIAL PRIMARY KEY,
#                name VARCHAR(50) UNIQUE,
#                cost_forest INT DEFAULT 0,
#                cost_lake INT DEFAULT 0,
#                cost_city INT DEFAULT 0,
#                points INT NOT NULL);''')

# cursor.execute('''CREATE TABLE bank_resources (
#                resource_id SERIAL PRIMARY KEY,
#                name VARCHAR(50) UNIQUE,
#                amount INT DEFAULT 0);''')

# cursor.execute('''CREATE TABLE player_resources (
#                id SERIAL PRIMARY KEY,
#                player_id INT REFERENCES players(player_id) ON DELETE CASCADE,
#                resource_id INT REFERENCES bank_resources(resource_id),
#                amount INT DEFAULT 0);''')

# cursor.execute('''CREATE TABLE player_features (
#                id SERIAL PRIMARY KEY,
#                player_id INT REFERENCES players(player_id) ON DELETE CASCADE,
#                feature_id INT REFERENCES features(feature_id),
#                count INT DEFAULT 0);''')

# cursor.execute('''CREATE TABLE player_milestones (
#                id SERIAL PRIMARY KEY,
#                player_id INT REFERENCES players(player_id) ON DELETE CASCADE,
#                milestone_id INT REFERENCES milestones(milestone_id),
#                count INT DEFAULT 0);''')

# connection.commit()

# cursor.execute("""INSERT INTO bank_resources (name, amount) VALUES ('Oxygen', 6), ('Water', 6), ('Energy', 6);""")

# cursor.execute("""INSERT INTO features (name, cost_oxygen, cost_water, cost_energy) VALUES
#                ('Forest', 2, 1, 0),
#                ('Lake', 0, 2, 1),
#                ('City', 1, 1, 2);""")

# cursor.execute("""INSERT INTO milestones (name, cost_forest, cost_lake, cost_city, points) VALUES
#                ('Habitat', 1, 1, 0, 3),
#                ('Metropolis', 0, 0, 2, 5),
#                ('New World', 2, 2, 1, 10);""")

# connection.commit()
