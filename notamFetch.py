import requests
import json

outputDecoder = json.decoder.JSONDecoder

creds = {
    "client_id" : "bdffccee1a4141acade40174a7e53bc5",
    "client_secret" : "b5ea7326E4E1461a8e9fc1bcE108aD49",
}

input = {
    "pageSize" : "100",
    "pageNum" : "1",
    "domesticLocation" : "JFK ",
    "sortBy" : "featureType",
}


result = requests.get(url="https://external-api.faa.gov/notamapi/v1/notams", params=input , headers=creds)
output = result.text
status = result.status_code
print(status)
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
print(notamNum)
pageNum = dataDict.get("pageNum")
print(pageNum)
# gets a list of notams the size of the pageSize
notamData = dataDict.get("items")

for i in range(notamNum) :
    curNotam = notamData[i]
    curNotamProperties = curNotam.get("properties").get("coreNOTAMData").get("notam")
    curNotamText = curNotamProperties.get("text")
    print(curNotamText)
    print()