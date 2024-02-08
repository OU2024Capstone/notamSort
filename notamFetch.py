import requests
import json
from geopy.geocoders import Nominatim

full_notam_list = []
faa_api = "https://external-api.faa.gov/notamapi/v1/notams"

# call me to populate and return the notam list
def get_notams(departure_airport, arrival_airport) :
    # do some sanitization on the input strings
    geolocator = Nominatim(user_agent="notam_sort")
    departure_airport_location = geolocator.geocode(departure_airport)
    arrival_airport_location = geolocator.geocode(arrival_airport)

    # read these from a file then add to .gitignore
    # this can be called anywhere doesnt have to be in the function call here
    credentials = {
        "client_id" : "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "client_secret" : "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    }

    faa_api_input = {
        "pageSize" : "100",
        "pageNum" : "1",
        "locationLongitude" : str(departure_airport_location.longitude),
        "locationLatitude" : str(departure_airport_location.latitude),
        "locationRadius" : "25",
    }

    api_result = requests.get(url=faa_api, params=faa_api_input , headers=credentials)
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
