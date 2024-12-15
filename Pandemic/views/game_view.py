class GameView:
    """
    Manages game display and user interaction for console-based game.
    """

    def display_game_intro(self):
        """
        Display the game introduction and rules.
        """
        print("Pandemic Strategy Game")
        print("=" * 30)
        print("Mission: Develop and spread a virus across Finland")
        print("\nObjectives:")
        print("1. Collect 5 ingredients to create the virus")
        print("2. Deploy agents to help spread the virus")
        print("3. Affect all municipalities to win")
        print("\nRules:")
        print("- Limited points available")
        print("- Points are gained/lost through actions")
        print("- Agents lose health when spreading the virus")
        print("= " * 30)

    def display_status(self, game_state):
        """
        Display current game status.

        :param game_state: Current game state
        """
        print("\n--- Game Status ---")
        print(f"Points: {game_state.player_points}")
        print(f"Ingredients Collected: {len(game_state.ingredients_collected)}/{game_state.TOTAL_INGREDIENTS}")
        print(f"Virus Created: {'Yes' if game_state.virus_created else 'No'}")
        print(f"Municipalities Affected: {len(game_state.affected_municipalities)}")
        print(f"Active Agents: {len(game_state.agents)}")

    def display_menu(self):
        """
        Display available game actions.

        :return: User's chosen action
        """
        print("\nAvailable Actions:")
        print("1. Gather Ingredient")
        print("2. Create Virus")
        print("3. Deploy Agent")
        print("4. Administer Virus")
        print("5. End Turn")
        return input("Choose an action (1-5): ")