from db_connection import DatabaseConnection
from ingredients import IngredientsModel
from .agents import AgentsModel
from municipalities import MunicipalitiesModel
from game_state import GameState
from game_logic import GameLogic
from views.game_view import GameView


def main():
    """
    Main game runner that initializes and manages the game flow.
    """
    # Database configuration
    db_config = {
        'host': '127.0.0.1',
        'port': 3306,
        'database': 'pandemic_updated',
        'user': 'root',
        'password': 'password'
    }

    # Initialize database connection
    db_connection = DatabaseConnection(db_config)

    try:
        # Initialize models
        ingredients_model = IngredientsModel(db_connection)
        agents_model = AgentsModel(db_connection)
        municipalities_model = MunicipalitiesModel(db_connection)

        # Initialize game components
        game_state = GameState()
        game_logic = GameLogic(
            ingredients_model,
            agents_model,
            municipalities_model,
            game_state
        )
        game_view = GameView()

        # Game introduction
        game_view.display_game_intro()

        # Get total municipalities for win condition
        total_municipalities = len(municipalities_model.fetch_municipalities())

        # Main game loop
        while True:
            game_view.display_status(game_state)
            action = game_view.display_menu()

            if action == '1':
                ingredient = game_logic.gather_ingredient()
                if ingredient:
                    print(f"Collected: {ingredient}")
                else:
                    print("No more ingredients to collect.")

            elif action == '2':
                if game_logic.create_virus():
                    print("Virus created successfully!")
                else:
                    print("Cannot create virus. Check ingredients or points.")

            elif action == '3':
                agent = game_logic.deploy_agent()
                if agent:
                    print(f"Agent {agent} deployed!")
                else:
                    print("Cannot deploy agent. Check available points.")

            elif action == '4':
                if not game_state.virus_created:
                    print("Virus must be created first!")
                    continue

                # Get list of unaffected municipalities
                unaffected_municipalities = [
                    m for m in municipalities_model.fetch_municipalities()
                    if m not in game_state.affected_municipalities
                ]

                if not unaffected_municipalities:
                    print("All municipalities have been affected!")
                    continue

                # Let player choose a municipality
                print("Select a municipality to affect:")
                for i, municipality in enumerate(unaffected_municipalities, 1):
                    print(f"{i}. {municipality}")

                try:
                    choice = int(input("Enter municipality number: ")) - 1
                    if 0 <= choice < len(unaffected_municipalities):
                        selected_municipality = unaffected_municipalities[choice]
                        if game_logic.administer_virus(selected_municipality):
                            print(f"{selected_municipality} has been affected!")
                        else:
                            print("Failed to administer virus.")
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Please enter a valid number.")

            elif action == '5':
                print("Ending turn...")
                # Optional: Add any end-of-turn logic here

            # Check game completion
            game_status = game_state.is_game_over(total_municipalities)
            if game_status == "win":
                print("Congratulations! You've successfully spread the virus to all municipalities!")
                break
            elif game_status == "loss":
                print("Game Over! You've run out of points.")
                break

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure database connection is closed
        db_connection.close()

if __name__ == "__main__":
    main()