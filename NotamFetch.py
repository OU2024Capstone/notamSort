import time
import requests
import json
import os
import sys
from dotenv import load_dotenv
from Notam import Notam
import NotamSort
from NavigationTools import *
from io import StringIO
import concurrent.futures
import plotly.graph_objects as go
from datetime import datetime
figure = go.Figure()

# link to the FAA API
FAA_API_ENTRYPOINT = "https://external-api.faa.gov/notamapi/v1/notams"
# spacing between the center of our notam requests in nautical miles
DEFAULT_PATH_STEP_SIZE_NM = 40
# max number of NOTAMs we can grab in one call
MAX_NOTAMS = 1000
# radius around the flight path to get NOTAMs
NOTAM_RADIUS = 25
# max number of retries before quitting our program
MAX_API_ATTEMPTS = 3
# blank default parameters for the API
NOTAM_REQUEST_PARAMS = {
    "pageSize" : str(MAX_NOTAMS),
    "locationRadius" : str(NOTAM_RADIUS),
}

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

def get_notams_at(request_location : PointObject, request_radius : int, message_log : StringIO, additional_params = {}) -> set:
    """ 
    This function takes the notam request, requests the api for the notams, and then returns the output.
    request_latitude_longitude expects to be a PointObject object containing the parameters 'latitude' and 'longitude' and contain type float values
    """

    if not(isinstance(request_location, PointObject)):
        raise ValueError(f"Error: location is of invalid type, expected PointObject got {type(request_location)}")
    if not(isinstance(additional_params, dict)):
        raise ValueError(f"Error: additional_params is of invalid type, expected dict got {type(additional_params)}")

    # blank default parameters for the API
    NOTAM_REQUEST_PARAMS = {
        "pageSize" : str(MAX_NOTAMS),
        "locationRadius" : str(request_radius),
        "locationLatitude" : str(request_location.latitude),
        "locationLongitude" : str(request_location.longitude),
    }

    NOTAM_REQUEST_PARAMS.update(additional_params)

    # set() Will only contain unique elements.
    notam_set = set()
    num_pages = 1
    current_page = 1
    while current_page <= num_pages :
        NOTAM_REQUEST_PARAMS.update({"pageNum" : str(current_page)})
        
        api_response = requests.get(url=FAA_API_ENTRYPOINT, params=NOTAM_REQUEST_PARAMS, headers=credentials)

        if api_response.status_code == 401:
            raise RuntimeError( f"HTTP 401 return code from FAA API. Are you authenticated?" )
        if api_response.status_code == 404:
            raise RuntimeError( f"HTTP 404 return code from FAA API. Has the URL moved? Accessed url \"{FAA_API_ENTRYPOINT}\"" )
        if api_response.status_code == 429:
            return api_response.status_code
            raise RuntimeError( f"HTTP 429 return code from FAA API. Your request limit has been reached, please wait 1 minute and try again." )
        if api_response.status_code != 200:
            return api_response.status_code
            raise RuntimeError( f"Received non-HTTP 200 status code {api_response.status_code} from FAA API" )

        api_response_json = json.loads(api_response.text)

        # The FAA API often does not follow good HTTP response code practices. For
        # example, instead of returning an HTTP 400 Bad Request, the API will
        # respond with HTTP 200 but include a single message about what was wrong.
        # In these cases, we want to ensure that we fail appropriately.
        if "message" in api_response_json.keys() and len(api_response_json.keys()) == 1:
            raise RuntimeError( f"Received error message from FAA API: {api_response_json['message']}" )
        
        num_pages = api_response_json.get("totalPages")
        total_notams_count = api_response_json.get("totalCount")
        returned_notam_list = api_response_json.get("items")
        returned_notam_count = len(returned_notam_list)
        for notam in returned_notam_list:
            # Create a Notam object and append to the notam list. The Notam
            # class contains constants to get specific properties from the 
            # FAA api easily.
            notam_set.add(Notam(notam))
        
        print(f"Found {len(returned_notam_list)} notams at {request_location}", file=message_log)
        current_page += 1

    if (returned_notam_count < total_notams_count) :
        raise RuntimeError(f"Unable to retrieve all notams at {request_location}, expected {total_notams_count} and got {returned_notam_count}")
    return notam_set

