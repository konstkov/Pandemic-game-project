import json
import os
import mysql.connector
from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS

import config
from agents import AgentsModel
from db_connection import DatabaseConnection
from game_logic import GameLogic
from game_state import GameState
from ingredients import IngredientsModel
from municipalities import MunicipalitiesModel

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
db_config = {
    'host': os.environ.get('HOST', 'localhost'),
    'port': 3306,
    'database': os.environ.get('DB_NAME', 'pandemic_updated'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASS', 'password')
}

# Global game state and database connection
db_connection = DatabaseConnection(db_config)
ingredients_model = IngredientsModel(db_connection)
agents_model = AgentsModel(db_connection)
municipalities_model = MunicipalitiesModel(db_connection)

game_state = GameState()
game_logic = GameLogic(
    ingredients_model,
    agents_model,
    municipalities_model,
    game_state
)

# Database connection for fetching airport data
config.conn = mysql.connector.connect(
    host=os.environ.get('HOST'),
    port=3306,
    database=os.environ.get('DB_NAME'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASS'),
    autocommit=True
)

@app.route('/newgame',methods=['GET'])
def newgame():
    """
    Basically starts a new game, fetches airport data from the database
    and returns json response wit game state details and a list of active locations
    """

    game_state.reset()  # Ensure game state is reset for a new game
    # Fetch locations from the database
    cursor = config.conn.cursor()
    cursor.execute("SELECT name, municipality, latitude_deg, longitude_deg FROM airport WHERE iso_country = 'FI'")
    locations = cursor.fetchall()

    print("Fetched Locations: ", locations) #for debugging mostly, prints it in the console not very necessary imo
                                                #like checking where and what is being printed

    #BAsically converts the raw database query result (locations) into a list of dictionaries
    formatted_locations = [
        {
            "name": loc[0],
            "municipality": loc[1],
            "latitude": loc[2],
            "longitude": loc[3],
            "active": True  #  sets/marks all locations as active
        }
        for loc in locations
    ]

    # Construct the response
    response = {
        #supposed to add player_id but dont have time to resolve it
        "player_points": game_state.player_points,
        "ingredients_collected": len(game_state.ingredients_collected),
        "affected_municipalities": list(game_state.affected_municipalities),
        "virus_created": game_state.virus_created,
        "agents": game_state.agents,
        "location": formatted_locations
    }
    return response

@app.route('/gather-ingredient', methods=['GET'])
def gather_ingredient():
    """
    Gather an ingredient
    BAsically updates players points and the ingreidents they collected
    returns json response with updated game state or gives and error if no ingridients are available
    """
    ingredient = game_logic.gather_ingredient()

    if ingredient:
        return ({
            "ingredient": ingredient,
            "ingredients_collected": list(game_state.ingredients_collected),
            "points": game_state.player_points
        })
    else:
        return ({
            "message": "No more ingredients available",
            "ingredients_collected": list(game_state.ingredients_collected)
        }), 400

@app.route('/create_virus', methods=['GET'])
def create_virus():
    """
    Basically tries to create the virus if they are successfull deducts their points
    and again returns json response with updated game state or gives an error if
     they didnt gather enough ingreidents
    """
    success = game_logic.create_virus()
    if success:
        return ({
            'message': 'Virus created successfully',
            'points': game_state.player_points,
            'virus_created': game_state.virus_created
        })
    else:
        return ({'error': 'Cannot create virus'}), 400

@app.route('/deploy-agent', methods=['GET'])
def deploy_agent():
    """
    Deploy an agent using deploy_agent from gamelogic and
    updates the number of agents and your points
    and returns upd game state or error if no agent can be deployed i.e you got them all.
    """
    agent_name = game_logic.deploy_agent()

    if agent_name:
        return ({
            'message': f'Agent {agent_name} deployed successfully',
            'agents': game_state.agents,
            'points': game_state.player_points
        })
    else:
        return ({'error': 'Cannot deploy agent'}), 400


@app.route('/administer-virus', methods=['GET'])
def administer_virus():
    """
    Administer a virus to a specified municipality.
    check if the municipalitiy is already infected and virus is already made
    updates the affected municipality
    """
    data = request.get_json()
    municipality = data.get('municipality')

    if not municipality:
        return ({'error': 'Municipality not provided'}), 400

    success = game_logic.administer_virus(municipality)

    if success:
        return ({
            'message': f'Virus administered to {municipality}',
            'affected_municipalities': list(game_state.affected_municipalities),
            'points': game_state.player_points,
            'agents': game_state.agents
        })
    else:
        return ({'error': 'Cannot administer virus'}), 400


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)