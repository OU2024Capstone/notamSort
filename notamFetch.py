import requests
import json
import os
import sys
from geopy.geocoders import Nominatim
from geopy import exc
from dotenv import load_dotenv
from Notam import Notam
import NotamSort
from NavigationTools import *

# spacing between the center of our notam requests in nautical miles
DEFAULT_PATH_STEP_SIZE_NM = 40

GEOLOCATOR = Nominatim(user_agent="notam_sort")
# client's credentials to the FAA API
credentials = None
faa_api = "https://external-api.faa.gov/notamapi/v1/notams"

def load_credentials() -> dict:
    """Returns the client's credentials for querying the FAA's API. 
    
    Querying the FAA NOTAM API requires authorization. There are two components
    required--a client_id and a client_secret. We store these values in a .env
    file in the root directory. If running locally, it is required to set up
    these credentials in the .env file manually.

    Returns
    -------
    dict
        A dict containing client_id and client_secret.
    """

    if not os.path.exists('.env'):
        raise FileNotFoundError('.env file not found in root directory. Have you set up a .env file for credentials?')

    load_dotenv()

    client_id = os.getenv('client_id')
    client_secret = os.getenv('client_secret')

    missing_auth = []
    if not client_id:
        missing_auth.append( "client_id" )
    if not client_secret:
        missing_auth.append( "client_secret" )
    if missing_auth:
        raise RuntimeError( f"Missing required authorization credential(s) {', '.join( missing_auth )} in .env file! Have you set up your credentials locally?" )

    return {
        "client_id": client_id,
        "client_secret": client_secret,
    }

def get_notams_at(request_location : PointObject, additional_params = {}) -> list:
    """ 
    This function takes the notam request, requests the api for the notams, and then returns the output.
    request_latitude_longitude expects to be a PointObject object containing the parameters 'latitude' and 'longitude' and contain type float values
    """

    if not(isinstance(request_location, PointObject)):
        raise ValueError(f"Error: location is of invalid type, expected PointObject got {type(request_location)}")
    
    # This is our request template
    notam_request_parameters = {
        "pageSize" : "1000",
        "pageNum" : "1",
        "locationLatitude" : str(request_location.latitude),
        "locationLongitude" : str(request_location.longitude),
        "locationRadius" : "25",
    }

    notam_request_parameters.update( additional_params )

    api_response = requests.get(url=faa_api, params=notam_request_parameters, headers=credentials)

    if api_response.status_code == 401:
        raise RuntimeError( f"HTTP 401 return code from FAA API. Are you authenticated?" )
    if api_response.status_code == 404:
        raise RuntimeError( f"HTTP 404 return code from FAA API. Has the URL moved? Accessed url \"{faa_api}\"" )
    if api_response.status_code != 200:
        raise RuntimeError( f"Received non-HTTP 200 status code {api_response.status_code} from FAA API" )

    api_response_json = json.loads(api_response.text)

    # The FAA API often does not follow good HTTP response code practices. For
    # example, instead of returning an HTTP 400 Bad Request, the API will
    # respond with HTTP 200 but include a single message about what was wrong.
    # In these cases, we want to ensure that we fail appropriately.
    if "message" in api_response_json.keys() and len(api_response_json.keys()) == 1:
        raise RuntimeError( f"Received error message from FAA API: {api_response_json['message']}" )

    # Parsing data about dictionary.
    num_notams = api_response_json.get("pageSize")
    num_pages = api_response_json.get("pageNum")
    returned_notam_list = api_response_json.get("items")

    notam_list = []

    # Get all of the notams and place them inside of notam list.
    for notam in returned_notam_list:
        # Create a Notam object and append to the notam list. The Notam
        # class contains constants to get specific properties from the 
        # FAA api easily.
        notam_list.append(Notam(notam))
    
    print(f"Found {len(notam_list)} notams at {request_location}")

    return notam_list


