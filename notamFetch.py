import requests
import json
import os
import sys
from geopy.geocoders import Nominatim
from dotenv import load_dotenv

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

# call me to populate and return the notam list
def get_notams(departure_airport, arrival_airport) :
    # do some sanitization on the input strings
    geolocator = Nominatim(user_agent="notam_sort")
    departure_airport_location = geolocator.geocode(departure_airport)
    arrival_airport_location = geolocator.geocode(arrival_airport)

    faa_api_input = {
        "pageSize" : "100",
        "pageNum" : "1",
        "locationLongitude" : str(departure_airport_location.longitude),
        "locationLatitude" : str(departure_airport_location.latitude),
        "locationRadius" : "25",
    }

    api_result = requests.get(url=faa_api, params=faa_api_input , headers=FAA_AUTH)
    api_output = api_result.text
    api_status = api_result.status_code

    if api_status != 200 :
        print("fail")
        raise Exception("bad return code")

    # turn the returned json into a dictionary
    departure_airport_notam_dict = json.loads(api_output)

    # gets a list of notams the size of the page / number of notams
    num_notams = departure_airport_notam_dict.get("pageSize")
    num_pages = departure_airport_notam_dict.get("pageNum")
    departure_notam_list = departure_airport_notam_dict.get("items")

    for i in range(num_notams) :
        current_notam = departure_notam_list[i]
        # dig into the api response to get the important information
        current_notam_properties = current_notam.get("properties").get("coreNOTAMData").get("notam")
        current_notam_text = current_notam_properties.get("text")
        full_notam_list.append(current_notam_text)
    
    return full_notam_list

# probably doesnt work because the notam list isnt built
def save_to_file(output_file_name) :
    output_file = open(output_file_name+".json", "w")
    for notam in full_notam_list :
        output_file.write(notam)
    output_file.close()

# For testing purposes, this function will output any list of notams it is given.
def print_to_console(notam_list):
    for notam in notam_list:
        print(notam)