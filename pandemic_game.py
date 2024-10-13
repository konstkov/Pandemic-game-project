import mysql.connector
import random #

connection = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    database='pandemic',
    user='konstantinkovalev',
    password='password',
    autocommit=False,
    collation='utf8mb4_general_ci',
    charset='utf8mb4',
    use_unicode=True
)

cursor = connection.cursor()


# Fetch ingredients from the database
def fetch_ingredients():
    cursor.execute("SELECT item_name FROM Inventory")
    return [row[0].encode('utf-8').decode('utf-8') for row in cursor.fetchall()]

# Fetch agents from the database
def fetch_agents():
    cursor.execute("SELECT People_name FROM people")
    return [row[0].encode('utf-8').decode('utf-8') for row in cursor.fetchall()]

import time
import sys
from colorama import Fore, Style, init

# Initialize colorama
init()

def slow_print(text, delay=0.05, color=Style.RESET_ALL):
    for char in text:
        sys.stdout.write(f"{color}{char}")
        sys.stdout.flush()
        time.sleep(delay)
    print(Style.RESET_ALL)  # Reset to default

# Game introduction with color and animation
def game_intro():
    slow_print("You have been hired to orchestrate this plan as the world has done us injustice", 0.05, Fore.RED)
    slow_print("and hasn't recognized our skill.", 0.05, Fore.RED)
    slow_print("First, you have to collect all 5 ingredients, then develop a virus.", 0.05, Fore.YELLOW)
    slow_print("Hire more people to help spread the virus across Finland, but remember:", 0.05)
    slow_print("You have a specific number of points.", 0.05, Fore.CYAN)
    slow_print("Gain points by completing missions and creating the virus,", 0.05, Fore.GREEN)
    slow_print("but you must not run out of points or you lose.", 0.05, Fore.RED)
    slow_print("Spread the virus throughout all municipalities of Finland,", 0.05, Fore.YELLOW)
    slow_print("or you will have failed the mission and be exiled/banished.", 0.05, Fore.MAGENTA)

game_intro()

import mysql.connector
import random


# fetch ingredients from the database
def fetch_ingredients():
    cursor.execute("select item_name from inventory")
    return [row[0].encode('utf-8').decode('utf-8') for row in cursor.fetchall()]

# fetch agents from the database
def fetch_agents():
    cursor.execute("select people_name from people")
    return [row[0].encode('utf-8').decode('utf-8') for row in cursor.fetchall()]

# fetch municipalities from the database
def fetch_municipalities():
    cursor.execute("select distinct municipality from airport where airport.iso_country = 'fi' "
                   "and municipality is not null and trim(municipality) != '';")
    return [row[0].encode('utf-8').decode('utf-8') for row in cursor.fetchall()]

# game variables to store the current state of the game
player_points = 10  # player's initial points
affected_municipalities = set()  # municipalities affected by the virus
ingredients_collected = set()  # ingredients collected by the player
virus_created = False  # flag to check if the virus has been created
agents = []  # list of agents deployed by the player

# constants for the game
total_ingredients = 5  # total number of ingredients required to create the virus
agent_cost = 5  # points required to deploy an agent
virus_cost = 10  # points required to create the virus
virus_points = 20  # points earned when affecting a municipality with the virus

# fetch data from the database
all_ingredients = fetch_ingredients()
all_agents = fetch_agents()
municipalities = fetch_municipalities()

# function to initialize or reset the game
def initialize_game():
    global player_points, affected_municipalities, ingredients_collected, virus_created, agents
    # reset all variables to their starting values
    player_points = 10
    affected_municipalities = set()
    ingredients_collected = set()
    virus_created = False
    agents = []
    print("game initialized!")  # message to indicate the game has started/reset

# function to display the current status of the player in the game
def display_status():
    print(f"\ncurrent points: {player_points}")  # show player's current points
    print(f"ingredients collected: {len(ingredients_collected)}/{total_ingredients}")  # number of ingredients collected
    print(f"virus created: {'yes' if virus_created else 'no'}")  # show if the virus has been created
    print(f"municipalities affected: {len(affected_municipalities)}")  # show how many municipalities are affected
    print(f"active agents: {len(agents)}")