# Currently returns the union of the depature and arrival airport notams.
# Looking to add in-flight notams and figure out a way to remove any intersecting notams.
# Additionally, the resulting list should be sorted.
def get_all_notams(departure_airport : str, arrival_airport : str) -> list:
    """This is the starting point for the program, the front end should call this function.
        From there, this function should call other functions to 
        retrieve depature and arrival airport notams as well as in-flight notams,
        get these notams sorted, and return the sorted list back to the front end."""
    
    global credentials
    credentials = load_credentials()
    sort_list = NotamSort.SimpleSort()
    
    error_log = []
    if not(isinstance(departure_airport, str)) :
        error_log.append(f"Error: departure_airport is of the wrong type, expected str and got {type(departure_airport)}")
    if not(isinstance(arrival_airport, str)) :
        error_log.append(f"Error: arrival_airport is of the wrong type, expected str and got {type(arrival_airport)}")
    if error_log :
        error_message = "\n".join(error_log)
        raise ValueError(error_message)
    
    departure_point = PointObject.from_airport_code(departure_airport)
    arrival_point = PointObject.from_airport_code(arrival_airport)

    departure_airport_notams = get_notams_at(departure_point)
    arrival_airport_notams = get_notams_at(arrival_point)

    middle_notams = get_notams_between(departure_point, arrival_point, DEFAULT_PATH_STEP_SIZE_NM)

    full_notam_list = (
        departure_airport_notams 
        + arrival_airport_notams 
        + middle_notams
    )

    return sort_list.sort(full_notam_list)


def get_notams_between(point_one: PointObject, point_two: PointObject, spacing: float | int) -> list :
    """
    point_one: starting point
    point_two: ending point
    spacing: nautical miles between the center of each notam call

    Returns a list of the notams between the 2 points, does not include the end points
    """
    error_log = []
    if not(isinstance(point_one, PointObject)) :
        error_log.append(f"Error: point_one is of the wrong type, expected PointObject and got {type(point_one)}")
    if not(isinstance(point_two, PointObject)) :
        error_log.append(f"Error: point_two is of the wrong type, expected PointObject and got {type(point_one)}")
    if not(isinstance(spacing, (float, int))) :
        error_log.append(f"Error: spacing is of the wrong type, expected float or int and got {type(spacing)}")
    if error_log :
        error_message = "\n".join(error_log)
        raise ValueError(error_message)

    total_distance = get_distance(point_one, point_two)
    
    bearing = get_bearing(point_one, point_two)
    
    # i acts as our mile-marker along the flight path
    # with a hard-coded spacing option we have issues with overlap around the end of the path
    # we could divide the distance by some max number of api calls instead
    middle_notams = []
    current_point = point_one
    for i in range(0, int((total_distance)-spacing), int(spacing)) :
        next_point = get_next_point_manual(current_point, bearing, spacing)
        middle_notams += get_notams_at(next_point)
        current_point = next_point
        bearing = get_bearing(current_point, point_two)
    return middle_notams


def save_to_file(output_file_name : str, notam_list: list) :
    if notam_list :
        output_file = open(output_file_name+".json", "w")
        for notam in notam_list :
            output_file.write(notam)
        output_file.close()
    else :
        print("No Notams Retrieved Yet")

# For testing purposes, this function will output any list of notams it is given.
def print_to_console(notam_list : list):
    for notam in notam_list:
        print(notam)

def is_valid_US_airport_code(user_input : str) -> bool:
    """Validates an ICAO/IATA US airport code using Nominatim.

    Parameters
    ----------
    user_input : str
        String representing the airport code.

    Returns
    -------
    bool
        Whether user_input is a valid ICAO/IATA US airport code or not.
    """

    # Only accecpt 4-character or 3-character strings
    if(len(user_input) > 4 or len(user_input) < 3):
        print(f"'{user_input}' must be in either ICAO or IATA format.")
        return False
    
    code_format = 'iata' if len(user_input) == 3 else 'icao'
    geocode_query = f"{user_input.upper()} Airport"
    geocoder_results = None
    airport = None

    # namedetails provides the ICAO/IATA code from the geocode results, which
    # are not returned by default. exactly_one is set to false because 
    # airport codes are not prioritzed in Nominatim, and we want to 
    # watch out for any cases where a non-airport location is the first
    # search result.
    try:
        geocoder_results = GEOLOCATOR.geocode(geocode_query, exactly_one=False, namedetails=True, country_codes="US" )
    except exc.GeopyError as error_message:
        print(f"Error: geocode failed with message '{error_message}'.")

    # Get only the locations that are classified as an aeroway with an 
    # ICAO/IATA code matching the user's input. If none exist, the input was
    # not a valid US airport code.
    # In Nominatim, all airports are classified as an aeroway.
    # casefold() => Used for case-insensitive string comparison.
    if geocoder_results is not None:
        airport = next(filter(lambda location: 
                            location.raw.get('class') =='aeroway' and 
                            location.raw.get('namedetails').get(code_format).casefold() == user_input.casefold(), 
                            geocoder_results), None)

    if airport is None:
        return False
    else:
        return True