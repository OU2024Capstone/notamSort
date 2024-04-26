import math
import geopy.distance
from io import StringIO
from json import load
from os import path

# File name for database file
DATABASE_FILE_DIR = "database/Airports.json"
# radius of the earth in nautical miles
EARTH_RADIUS = 3443.89849
# conversion factor between miles and nautical miles
NM_TO_MILES = 1.151
database = None

class PointObject :
    """
    latitude: float value between (and including) -90 and 90
    longitude: float value between (and including) -180 and 180
    """
    latitude: float
    longitude: float


    def __init__(self, latitude = None, longitude = None) :
        
        if not(isinstance(latitude, (float, int))) :
            raise TypeError(f"Error: Latitude is of the wrong type, expected float or int and got {type(latitude)}")
        if not(isinstance(longitude, (float, int))) :
            raise TypeError(f"Error: Longitude is of the wrong type, expected float or int and got {type(longitude)}")
            
        if abs(latitude) > 90 :
            raise ValueError(f"Error: Incorrect value for latitude, must be between -90 and 90")
        if abs(longitude) > 180 :
            raise ValueError(f"Error: Incorrect value for longitude, must be between -180 and 180")

        else :
            # if we get this far without an error we have valid lat/long inputs
            self.latitude = latitude
            self.longitude = longitude

    @classmethod
    def from_airport_code(cls, message_log : StringIO, location = None) :
        """
        location: a string (IATA or ICAO code) to convert to a set of coordinates
        """

        if not(isinstance(location, str)) :
            raise TypeError(f"Error: Location is of the wrong type, expected str and got {type(location)}")
        else :
            try :
                output_location = get_valid_US_airport(location, message_log)
            except ValueError as err:
                raise err
            if output_location == None:
                raise TypeError(f"Error: The database was not able to find a result for the following location: {location}")

            else :
                latitude = output_location[0]
                longitude = output_location[1]
                return cls(latitude, longitude)

    def __str__(self) :
        return f"Latitude: {self.latitude}, Longitude: {self.longitude}"

def load_database_file() -> None:
        """
        Reads the local data base file and creates a dictionary from it.
        """
        global database

        if database is None:

            if not path.exists(DATABASE_FILE_DIR):
                raise FileNotFoundError(f"No database found! A file is expected at {DATABASE_FILE_DIR} relative to where this app was run.")

            file = open(DATABASE_FILE_DIR)
            database = load(file)
            database = database["features"]

            file.close()   

def get_valid_US_airport(user_input : str, message_log : StringIO) -> tuple:
        """ Get the first US airport that is found within the database 
            that matches the string supplied.

        Parameters
        ----------
        user_input : str
            String representing the airport code.

        message_log : StringIO
            Used to redirect all printed messages to the frontend.

        Returns
        -------
        tuple
            The latitude and longitude of the airport
        """

        if len(user_input) == 4 or len(user_input) == 3:
            for airport in database:
                # Get the two airport codes.
                # IDENT covers both IATA and the FAA identifiers
                airport_properties = airport["properties"]
                curr_airport_code_IATA_FAA = airport_properties["IDENT"]
                curr_airport_code_ICAO = airport_properties["ICAO_ID"]

                is_IATA_FAA_code = curr_airport_code_IATA_FAA is not None and curr_airport_code_IATA_FAA.upper() == user_input.upper()
                is_ICAO_code = curr_airport_code_ICAO is not None and curr_airport_code_ICAO.upper() == user_input.upper()
                
                # Was using the US_HIGH, US_LOW, etc. identifiers before, but some of the airports are mislabeled
                # For example, WA and OR airports could be labeled as PACIFIC airports. 
                # Some AK airports have both AK_HIGH an AK_LOW set to 0.
                # Instead of looking for every edge case, just check the two states that don't need to be included
                is_in_US_mainland = (airport_properties["COUNTRY"] == "UNITED STATES" 
                                     and not (airport_properties["STATE"] == "AK" or airport_properties["STATE"] == "HI")) 

                if is_in_US_mainland and (is_ICAO_code or is_IATA_FAA_code):
                    # coordinates contains a list of the longitude, latitude, and altitude
                    # Altitude is weirdly not used, however.
                    airport_lat = airport["geometry"]["coordinates"][1]
                    airport_long = airport["geometry"]["coordinates"][0]
                    return (airport_lat, airport_long)
                
                elif not is_in_US_mainland and (is_ICAO_code or is_IATA_FAA_code):
                    raise ValueError(f"Airport must be in the continental United States, got {user_input} instead.")

        else:
            raise ValueError(f"Airport code is expected to be in IATA, ICAO, or FAA forms, got {user_input} instead")
        
        return None

def get_distance(point_one: PointObject, point_two: PointObject) :
    """
    point_one: point from wich we start measuring the distance
    point_two: stopping point

    Returns the distance from one to two, in nautical miles
    """
    error_log = []
    if not(isinstance(point_one, PointObject)) :
        error_log.append(f"Error: point_one is of the wrong type, expected PointObject and got {type(point_one)}")
    if not(isinstance(point_two, PointObject)) :
        error_log.append(f"Error: point_two is of the wrong type, expected PointObject and got {type(point_two)}")
    
    if error_log :
        error_message = "\n".join(error_log)
        raise ValueError(error_message)

    point_one_coords = (point_one.latitude, point_one.longitude)
    point_two_coords = (point_two.latitude, point_two.longitude)

    distance = geopy.distance.great_circle(point_one_coords, point_two_coords).miles / NM_TO_MILES
        
    return distance


