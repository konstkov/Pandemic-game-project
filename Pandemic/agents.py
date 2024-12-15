from db_connection import DatabaseConnection


class AgentsModel:
    """
    Manages interactions with agents in the database.
    """

    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection

    def fetch_agents(self):
        """
        Fetch all available agents from the people table.

        :return: List of agent names
        """
        query = "SELECT People_name FROM people"
        agents = self.db.execute_query(query)
        return [agent['People_name'] for agent in agents]

    def get_available_agents(self, deployed_agents):
        """
        Get agents that have not been deployed yet.

        :param deployed_agents: List of already deployed agents
        :return: List of available agents
        """
        all_agents = self.fetch_agents()
        return [agent for agent in all_agents if agent not in deployed_agents]