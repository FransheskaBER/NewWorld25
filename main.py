import psycopg2

connection = psycopg2.connect(
    database = "NewWorld25",
    user = 'postgres',
    password = 'Franshsk19',
    host = 'localhost',
    port = '5432'
    )
cursor = connection.cursor()

class Player:
    def __init__(self, player_id, name):
        self.player_id = player_id
        self.name = name
        self.points = 0
    
    def add_points(self, milestone_id):
        # First look at how many points a player gets with that milestone
        cursor.execute("SELECT points FROM milestones WHERE milestone_id = %s", (milestone_id,))
        result = cursor.fetchone()[0]
        if result:
            milestone_points = result
            # Now, we will update the player's points here and in the DB
            self.points += milestone_points
            cursor.execute("UPDATE players SET points = points + %s WHERE player_id = %s", (milestone_points, self.player_id))
            connection.commit()

    def gather_resources(self):
        print("\nWhich resources do you want to take?")
        print("\n1. Take 3 different resources (Oxygen, Water, Energy)")
        print("\n2. Take 2 of the same resource")
        choice = int(input("\nEnter 1 or 2: "))
        if choice == 1:
            # First we are going to check availability
            cursor.execute("SELECT resource_id, name, amount FROM bank_resources")
            resources = cursor.fetchall()
            enough = True
            for row in resources:
                # Take the amount index and store it in a variable
                amount = row[2]
                if amount < 1:
                    enough = False
                    break
            if enough:
                for resource_id, _, _ in resources:
                    cursor.execute("UPDATE player_resources SET amount = amount + 1 WHERE player_id = %s AND resource_id = %s", (self.player_id, resource_id))
                    cursor.execute("UPDATE bank_resources SET amount = amount - 1 WHERE resource_id = %s", (resource_id,))
                connection.commit()
                print(f"{self.name} gathered 1 Oxygen, 1 Water, 1 Energy.")
            else:
                print("Not enough resources in the bank for 3 different ones. Falling back to option 2.")
                return self.gather_two_same()
    
    def gather_two_same(self):
        resource_type = input("Enter O for Oxygen, W for Water, E for Energy: ").upper()
        mapping = {"O": 1, "W": 2, "E": 3}
        if resource_type not in mapping:
            print("Invalid resource choice.")
            return
        resource_id = mapping[resource_type]
        cursor.execute("SELECT amount FROM bank_resources WHERE resource_id = %s", (resource_id,))
        bank_amount = cursor.fetchone()[0] #  we are adding the index 0 to get the actual number, since fetchone gets a tuple (4,)
        if bank_amount >= 2:
            cursor.execute("UPDATE player_resources SET amount = amount + 2 WHERE player_id = %s AND resource_id = %s", (self.player_id, resource_id))
            cursor.execute("UPDATE bank_resources SET amount = amount - 2 WHERE resource_id = %s", (resource_id,))
            connection.commit()
            print(f"{self.name} gathered 2 of {resource_type}.")
        else:
            print(f"Not enough {resource_type} in the bank.")

    def build_feature(self):
        print("Spend your resources to build a Forest, Lake, or City.")
        # Fetch all the features we have for visibility
        cursor.execute("SELECT feature_id, name, cost_oxygen, cost_water, cost_energy FROM features")
        rows = cursor.fetchall()
        for feature_id, name, cost_oxygen, cost_water, cost_energy in rows:
            print(f"- {name} = {cost_oxygen} Oxygen + {cost_water} Water + {cost_energy} Energy")
        feature_type = input("Enter F for forest, L for lake and C for city: ").upper()
        mapping = {"F": 1, "L": 2, "C": 3}
        if feature_type not in mapping:
            print("Invalid feature choice.")
            return
        # Fech feature_id from the player's input
        feature_id = mapping[feature_type]
        # Get feature costs from DB
        cursor.execute("SELECT cost_oxygen, cost_water, cost_energy FROM features WHERE feature_id = %s", (feature_id,))
        cost_oxygen, cost_water, cost_energy = cursor.fetchone()
        # Check if player has enough resources
        enough = True
        for resource_id, required_per_feature in [(1, cost_oxygen), (2, cost_water), (3, cost_energy)]:
            if required_per_feature > 0:
                cursor.execute("SELECT amount FROM player_resources WHERE player_id = %s AND resource_id = %s", (self.player_id, resource_id))
                amount = cursor.fetchone()[0]
                if amount < required_per_feature:
                    enough = False
                    break
        if not enough:
            print("You don’t have enough resources to build this feature.")
            return
        # Deduct resources from player and return them to the bank
        for resource_id, required_per_feature in [(1, cost_oxygen), (2, cost_water), (3, cost_energy)]:
        # the resource id is for example oxygen 1 and the cost_oxygen is how much oxygen we need for this feature? 2, 1, etc..
            if required_per_feature > 0:
                cursor.execute("UPDATE player_resources SET amount = amount - %s WHERE player_id = %s AND resource_id = %s", (required_per_feature, self.player_id, resource_id))
                cursor.execute("UPDATE bank_resources SET amount = amount + %s WHERE resource_id = %s", (required_per_feature, resource_id))
        # Add feature to player_features
        cursor.execute("UPDATE player_features SET count = count + 1 WHERE player_id = %s AND feature_id = %s", (self.player_id, feature_id))
        cursor.execute("SELECT name FROM features WHERE feature_id = %s", (feature_id,))
        feature_name = cursor.fetchone()[0]
        connection.commit()
        print(f"{self.name} built a {feature_name}.")
    
    def claim_milestone(self):
        print("If you already own the required Features, trade them in to claim the milestone: Habitat, Metropolis or New World.")

        # Fecth all milestone
        cursor.execute("SELECT milestone_id, name, cost_forest, cost_lake, cost_city, points FROM milestones")
        rows = cursor.fetchall()
        for milestone_id, name, cost_forest, cost_lake, cost_city, points in rows:
            print(f"- {name} = {cost_forest} Forest + {cost_lake} Lake + {cost_city} City ({points} points)")
        milestone_type = input("Enter H for habitat, M for metropolis and N for new world: ").upper()
        mapping = {"H": 1, "M": 2, "N": 3}
        if milestone_type not in mapping:
            print("Invalid feature choice.")
            return
        
        # Fech milestone_id from the player's input
        milestone_id = mapping[milestone_type]

        # Get milestone costs from DB
        cursor.execute("SELECT cost_forest, cost_lake, cost_city FROM milestones WHERE milestone_id = %s", (milestone_id,))
        cost_forest, cost_lake, cost_city = cursor.fetchone()

        # Check if player has enough features
        enough = True
        for feature_id, required_per_milestone in [(1, cost_forest), (2, cost_lake), (3, cost_city)]:
            if required_per_milestone > 0:
                cursor.execute("SELECT count FROM player_features WHERE player_id = %s AND feature_id = %s", (self.player_id, feature_id))
                amount = cursor.fetchone()[0]
                if amount < required_per_milestone:
                    enough = False
                    break
        if not enough:
            print("You don’t have enough features to claim this milestone.")
            return
        
        # Deduct features
        for feature_id, required_per_milestone in [(1, cost_forest), (2, cost_lake), (3, cost_city)]:
            if required_per_milestone > 0:
                cursor.execute("UPDATE player_features SET count = count - %s WHERE player_id = %s AND feature_id = %s", (required_per_milestone, self.player_id, feature_id))
        
        # Insert milestone 
        cursor.execute("INSERT INTO player_milestones (player_id, milestone_id) VALUES (%s, %s)", (self.player_id, milestone_id))
        
        # Add milestone points 
        self.add_points(milestone_id)

        cursor.execute("SELECT name FROM milestones WHERE milestone_id = %s", (milestone_id,))
        milestone_name = cursor.fetchone()[0]
        connection.commit()
        print(f"{self.name} claimed the {milestone_name} milestone and now has {self.points} points!")

