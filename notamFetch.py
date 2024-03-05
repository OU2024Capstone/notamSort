import requests
import json
import os
import sys
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
from Notam import Notam
import NotamSort


# Querying the FAA NOTAM API requires authorization. There are two components
# required--a client_id and a client_secret. We store these values in a .env
# file in the root directory. If running locally, it is required to set up
# these credentials in the .env file manually.
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

FAA_AUTH = {
    "client_id": client_id,
    "client_secret": client_secret,
}

full_notam_list = []
faa_api = "https://external-api.faa.gov/notamapi/v1/notams"
GEOLOCATOR = Nominatim(user_agent="notam_sort")
LAT_KEY = "latitude"
LONG_KEY = "longitude"

# read these from a file then add to .gitignore
# this can be called anywhere doesnt have to be in the function call here
# credentials retrieved from external '.env' file located in root dir
credentials = {
    "client_id": os.getenv('client_id'),
    "client_secret": os.getenv('client_secret'),
}

def send_api_request(request_latitude_longitude : dict, additional_params={}) -> list:
    """ This function takes the notam request, requests the api for the notams,
    and then returns the list of notams.

    request_latitude_longitude expects to be a dict object containing the keys
    'latitude' and 'longitude' and contain type float values

    If you wish to pass additional HTTP parameters to the FAA API, add them to
    the dict additional_params. Note that any params with the same key will
    overwrite existing params.
    """
    
    # This is our request template
    notam_request_parameters = {
        "pageSize" : "1000",
        "pageNum" : "1",
        "locationLatitude" : str(request_latitude_longitude[LAT_KEY]),
        "locationLongitude" : str(request_latitude_longitude[LONG_KEY]),
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
    
    print(f"Found {len(notam_list)} notams at {request_latitude_longitude}")

    return notam_list


def get_notams_at(location: str | dict) -> list:
    """Given either an airport code as str or a dictionary containing the 'latitude' and 'longitude' of the notam request,
        this function returns a list of notams at that location.
        

        Several errors could be raised from this function:
        
        RuntimeError may occur if the inputted airport code is invalid.

        TypeError may occur if the function recieves arguments that are not of type 'str' or 'dict'. 
        May also occur if the dictionary keys 'latitude' or 'longitude' contain a value that is not of type 'float'
        
        KeyError may occur if the dictionary is missing either the 'latitude' or 'longitude' keys"""

    if isinstance(location, str):

        # Attempt to get the longitude and latitude of the airport.
        airport_info = GEOLOCATOR.geocode(location)

        # If the geolocator outputs None, then something has gone wrong.
        if(airport_info is None):
            raise RuntimeError(f"Invalid airport. {location} was not found.")

        request_latitude_longitude = {LAT_KEY: airport_info.latitude, LONG_KEY: airport_info.longitude}
            

    elif isinstance(location, dict):

        if(LAT_KEY in location.keys() and LONG_KEY in location.keys()):
            
            if(isinstance(location[LAT_KEY], float) and isinstance(location[LONG_KEY], float)):
                request_latitude_longitude = location
            
            else:
                raise TypeError(f"Latitude and Longitude expected type float, but got {type(location[LAT_KEY])} and {type(location[LONG_KEY])} instead.")

        else:
            raise KeyError("Dictionary keys are expected to be formatted as {" + f"'{LAT_KEY}': float, '{LONG_KEY}': float" + "}")

    else:
        raise TypeError(f"Unsupported input for location \"{location}\", expected type str or dict but got {type(location)} instead.")


    return send_api_request(request_latitude_longitude)


    # Currently returns the union of the depature and arrival airport notams.
    # Looking to add in-flight notams and figure out a way to remove any intersecting notams.
    # Additionally, the resulting list should be sorted.
def get_all_notams(departure_airport : str, arrival_airport : str) -> list:
    """This is the starting point for the program, the front end should call this function.
        From there, this function should call other functions to 
        retrieve depature and arrival airport notams as well as in-flight notams,
        get these notams sorted, and return the sorted list back to the front end."""
    
    sort_list = NotamSort.SimpleSort()

    departure_airport_notams = get_notams_at(departure_airport)

    arrival_airport_notams = get_notams_at(arrival_airport)

    return sort_list.sort(departure_airport_notams + arrival_airport_notams)


# probably doesnt work because the notam list isnt built
def save_to_file(output_file_name : str) :
    output_file = open(output_file_name+".json", "w")
    for notam in full_notam_list :
        output_file.write(notam)
    output_file.close()

# For testing purposes, this function will output any list of notams it is given.
def print_to_console(notam_list : list):
    for notam in notam_list:
        print(notam)
