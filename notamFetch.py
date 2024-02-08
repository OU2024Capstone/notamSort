import requests
import json
from geopy.geocoders import Nominatim

notamList = []

# call me to populate and return the notam list
def getNotams(depAP, arrAP) :
    # do some sanitization on the input strings
    geoLocator = Nominatim(user_agent="notam_sort")
    depAP = geoLocator.geocode(depAP)
    arrAP = geoLocator.geocode(arrAP)

    # read these from a file then add to .gitignore
    # this can be called anywhere doesnt have to be in the function call here
    creds = {
        "client_id" : "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "client_secret" : "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    }

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

    # turn the returned json into a dictionary
    dataDict = json.loads(output)

    # gets a list of notams the size of the page / number of notams
    notamNum = dataDict.get("pageSize")
    pageNum = dataDict.get("pageNum")
    notamData = dataDict.get("items")

    for i in range(notamNum) :
        curNotam = notamData[i]
        curNotamProperties = curNotam.get("properties").get("coreNOTAMData").get("notam")
        curNotamText = curNotamProperties.get("text")
        notamList.append(curNotamText)
    
    return notamList

# probably doesnt work because the notam list isnt built
def saveToFile(outputFileName) :
    outputFile = open(outputFileName+".json", "w")
    for notam in notamList :
        outputFile.write(notam)
    outputFile.close()

#getNotams("jfk", "dfw")
#saveToFile("output")
#print(notamList[1])