# function to handle the player's turn and choice of action
def player_turn():
    display_status()  # display current game status
    # display the menu of actions for the player
    print("\n1. gather ingredients")
    print("2. create virus")
    print("3. deploy agent")
    print("4. administer virus")
    print("5. end turn")
    # get player's choice of action
    choice = input("choose an action: ")

    # execute the corresponding function based on the player's choice
    if choice == "1":
        gather_ingredients()  # option to gather ingredients
    elif choice == "2":
        create_virus()  # option to create the virus
    elif choice == "3":
        deploy_agent()  # option to deploy an agent
    elif choice == "4":
        administer_virus()  # option to administer the virus to a municipality
    elif choice == "5":
        return False  # end the player's turn
    else:
        print("invalid choice. please select a valid action.")  # handle invalid input
    return True  # return true to continue the game

# function to allow the player to gather ingredients
def gather_ingredients():
    global player_points, ingredients_collected  # access global variables
    if len(ingredients_collected) >= total_ingredients:
        print("you have already collected all ingredients.")  # no more ingredients to collect
        return

    # iterate through the list of ingredients and collect one that hasn't been collected yet
    for ingredient in all_ingredients:
        if ingredient not in ingredients_collected:  # check if the ingredient is already collected
            ingredients_collected.add(ingredient)  # add the ingredient to the set
            player_points += 5  # reward the player with 5 points
            print(f"you collected {ingredient}! +5 points")  # inform the player
            return  # exit after collecting one ingredient

    print("no more ingredients to collect.")  # no ingredients left to collect

# function to create the virus if the player has enough ingredients and points
def create_virus():
    global player_points, virus_created  # access global variables
    if virus_created:
        print("the virus has already been created.")  # virus creation can only happen once
        return
    if len(ingredients_collected) < total_ingredients:
        print("not enough ingredients to create the virus.")  # check if enough ingredients are collected
        return
    if player_points < virus_cost:
        print("not enough points to create the virus.")  # check if the player has enough points
        return

    # deduct points and mark the virus as created
    player_points -= virus_cost
    virus_created = True
    print(f"virus created successfully! -{virus_cost} points")  # inform the player

# function to deploy an agent if the player has enough points
def deploy_agent():
    global player_points, agents  # access global variables
    if player_points < agent_cost:
        print("not enough points to deploy an agent.")  # check if the player has enough points
        return

    # iterate through available agents and deploy one that hasn't been deployed yet
    for agent in all_agents:
        if agent not in [a["name"] for a in agents]:  # check if the agent is already deployed
            agents.append({"name": agent, "health": 100})  # add the agent with full health
            player_points -= agent_cost  # deduct points for deploying the agent
            print(f"agent {agent} deployed! -{agent_cost} points")  # inform the player
            return

    print("no more agents available to deploy.")  # no more agents left to deploy

# function to administer the virus to a municipality if possible
def administer_virus():
    global player_points, affected_municipalities  # access global variables
    if not virus_created:
        print("the virus hasn't been created yet.")  # check if the virus is ready
        return
    if not agents:
        print("no agents available to administer the virus.")  # check if agents are deployed
        return

    # list of municipalities that haven't been affected yet
    unaffected_municipalities = [m for m in municipalities if m not in affected_municipalities]

    if not unaffected_municipalities:
        print("all municipalities have been affected!")  # no more municipalities to affect
        return

    # display the list of unaffected municipalities for the player to choose from
    print("select a municipality to affect:")
    for i, municipality in enumerate(unaffected_municipalities):
        print(f"{i + 1}. {municipality}")

    # get the player's choice and affect the selected municipality
    choice = int(input("enter the number of the municipality: ")) - 1
    if 0 <= choice < len(unaffected_municipalities):
        municipality = unaffected_municipalities[choice]
        affected_municipalities.add(municipality)  # mark the municipality as affected
        player_points += virus_points  # reward the player with points
        print(f"{municipality} has been affected with a virus! +{virus_points} points")

        # decrease the health of all deployed agents
        for agent in agents:
            agent['health'] -= 20  # decrease health by a fixed amount
        # remove agents with health below or equal to 0
        agents[:] = [agent for agent in agents if agent['health'] > 0]
    else:
        print("invalid choice.")  # handle invalid input

# function to check if the player has won by affecting all municipalities
def check_win_condition():
    return len(affected_municipalities) == len(municipalities)  # check if all municipalities are affected

# main game loop function
def play_game():
    initialize_game()  # initialize/reset the game
    while True:
        if not player_turn():  # process player's turn
            break  # end the game if the player chooses to end their turn
        if check_win_condition():  # check if the player has won
            print("congratulations! you've affected all municipalities in finland with a virus!")
            break
        if player_points <= 0:  # check if the player has run out of points
            print("game over! you've run out of points.")
            break

# start the game
play_game()  # call the main game function to start the game