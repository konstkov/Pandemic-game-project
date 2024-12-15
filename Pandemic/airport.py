import config
from weather import Weather
from geopy import distance


class Airport:
    # lisätty data, jottei tartte jokaista lentokenttää hakea erikseen
    def __init__(self, ident, active=False, data=None):
        self.ident = ident
        self.active = active

        # vältetään kauhiaa määrää hakuja
        if data is None:
            # find airport from DB
            sql = "SELECT ident, name, latitude_deg, longitude_deg FROM Airport WHERE ident='" + ident + "'"
            print(sql)
            cur = config.conn.cursor()
            cur.execute(sql)
            res = cur.fetchall()
            if len(res) == 1:
                # game found
                self.ident = res[0][0]
                self.name = res[0][1]
                self.latitude = float(res[0][2])
                self.longitude = float(res[0][3])
        else:
            self.name = data['name']
            self.latitude = float(data['latitude'])
            self.longitude = float(data['longitude'])

    def find_nearby_airports(self):
        # List to hold nearby airports
        nearby_airports = []

        # SQL query with placeholders for parameters
        sql = """
            SELECT ident, name, latitude_deg, longitude_deg
            FROM Airport
            WHERE latitude_deg BETWEEN %s AND %s
            AND longitude_deg BETWEEN %s AND %s
        """

        # Calculate bounds for latitude and longitude
        latitude_min = self.latitude - config.max_lat_dist
        latitude_max = self.latitude + config.max_lat_dist
        longitude_min = self.longitude - config.max_lon_dist
        longitude_max = self.longitude + config.max_lon_dist

        # Execute the query with parameters
        cur = config.conn.cursor()
        cur.execute(sql, (latitude_min, latitude_max, longitude_min, longitude_max))
        results = cur.fetchall()

        # Process the query results
        for r in results:
            if r[0] != self.ident:  # Exclude the current airport
                # Create data for the Airport instance
                data = {'name': r[1], 'latitude': r[2], 'longitude': r[3]}
                print("Found nearby airport:", data)

                # Create an Airport instance
                nearby_airport = Airport(r[0], False, data)

                # Calculate distance to the airport
                nearby_airport.distance = self.distanceTo(nearby_airport)

                # Check if the airport is within the maximum allowed distance
                if nearby_airport.distance <= config.max_distance:
                    # Add the airport to the list of nearby airports
                    nearby_airports.append(nearby_airport)

                    # Calculate CO2 consumption for reaching this airport
                    nearby_airport.co2_consumption = self.co2_consumption(nearby_airport.distance)

        return nearby_airports

    def fetchWeather(self, game):
        self.weather = Weather(self, game)
        return

    def distanceTo(self, target):

        coords_1 = (self.latitude, self.longitude)
        coords_2 = (target.latitude, target.longitude)
        dist = distance.distance(coords_1, coords_2).km
        return int(dist)

    def co2_consumption(self, km):
        consumption = config.co2_per_flight + km * config.co2_per_km
        return consumption
