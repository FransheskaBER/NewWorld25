from development_cards import draw_development_card
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

        # Show the bank resources before asking
        print("\n\n\033[1;34m🏦 These are the current resources in the bank:\033[0m")

        cursor.execute("SELECT name, amount FROM bank_resources")
        for name, amount in cursor.fetchall():
            icons = {
                "Oxygen": "💨",
                "Water": "💧",
                "Energy": "⚡"}
            print(f"- {icons.get(name, '❓')} {name}: {amount}")

        print("\n\n\033[1;33m📦 Which resources do you want to take?\033[0m")
        print("\033[1;36m1️⃣  Take 3 different resources (💨 Oxygen, 💧 Water, ⚡ Energy)\033[0m")
        print("\033[1;35m2️⃣  Take 2 of the same resource\033[0m")

        try:
            choice = int(input("\n\033[1;32m👉 Enter 1 or 2: \033[0m"))
        except ValueError:
            print("\nPlease enter a number (1 or 2).")
            return self.gather_resources()  # restart this step
        
        if choice == 1:

            # First we are going to check availability
            cursor.execute("SELECT resource_id, name, amount FROM bank_resources")
            resources = cursor.fetchall()
            enough = True
            for row in resources:

                # Take the amount by index and store it in a variable
                amount = row[2]
                if amount < 1:
                    enough = False
                    break
            if enough:
                for resource_id, _, _ in resources:
                    cursor.execute("UPDATE player_resources SET amount = amount + 1 WHERE player_id = %s AND resource_id = %s", (self.player_id, resource_id))
                    cursor.execute("UPDATE bank_resources SET amount = amount - 1 WHERE resource_id = %s", (resource_id,))
                connection.commit()

                msg = f"---✔️ {self.name} gathered 1 💨 Oxygen, 1 💧 Water, 1 ⚡ Energy ✔️---"
                print("\n\033[1;32m" + msg.center(70) + "\033[0m\n")


            else:
                print("\n\nNot enough resources in the bank for 3 different ones. Choose option 2.")
                return self.gather_two_same()
        elif choice == 2:
            return self.gather_two_same()  # Call the function gather_two_same which ask player which resources

    def gather_two_same(self):
        resource_type = input("\n\nEnter O for Oxygen, W for Water, E for Energy: ").upper()
        mapping = {"O": 1, "W": 2, "E": 3}
        if resource_type not in mapping:
            print("\nInvalid resource choice.")
            return
        resource_id = mapping[resource_type]
        cursor.execute("SELECT amount FROM bank_resources WHERE resource_id = %s", (resource_id,))
        bank_amount = cursor.fetchone()[0] #  we are adding the index 0 to get the actual number, since fetchone gets a tuple (4,)
        if bank_amount >= 2:
            cursor.execute("UPDATE player_resources SET amount = amount + 2 WHERE player_id = %s AND resource_id = %s", (self.player_id, resource_id))
            cursor.execute("UPDATE bank_resources SET amount = amount - 2 WHERE resource_id = %s", (resource_id,))
            connection.commit()
                      
            msg = f"---✔️ {self.name} gathered 2 of {resource_type} ✔️---"
            print("\n\033[1;32m" + msg.center(70) + "\033[0m\n")


        else:
            print(f"\n\nNot enough {resource_type} in the bank.")

    def build_feature(self):
        # Fetch player's current resrouces for visibility
        # msg = f"📦 {self.name}'s Current Resources 📦"
        # print("\n\033[1;34m" + msg.center(80, "=") + "\033[0m")
        # cursor.execute("SELECT a.name, b.amount FROM player_resources b JOIN bank_resources a ON b.resource_id = a.resource_id WHERE player_id = %s", (self.player_id,))
        # for res_name, amount in cursor.fetchall():
        #     print(f"- {res_name}: {amount}")

        msg = f"📦 Spend your resources to build a Forest, Lake, or City 📦"
        print("\n\033[1;34m" + msg.center(80, "=") + "\033[0m\n")
        
        # Fetch all the features we have for visibility
        cursor.execute("SELECT feature_id, name, cost_oxygen, cost_water, cost_energy FROM features")
        rows = cursor.fetchall()
        for feature_id, name, cost_oxygen, cost_water, cost_energy in rows:
            print(f"- {name} = "
                  f"\033[1;36m{cost_oxygen} 💨 Oxygen\033[0m + "
                  f"\033[1;34m{cost_water} 💧 Water\033[0m + "
                  f"\033[1;33m{cost_energy} ⚡ Energy\033[0m") 

        feature_type = input("\nEnter F for forest, L for lake and C for city: ").upper()
        mapping = {"F": 1, "L": 2, "C": 3}
        if feature_type not in mapping:
            print("\nInvalid feature choice.")
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
            print("\nYou don’t have enough resources to build this feature.")
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
        print(f"\n\033[1;32m🏆 {self.name} built a {feature_name}! 🏆\033[0m")
    
    def claim_milestone(self):
        # Fetch current player's feature for visibility
        print(f"\n\n{self.name}'s current features:\n")
        cursor.execute("SELECT a.name, b.count FROM player_features b JOIN features a ON b.feature_id = a.feature_id WHERE player_id = %s", (self.player_id,))
        for feat_name, count in cursor.fetchall():
            print(f"- {feat_name}: {count}")

        print("\nIf you already own the required Features, trade them in to claim the milestone: Habitat, Metropolis or New World.\n")

        # Fecth all milestone
        cursor.execute("SELECT milestone_id, name, cost_forest, cost_lake, cost_city, points FROM milestones")
        rows = cursor.fetchall()
        for milestone_id, name, cost_forest, cost_lake, cost_city, points in rows:
            print(f"- {name} = {cost_forest} 🌲 Forest + {cost_lake} 💧 Lake + {cost_city} 🏙️ City ({points} ⭐ points)")

        milestone_type = input("\nEnter H for habitat, M for metropolis and N for new world: ").upper()
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
            print("\nYou don’t have enough features to claim this milestone.")
            return
        
        # Deduct features
        for feature_id, required_per_milestone in [(1, cost_forest), (2, cost_lake), (3, cost_city)]:
            if required_per_milestone > 0:
                cursor.execute("UPDATE player_features SET count = count - %s WHERE player_id = %s AND feature_id = %s", (required_per_milestone, self.player_id, feature_id))
        
        # Insert milestone 
        cursor.execute("UPDATE player_milestones SET count = count + 1 WHERE player_id = %s AND milestone_id = %s RETURNING *;", (self.player_id, milestone_id))
        
        # Add milestone points 
        self.add_points(milestone_id)

        cursor.execute("SELECT name FROM milestones WHERE milestone_id = %s", (milestone_id,))
        milestone_name = cursor.fetchone()[0]
        connection.commit()
        print(f"\n\033[1;33m🏆 {self.name} claimed the {milestone_name} milestone "f"and now has {self.points} points! 🏆\033[0m")


