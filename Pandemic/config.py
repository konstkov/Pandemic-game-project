import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables (e.g., from .env file)
load_dotenv()

# Game parameters
max_distance = 200
max_lat_dist = max_distance / 50
max_lon_dist = max_distance / 50

co2_initial = 0
co2_budget = 1000
co2_per_flight = 50
co2_per_km = 1

default_starting_point = "EFKE"
default_name = "Anna"

# Internal shared variables -- do not modify
conn = None

# Database connection setup
def init_db():
    global conn
    conn = mysql.connector.connect(
        host=os.getenv('HOST', 'localhost'),
        port=3306,
        database=os.getenv('DB_NAME', 'pandemic_updated'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASS', 'password'),
        autocommit=True
    )
