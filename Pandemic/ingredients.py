from db_connection import DatabaseConnection


class IngredientsModel:
    """
    Manages interactions with ingredients in the database.
    """

    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection

    def fetch_ingredients(self):
        """
        Fetch all ingredients from the Inventory table.

        :return: List of ingredient names
        """
        query = "SELECT Item_name FROM inventory"
        ingredients = self.db.execute_query(query)
        print(ingredients)
        return [ingredient['Item_name'] for ingredient in ingredients]

    def is_ingredient_collected(self, ingredient_name):
        """
        Check if a specific ingredient has already been collected.

        :param ingredient_name: Name of the ingredient
        :return: Boolean indicating collection status
        """
        return ingredient_name in self.fetch_ingredients()