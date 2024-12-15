from db_connection import DatabaseConnection


class MunicipalitiesModel:
    """
    Manages interactions with municipalities in the database.
    """

    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection

    def fetch_municipalities(self):
        """
        Fetch all municipalities in Finland from the airport table.

        :return: List of unique municipality names
        """
        query = """
        SELECT DISTINCT municipality 
        FROM airport 
        WHERE airport.iso_country = 'fi' 
        AND municipality IS NOT NULL 
        AND TRIM(municipality) != ''
        """
        municipalities = self.db.execute_query(query)
        return [municipality['municipality'] for municipality in municipalities]