def get_bearing(point_one: PointObject, point_two: PointObject) -> float :
    """
    point_one: point from wich we start measuring the angle
    point_two: point at wich we end the angle

    Returns the bearing from one to two, in degrees
    """
    error_log = []
    if not(isinstance(point_one, PointObject)) :
        error_log.append(f"Error: point_one is of the wrong type, expected PointObject and got {type(point_one)}")
    if not(isinstance(point_two, PointObject)) :
        error_log.append(f"Error: point_two is of the wrong type, expected PointObject and got {type(point_two)}")
    
    if error_log :
        error_message = "\n".join(error_log)
        raise ValueError(error_message)

    # math.cos and sin uses radians
    # so we need to convert our lat/long coords into radians first
    # the immediate output doesnt need any conversion
    latitude_one_radians = math.radians(point_one.latitude)
    longitude_one_radians = math.radians(point_one.longitude)
    latitude_two_radians = math.radians(point_two.latitude)
    longitude_two_radians = math.radians(point_two.longitude)
    longitude_difference_radians = math.radians(point_two.longitude-point_one.longitude)

    x = (math.cos(latitude_two_radians) 
        * math.sin(longitude_difference_radians))
    
    product_one = (
        math.cos(latitude_one_radians) 
        * math.sin(latitude_two_radians)
    )
    product_two = (
        math.sin(latitude_one_radians) 
        * math.cos(latitude_two_radians) 
        * math.cos(longitude_difference_radians)
    )
    y = (product_one - product_two)
    
    bearing_radians = math.atan2(x, y)
    bearing = math.degrees(bearing_radians)

    # return the bearing angle in degrees to keep the units consistent
    return bearing


def get_next_point_geopy(point: PointObject, bearing: float, distance: float| int) -> PointObject :
    """
    point: point from wich we start measuring distance
    distance: target distance from the start in nautical miles
    bearing: heading in degrees

    Returns new lat/lon point a specified distance from the start, in degrees
    """
    error_log = []
    if not(isinstance(point, PointObject)) :
        error_log.append(f"Error: point_one is of the wrong type, expected PointObject and got {type(point)}")
    if not(isinstance(bearing, float)) :
        error_log.append(f"Error: bearing is of the wrong type, expected float and got {type(bearing)}")
    if not(isinstance(distance, (float, int))) :
        error_log.append(f"Error: distance is of the wrong type, expected float or int and got {type(distance)}")

    if error_log :
        error_message = "\n".join(error_log)
        raise ValueError(error_message)
    
    spacing = geopy.distance.distance(miles=distance*NM_TO_MILES)
    next_point_geopy = spacing.destination([point.latitude, point.longitude], bearing)
    next_point = PointObject(next_point_geopy.latitude, next_point_geopy.longitude)
    return next_point


# our implementation from:
# https://www.igismap.com/formula-to-find-bearing-or-heading-angle-between-two-points-latitude-longitude/
# results confirmed by https://www.fcc.gov/media/radio/find-terminal-coordinates
# both methods are off in the latitude by ~0.001 of the FCC calculator in different directions
# we currently only use the geopy implementation to find the next point not this one
def get_next_point_manual(point: PointObject, bearing: float, distance: float | int) -> PointObject :
    """
    point: point from wich we start measuring distance
    bearing: heading in degrees
    distance: target distance from the start in nautical miles

    Returns new lat/lon coordinate a specified distance from the start, in degrees
    """
    error_log = []
    if not(isinstance(point, PointObject)) :
        error_log.append(f"Error: point_one is of the wrong type, expected PointObject and got {type(point)}")
    if not(isinstance(bearing, float)) :
        error_log.append(f"Error: bearing is of the wrong type, expected float and got {type(bearing)}")
    if not(isinstance(distance, (float, int))) :
        error_log.append(f"Error: distance is of the wrong type, expected float or int and got {type(distance)}")

    if error_log :
        error_message = "\n".join(error_log)
        raise ValueError(error_message)
    

    # math.cos and sin uses radians
    # so we need to convert our lat/long coords into radians first
    point_longitude_radians = math.radians(point.longitude)
    point_latitude_radians = math.radians(point.latitude)
    bearing_radians = math.radians(bearing)

    next_latitude_radians = math.asin(
        (math.sin(point_latitude_radians) 
        * math.cos(distance / EARTH_RADIUS))
        + (math.cos(point_latitude_radians) 
        * math.sin(distance / EARTH_RADIUS) 
        * math.cos(bearing_radians))
    )

    x = (math.cos(distance / EARTH_RADIUS) 
        - (math.sin(point_latitude_radians) 
        * math.sin(next_latitude_radians)))
    
    y = (math.sin(bearing_radians) 
        * math.sin(distance / EARTH_RADIUS) 
        * math.cos(point_latitude_radians))

    next_longitude_radians = (point_longitude_radians + math.atan2(y,x))

    # then convert our output back to degrees
    next_latitude = math.degrees(next_latitude_radians)
    next_longitude = math.degrees(next_longitude_radians)
    next_point = PointObject(next_latitude, next_longitude)
    return next_point

# Initialize database
load_database_file()