class Game:    
    def __init__(self):
        self.players = []
        self.round = 0

    def setup(self):
        try:
            num_players = int(input("How many players (2–3)? "))
        except ValueError:
            print("Please enter a number: ")
            return self.setup()
        
        for i in range(num_players):
            name = input(f"Enter name for player {i+1}: ")
            
            # Insert into DB
            cursor.execute("INSERT INTO players (name) VALUES (%s) RETURNING player_id", (name,))
            player_id = cursor.fetchone()[0]

            # Create default rows in player_resources
            cursor.execute("SELECT resource_id FROM bank_resources")
            resource_ids = cursor.fetchall()
            for (r_id,) in resource_ids:
                cursor.execute("INSERT INTO player_resources (player_id, resource_id, amount) VALUES (%s, %s, 0)", (player_id, r_id))

            # Create default rows in player_features
            cursor.execute("SELECT feature_id FROM features")
            feature_ids = cursor.fetchall()
            for (f_id,) in feature_ids:
                cursor.execute("INSERT INTO player_features (player_id, feature_id, count) VALUES (%s, %s, 0)", (player_id, f_id))

            connection.commit()

            # Create a Player object
            player = Player(player_id, name)
            self.players.append(player)

        for p in self.players:
            print(f"Welcome {p.name}!")

    def play_round(self):
        self.round += 1
        print(f"\n--- Round {self.round} ---")

        for player in self.players:
            print(f"\n{player.name}'s turn:")
            choice = input("Choose action: 1 = Gather, 2 = Build, 3 = Claim milestone: ")

            if choice.lower() == "quit":
                print("\nGame aborted! Resetting everything...")
                
                # Reset DB tables
                cursor.execute("TRUNCATE player_milestones, player_features, player_resources, players RESTART IDENTITY CASCADE;")
                cursor.execute("UPDATE bank_resources SET amount = 4;")
                connection.commit()
                
                # Reset Game object
                self.players = []
                self.round = 0

                print("The game has been reset. Run setup() to start a new game.")
                return True # to stop current round right away
            
            if choice == "1":
                player.gather_resources()
            elif choice == "2":
                player.build_feature()
            elif choice == "3":
                player.claim_milestone()
            else:
                print("Invalid choice, turn skipped.")

            # Check win after each turn
            if self.check_winner():
                return True  # game ends
        return False  # no winner yet

    def check_winner(self):
        for player in self.players:
            if player.points >= 15:
                print(f"\n{player.name} wins with {player.points} points!")
                return True
        return False



    

        


