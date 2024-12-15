import mysql.connector
from typing import Dict, Any


class DatabaseConnection:
    """
    A class to manage database connections with improved security and configuration.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize a database connection with configurable parameters.

        :param config: A dictionary containing database connection parameters
        """
        try:
            self.connection = mysql.connector.connect(
                host=config.get('host', '127.0.0.1'),
                port=config.get('port', 3306),
                database=config.get('', 'pandemic_updated'),
                user=config.get('user', 'root'),
                password=config.get('password', 'password'),
                autocommit=config.get('autocommit', True),
                collation=config.get('collation', 'utf8mb4_general_ci'),
                charset=config.get('charset', 'utf8mb4'),
                use_unicode=config.get('use_unicode', True)
            )
            self.cursor = self.connection.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Error connecting to database: {err}")
            raise

    def execute_query(self, query: str, params: tuple = None):
        """
        Execute a SQL query with optional parameters.

        :param query: SQL query to execute
        :param params: Optional tuple of parameters for parameterized query
        :return: Query results
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Query execution error: {err}")
            return []

    def close(self):
        """Close database connection and cursor."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()