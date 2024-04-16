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
from io import StringIO
import concurrent.futures

# link to the FAA API
FAA_API_ENTRYPOINT = "https://external-api.faa.gov/notamapi/v1/notams"
# spacing between the center of our notam requests in nautical miles
DEFAULT_PATH_STEP_SIZE_NM = 40
# max number of NOTAMs we can grab in one call
MAX_NOTAMS = 1000
# radius around the flight path to get NOTAMs
NOTAM_RADIUS = 25
# blank default parameters for the API
NOTAM_REQUEST_PARAMS = {
    "pageSize" : str(MAX_NOTAMS),
    "locationRadius" : str(NOTAM_RADIUS),
}
# geolocator API agent for coordinates
GEOLOCATOR = Nominatim(user_agent="notam_sort")

# client's credentials to the FAA API
credentials = None


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

def get_notams_at(request_location : PointObject, message_log : StringIO, additional_params = {}) -> list:
    """ 
    This function takes the notam request, requests the api for the notams, and then returns the output.
    request_latitude_longitude expects to be a PointObject object containing the parameters 'latitude' and 'longitude' and contain type float values
    """

    if not(isinstance(request_location, PointObject)):
        raise ValueError(f"Error: location is of invalid type, expected PointObject got {type(request_location)}")
    if not(isinstance(additional_params, dict)):
        raise ValueError(f"Error: additional_params is of invalid type, expected dict got {type(additional_params)}")

    NOTAM_REQUEST_PARAMS.update({"locationLatitude" : str(request_location.latitude)})
    NOTAM_REQUEST_PARAMS.update({"locationLongitude" : str(request_location.longitude)})
    NOTAM_REQUEST_PARAMS.update(additional_params)

    notam_list = []
    num_pages = 1
    current_page = 1
    while current_page <= num_pages :
        NOTAM_REQUEST_PARAMS.update({"pageNum" : str(current_page)})
        
        api_response = requests.get(url=FAA_API_ENTRYPOINT, params=NOTAM_REQUEST_PARAMS, headers=credentials)

        if api_response.status_code == 401:
            raise RuntimeError( f"HTTP 401 return code from FAA API. Are you authenticated?" )
        if api_response.status_code == 404:
            raise RuntimeError( f"HTTP 404 return code from FAA API. Has the URL moved? Accessed url \"{FAA_API_ENTRYPOINT}\"" )
        if api_response.status_code != 200:
            raise RuntimeError( f"Received non-HTTP 200 status code {api_response.status_code} from FAA API" )

        api_response_json = json.loads(api_response.text)

        # The FAA API often does not follow good HTTP response code practices. For
        # example, instead of returning an HTTP 400 Bad Request, the API will
        # respond with HTTP 200 but include a single message about what was wrong.
        # In these cases, we want to ensure that we fail appropriately.
        if "message" in api_response_json.keys() and len(api_response_json.keys()) == 1:
            raise RuntimeError( f"Received error message from FAA API: {api_response_json['message']}" )
        
        num_pages = api_response_json.get("totalPages")
        num_notams = api_response_json.get("totalCount")
        returned_notam_list = api_response_json.get("items")
        for notam in returned_notam_list:
            # Create a Notam object and append to the notam list. The Notam
            # class contains constants to get specific properties from the 
            # FAA api easily.
            notam_list.append(Notam(notam))
        
        print(f"Found {len(returned_notam_list)} notams at {request_location}", file=message_log)
        current_page += 1

    if (len(notam_list) < num_notams) :
        raise RuntimeError(f"Unable to retrieve all notams at {request_location}, expected {num_notams} and got {len(notam_list)}")
    return notam_list

def get_notams_from_point_list(point_list : list, message_log : StringIO) -> list:
    """
    point_list: The list of points that should be requested at

    Returns a list of notams at each point within point_list
    """
    
    # Create as many threads as needed until 
    # hitting the FAA API request per minute cap.
    # Essentially, every request will have its own thread.
    MAX_NUMBER_OF_THREADS = 50
    
    # Good code for debugging without overloading the FAA API
    # Note that the API may still return a 429 if you make two
    # separate queries too quickly.
    if len(point_list) > MAX_NUMBER_OF_THREADS:
        raise RuntimeError(f"Flight path is too long, attempting to send {len(point_list)} requests which is over the {MAX_NUMBER_OF_THREADS} request limit! Not all NOTAMs can be retrieved from the FAA API server!")


    thread_list = []
    # Creates a thread pool which executes until all of the threads are finished
    with concurrent.futures.ThreadPoolExecutor() as executor:

        # Create a thread for every request
        for point in point_list:
            thread = executor.submit(get_notams_at, point, message_log)
            thread_list.append(thread)


    notam_list = []
    # Each request has a list of notams, so concatenate each thread's output into the notam list
    while len(thread_list) > 0:
        thread_list_copy = thread_list.copy()

        for i in range(len(thread_list_copy)):
            request = thread_list_copy[i]

            # Only check threads that are done.
            # Remove threads after retrieving their data.
            if(request.done()):
                notam_list += request.result()
                thread_list.remove(request)
    
    return notam_list


# Currently returns the union of the depature and arrival airport notams.
# Looking to add in-flight notams and figure out a way to remove any intersecting notams.
# Additionally, the resulting list should be sorted.
def get_all_notams(departure_airport : str, arrival_airport : str, message_log : StringIO) -> list:
    """This is the starting point for the program, the front end should call this function.
        From there, this function should call other functions to 
        retrieve depature and arrival airport notams as well as in-flight notams,
        get these notams sorted, and return the sorted list back to the front end."""
    
    global credentials
    credentials = load_credentials()
    sort_list = NotamSort.RatingSort()
    
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

    point_list = get_points_between(departure_point, arrival_point, DEFAULT_PATH_STEP_SIZE_NM)

    # point_list currently has only the in-flight points.
    # Add the departure and arrival points.
    point_list.insert(0, departure_point)
    point_list.append(arrival_point)

    full_notam_list = get_notams_from_point_list(point_list, message_log)

    return sort_list.sort(full_notam_list, departure_airport, arrival_airport)


def get_points_between(point_one: PointObject, point_two: PointObject, spacing: float | int) -> list :
    """
    point_one: starting point
    point_two: ending point
    spacing: nautical miles between the center of each notam call
    message_log: StringIO object used to display printed messages to the frontend.

    Returns a list of points between the 2 points, does not include the end points
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
    point_list = []
    current_point = point_one
    for i in range(0, int((total_distance)-spacing), int(spacing)) :
        next_point = get_next_point_manual(current_point, bearing, spacing)
        point_list.append(next_point)
        current_point = next_point
        bearing = get_bearing(current_point, point_two)
    return point_list

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

def is_valid_US_airport_code(user_input : str, message_log : StringIO) -> bool:
    """Validates an ICAO/IATA US airport code using Nominatim.

    Parameters
    ----------
    user_input : str
        String representing the airport code.

    message_log : StringIO
        Used to redirect all printed messages to the frontend.

    Returns
    -------
    bool
        Whether user_input is a valid ICAO/IATA US airport code or not.
    """

    # Only accecpt 4-character or 3-character strings
    if(len(user_input) > 4 or len(user_input) < 3):
        print(f"'{user_input}' must be in either ICAO or IATA format.", file=message_log)
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
        print(f"Error: geocode failed with message '{error_message}'.", file=message_log)

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