class Game:    
    def __init__(self):
        self.players = []
        self.round = 0

    def setup(self):
        try:
            num_players = int(input("\nHow many players (2–3)? "))
        except ValueError:
            print("\nPlease enter a number: ")
            return self.setup()
        self.current_player_ids = []
        for i in range(num_players):
            name = input(f"\n\nEnter name for player {i+1}: ")
            
            # Insert into DB
            cursor.execute("INSERT INTO players (name, date, winner, points) VALUES (%s, CURRENT_DATE, false, 0) RETURNING player_id", (name,))
            player_id = cursor.fetchone()[0]
            self.current_player_ids.append(player_id)

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
            
            # Create default rows in player_milestones
            cursor.execute("SELECT milestone_id FROM milestones")
            milestone_ids = cursor.fetchall()
            for (m_id,) in milestone_ids:
                cursor.execute("INSERT INTO player_milestones (player_id, milestone_id, count) VALUES (%s, %s, 0)", (player_id, m_id))

            connection.commit()

            # Create a Player object
            player = Player(player_id, name)
            self.players.append(player)

        for p in self.players:
            print(f"\n\033[1;36m✨ Welcome {p.name}! ✨\033[0m")

    def play_round(self):
        self.round += 1
                
        for player in self.players:
            msg = f"👉 {player.name.upper()}'S TURN 👈"
            print("\n\033[1;30;43m" + msg.center(80) + "\033[0m")

            # Show player's resources
            cursor.execute("SELECT br.name, pr.amount FROM player_resources pr JOIN bank_resources br ON pr.resource_id = br.resource_id WHERE player_id = %s", (player.player_id,))
            print("\n" + "="*40)
            print(f"\n{player.name}'s current resources:")
            for res_name, amount in cursor.fetchall():
                print(f"- {res_name}: {amount}")

            #  Show player's features
            cursor.execute("SELECT f.name, pf.count FROM player_features pf JOIN features f ON pf.feature_id = f.feature_id WHERE player_id = %s", (player.player_id,))
            print(f"\n{player.name}'s current features:")
            for feat_name, count in cursor.fetchall():
                print(f"- {feat_name}: {count}")
            print(f"- Points: {player.points}")
            print("\n" + "="*40 + "\n")


            #  Check if this player can build
            can_build = False
            cursor.execute("SELECT cost_oxygen, cost_water, cost_energy FROM features")
            features = cursor.fetchall()
            for cost_o, cost_w, cost_e in features:
                cursor.execute("SELECT amount FROM player_resources WHERE player_id = %s AND resource_id = 1", (player.player_id,))
                o2 = cursor.fetchone()[0]
                cursor.execute("SELECT amount FROM player_resources WHERE player_id = %s AND resource_id = 2", (player.player_id,))
                h2o = cursor.fetchone()[0]
                cursor.execute("SELECT amount FROM player_resources WHERE player_id = %s AND resource_id = 3", (player.player_id,))
                eng = cursor.fetchone()[0]
                if o2 >= cost_o and h2o >= cost_w and eng >= cost_e:
                    can_build = True
                    break
            
            #  Check if this player can claim
            can_claim = False
            cursor.execute("SELECT cost_forest, cost_lake, cost_city FROM milestones")
            milestones = cursor.fetchall()
            for cost_f, cost_l, cost_c in milestones:
                cursor.execute("SELECT count FROM player_features WHERE player_id = %s AND feature_id = 1", (player.player_id,))
                forests = cursor.fetchone()[0]
                cursor.execute("SELECT count FROM player_features WHERE player_id = %s AND feature_id = 2", (player.player_id,))
                lakes = cursor.fetchone()[0]
                cursor.execute("SELECT count FROM player_features WHERE player_id = %s AND feature_id = 3", (player.player_id,))
                cities = cursor.fetchone()[0]
                if forests >= cost_f and lakes >= cost_l and cities >= cost_c:
                    can_claim = True
                    break
            
            #  Show choices dynamically
            print("\n" + "="*30)
            print("🎯  Choose Action  🎯")
            print("="*30)

            print("\n1 = Gather resources")
            if can_build:
                print("\n2 = Build a feature")
            if can_claim:
                print("\n3 = Claim a milestone")
            if not can_build and not can_claim:
                print("\nYou don’t have enough to build or claim anything this turn — you should Gather or take a development card!")
            print("\n4 = Draw a development card")  # always available
            
            # Ask for action
            choice = input("\n\nEnter your choice (or type 'quit' to stop): ")

            if choice.lower() == "quit":
                print("\nGame aborted!")

                import json
                from export_results import export_game_results   

                results = export_game_results()

                with open("game_results.json", "w") as f:
                    json.dump(results, f, indent=4, default=str)
                
                # Reset DB tables
                cursor.execute("UPDATE bank_resources SET amount = 6;")
                connection.commit()
                
                # Reset Game object
                self.players = []
                self.round = 0

                print("The game has been reset. Run setup() to start a new game.")
                return True # to stop current round right away
            
            if choice == "1":
                player.gather_resources()
            elif choice == "2" and can_build:
                player.build_feature()
            elif choice == "3" and can_claim:
                player.claim_milestone()
            elif choice == "4":
                draw_development_card(player.player_id, player.name)
            else:
                print("Invalid choice, turn skipped.")

            # Check win after each turn
            if self.check_winner():
                return True  # game ends
            
        return False  # no winner yet

    def check_winner(self):
        for player in self.players:
            if player.points >= 10:
                print(f"\n\033[1;37;45m 🎉 {player.name} wins with {player.points} points! 🎉 \033[0m")


                from export_results import export_game_results   

                results = export_game_results()

                with open("game_results.json", "w") as f:
                    json.dump(results, f, indent=4, default=str)
                
                return True
        
        return False


if __name__ == "__main__":
    game = Game()
    game.setup()

    game_over = False
    while not game_over and game.round < 10:
        game_over = game.play_round()

    if not game_over:
        winner = max(game.players, key=lambda p: p.points)
        if winner.points == 0:
            print(f"\nGame over! No one wins. Everyone has 0 points after {game.round} rounds.")
            
            # Reset DB tables
            cursor.execute("UPDATE bank_resources SET amount = 6;")
            connection.commit()
            
            # Reset Game object
            game.players = []
            game.round = 0
            print("The game has been reset. Run setup() to start a new game.")
        else:
            print(f"\nGame over! {winner.name} wins with {winner.points} points (after {game.round} rounds).")
            
            # Reset DB tables
            cursor.execute("UPDATE bank_resources SET amount = 6;")
            connection.commit()
            
            # Reset Game object
            game.players = []
            game.round = 0
            print("The game has been reset. Run setup() to start a new game.")

        from export_results import export_game_results   

        results = export_game_results()

        with open("game_results.json", "w") as f:
            json.dump(results, f, indent=4, default=str)



        


