class GameState:
    """
    Manages the state of the game, tracking various game parameters.
    """

    def __init__(self, initial_points=10):
        """
        Initialize game state with default or custom parameters.

        :param initial_points: Starting points for the player
        """
        self.player_points = initial_points
        self.affected_municipalities = set()
        self.ingredients_collected = set()
        self.virus_created = False
        self.agents = []

        # Game constants
        self.TOTAL_INGREDIENTS = 5
        self.AGENT_COST = 5
        self.VIRUS_COST = 10
        self.VIRUS_POINTS = 20

    def reset(self):
        """
        Reset the game state to initial conditions.
        """
        self.__init__()

    def can_create_virus(self):
        """
        Check if virus can be created based on ingredients and points.

        :return: Boolean indicating if virus creation is possible
        """
        return (len(self.ingredients_collected) >= self.TOTAL_INGREDIENTS and
                self.player_points >= self.VIRUS_COST and
                not self.virus_created)

    def can_deploy_agent(self):
        """
        Check if an agent can be deployed based on available points.

        :return: Boolean indicating if agent deployment is possible
        """
        return self.player_points >= self.AGENT_COST

    def is_game_over(self, total_municipalities):
        """
        Check game completion conditions.

        :param total_municipalities: Total number of municipalities
        :return: Game state (win, loss, or ongoing)
        """
        if self.player_points <= 0:
            return "loss"
        if len(self.affected_municipalities) == total_municipalities:
            return "win"
        return "ongoing"