def get_notams_from_point_list(point_list : list, request_radius : int, message_log : StringIO) -> list:
    """
    point_list: The list of points that should be requested at

    request_radius: The radius that requests are given when issued at a point

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
            thread = executor.submit(get_notams_at, point, request_radius, message_log)
            thread_list.append(thread)

    # We start off with a set to avoid duplicate NOTAMs, 
    # but will convert and return a list, as sets cannot be sorted.
    notam_set = set()
    attempts = 0
    is_api_refreshed = False
    # save the failed points for multiple attempts
    failed_point_list = []
    # Each request has a list of notams, so concatenate each thread's output into the notam list
    # each loop adds failed threads backs to the thread_list
    while len(thread_list) > 0:
        thread_list_copy = thread_list.copy()

        for i in range(len(thread_list_copy)):
            request = thread_list_copy[i]
            # Only check threads that are done.
            # Remove threads after retrieving their data.
            if(request.done()):
                result = request.result()
                # check for a valid return from the API
                # if the return is invalid we return the response code
                if (not isinstance(result, int)) :
                    notam_set.update(result)
                # if we get anything other than a list handle the response code appropriately
                elif (attempts < MAX_API_ATTEMPTS) :
                    if (len(failed_point_list) > 0) :
                        failed_point = failed_point_list.pop(i)
                        failed_point_list.insert(i, failed_point)
                    else :
                        failed_point = point_list.pop(i)
                        point_list.insert(i, failed_point)
                        failed_point_list.append(failed_point)
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        # special behavior for 429 response code
                        if (result == 429 and not is_api_refreshed) :
                            # wait for the API limit to refresh before calling it again
                            print(f"Maximum number of API calls made, please wait 60 seconds...", file=message_log)
                            time.sleep(60)
                            is_api_refreshed = True
                        # re-submit the thread
                        # TODO attempt limit for non-API call limit related fails not implemented
                        new_thread = executor.submit(get_notams_at, failed_point, request_radius, message_log)
                        thread_list.append(new_thread)
                else :
                    # if we go over the attempt limit
                    raise RuntimeError(f"Attempts to retry the failed API calls failed")
                # remove the checked thread
                thread_list.remove(request)
        attempts += 1

    build_map(point_list)
    
    return list(notam_set) #return as list to allow sorting

def find_min_step_size(airport_distance : float):
    """
    Parameters
    -----------
    airport_distance : float
        The distance between two airports. Used to find how far each request needs to be
        to ensure the requests don't result in a 429 error code from the FAA API.

    Return Value
    ---------
    The minimum step size needed to traverse the flight path in 50 requests.
    """
    
    MAX_IN_FLIGHT_REQUESTS = 48
    
    return math.ceil(airport_distance/MAX_IN_FLIGHT_REQUESTS)

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
    
    departure_point = PointObject.from_airport_code(message_log, departure_airport)
    arrival_point = PointObject.from_airport_code(message_log, arrival_airport)

    step_size = DEFAULT_PATH_STEP_SIZE_NM
    request_radius = NOTAM_RADIUS
    airport_distance = get_distance(departure_point, arrival_point)

    if(airport_distance >= 1960):
        step_size = find_min_step_size(airport_distance)
        # By default, the step size was 80% of the radius*2.
        # This results in an overlap of 20% between two given requests.
        # request_radius = (step_size*1.2)/2
        request_radius = math.floor(step_size*0.6)

    point_list = get_points_between(departure_point, arrival_point, step_size)

    # point_list currently has only the in-flight points.
    # Add the departure and arrival points.
    point_list.insert(0, departure_point)
    point_list.append(arrival_point)

    full_notam_list = get_notams_from_point_list(point_list, request_radius, message_log)

    #Iterate through the notams to find notams that have already ended
    for notam in full_notam_list.copy():
        today = datetime.utcnow()
        try:
            if(notam.effective_end != "PERM"):
                given_date = datetime.strptime(notam.effective_end, "%Y-%m-%dT%H:%M:%S.%fZ")
                if given_date <= today:
                    full_notam_list.remove(notam)
        except Exception as e:
            #If there is any format besides the date or a Permanent notam
            print(e)

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

    if get_valid_US_airport(user_input, message_log):
        return True
    else:
        return False


def build_map(point_list : list) :
    longitudes = [p.longitude for p in point_list]
    latitudes = [p.latitude for p in point_list]
    figure.add_trace(go.Scattergeo(
        lon=[*longitudes],
        lat=[*latitudes],
        mode = 'lines+markers',
        line = dict(width = 1,color = 'red'),
    ))

    figure.update_layout(
        showlegend=False,
        margin=dict(l=10,r=10,t=10,b=10),
        geo = dict(
            scope = 'north america',
            projection_type = 'azimuthal equal area',
            #projection_scale=2.25,
            resolution=50,
            center_lat=point_list[0].latitude,
            center_lon=point_list[0].longitude,
            showland = True,
            showcountries=True,
            landcolor = 'rgb(243, 243, 243)',
            countrycolor = 'rgb(160, 160, 160)',
        )
    )

def get_map() :
    # Get map
    return figure

def clear_map():
    # Reset the map
    global figure
    figure = go.Figure()