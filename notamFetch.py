import requests
import json
from geopy.geocoders import Nominatim

# wow brian is the coolest mentor!

outputDecoder = json.decoder.JSONDecoder

geoLocator = Nominatim(user_agent="notam_sort")

creds = {
    "client_id" : "bdffccee1a4141acade40174a7e53bc5",
    "client_secret" : "b5ea7326E4E1461a8e9fc1bcE108aD49",
}

# get user input here
depAP = geoLocator.geocode("JFK")
arrAP = geoLocator.geocode("DFW")

input = {
    "pageSize" : "100",
    "pageNum" : "1",
    "locationLongitude" : str(depAP.longitude),
    "locationLatitude" : str(depAP.latitude),
    "locationRadius" : "25",
}


result = requests.get(url="https://external-api.faa.gov/notamapi/v1/notams", params=input , headers=creds)
output = result.text
status = result.status_code
#print(output)

if status != 200 :
    print("fail")
    raise Exception("bad return code")

outputFile = open("output.json", "w")
outputFile.write(output)
outputFile.close

outputFile = open("output.json", "r")
dataDict = json.load(outputFile)
outputFile.close()

notamNum = dataDict.get("pageSize")
pageNum = dataDict.get("pageNum")
# gets a list of notams the size of the pageSize
notamData = dataDict.get("items")

for i in range(notamNum) :
    curNotam = notamData[i]
    curNotamProperties = curNotam.get("properties").get("coreNOTAMData").get("notam")
    curNotamText = curNotamProperties.get("text")
    print(curNotamText)
    print()
