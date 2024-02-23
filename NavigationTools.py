import math
import geopy.distance
from geopy.geocoders import Nominatim

GEOLOCATOR = Nominatim(user_agent="notam_sort")
# radius of the earth in nautical miles
EARTH_RADIUS = 3443.89849
# conversion factor between miles and nautical miles
NM_TO_MILES = 1.151

class PointObject :
    """
    latitude: float value between (and including) -90 and 90
    longitude: float value between (and including) -180 and 180
    """
    latitude: float
    longitude: float


    def __init__(self, latitude = None, longitude = None) :
        error_log = []
        if not(isinstance(latitude, float)) :
            error_log.append(f"Error: latitude is of the wrong type, expected float and got {type(latitude)}")
        if not(isinstance(longitude, float)) :
            error_log.append(f"Error: longitude is of the wrong type, expected float and got {type(longitude)}")
            
        if abs(latitude) > 90 :
            error_log.append(f"Error: Incorrect value for latitude, must be between -90 and 90")
        if abs(longitude) > 180 :
            error_log.append(f"Error: Incorrect value for longitude, must be between -180 and 180")


        if error_log :
            error_message = "\n".join(error_log)
            raise ValueError(error_message)
        else :
            # if we get this far without an error we have valid lat/long inputs
            self.latitude = latitude
            self.longitude = longitude

    @classmethod
    def from_airport_code(cls, location = None) :
        """
        location: a string (KOKC airport code or address) to convert to a set of coordinates
        """
        if not(isinstance(location, str)) :
            raise ValueError(f"Error: location is of the wrong type, expected str and got {type(location)}")
        else :
            location_geocode = GEOLOCATOR.geocode(location)
            if location_geocode is None :
                raise RuntimeError(f"Invalid airport. {location} was not found.")
            else :
                latitude = location_geocode.latitude
                longitude = location_geocode.longitude
                return cls(latitude, longitude)



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
    latitude_difference_radians = abs(math.radians(point_two.latitude-point_one.latitude))

    x = (math.cos(longitude_two_radians) 
        * math.sin(latitude_difference_radians))
    
    product_one = (
        math.cos(longitude_one_radians) 
        * math.sin(longitude_two_radians)
    )
    product_two = (
        math.sin(longitude_one_radians) 
        * math.cos(longitude_two_radians) 
        * math.cos(latitude_difference_radians)
    )
    y = (product_one - product_two)
    
    bearing_radians = math.atan2(x, y)
    bearing = math.degrees(bearing_radians)

    # return the bearing angle in degrees to keep the units consistent
    return bearing


def get_next_point_geopy(point: PointObject, bearing: float, distance: float) -> PointObject :
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
    if not(isinstance(distance, float)) :
        error_log.append(f"Error: distance is of the wrong type, expected float and got {type(distance)}")

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
def get_next_point_manual(point: PointObject, bearing: float, distance: float) -> PointObject :
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
    if not(isinstance(distance, float)) :
        error_log.append(f"Error: distance is of the wrong type, expected float and got {type(distance)}")

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