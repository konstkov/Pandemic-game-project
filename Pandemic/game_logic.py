class GameLogic:
    """
    Manages the game's core logic and interactions between models and state.
    """

    def __init__(self, ingredients_model, agents_model, municipalities_model, game_state):
        """
        Initialize game logic with necessary components.

        :param ingredients_model: Ingredients database model
        :param agents_model: Agents database model
        :param municipalities_model: Municipalities database model
        :param game_state: Current game state
        """
        self.ingredients_model = ingredients_model
        self.agents_model = agents_model
        self.municipalities_model = municipalities_model
        self.game_state = game_state

    def gather_ingredient(self):
        """
        Collect an ingredient if possible.

        :return: Name of collected ingredient or None
        """
        all_ingredients = self.ingredients_model.fetch_ingredients()
        for ingredient in all_ingredients:
            if ingredient not in self.game_state.ingredients_collected:
                self.game_state.ingredients_collected.add(ingredient)
                self.game_state.player_points += 5
                return ingredient
        return None

    def create_virus(self):
        """
        Attempt to create a virus.

        :return: Boolean indicating virus creation success
        """

        print(self.game_state.can_create_virus())

        if self.game_state.can_create_virus():
            self.game_state.player_points -= self.game_state.VIRUS_COST
            self.game_state.virus_created = True
            return True
        return False

    def deploy_agent(self):
        """
        Deploy an agent if possible.

        :return: Name of deployed agent or None
        """
        if self.game_state.can_deploy_agent():
            available_agents = self.agents_model.get_available_agents(
                [agent['name'] for agent in self.game_state.agents]
            )
            if available_agents:
                agent_name = available_agents[0]
                self.game_state.agents.append({"name": agent_name, "health": 100})
                self.game_state.player_points -= self.game_state.AGENT_COST
                return agent_name
        return None

    def administer_virus(self, municipality):
        """
        Attempt to administer virus to a specific municipality.

        :param municipality: Name of municipality to affect
        :return: Boolean indicating virus administration success
        """
        if (self.game_state.virus_created and
                self.game_state.agents and
                municipality not in self.game_state.affected_municipalities):

            self.game_state.affected_municipalities.add(municipality)
            self.game_state.player_points += self.game_state.VIRUS_POINTS

            # Reduce agent health
            for agent in self.game_state.agents:
                agent['health'] -= 20

            # Remove agents with zero health
            self.game_state.agents = [
                agent for agent in self.game_state.agents if agent['health'] > 0
            ]

            return True
        return False