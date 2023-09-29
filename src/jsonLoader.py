import sys, json

jsonFile = {}

#name of the json file to load in jsonFile (ext. excluded)
def loadJSON(name):
    global jsonFile

    try:
        file = open("./docs/"+name+".json", "r")
        jsonFile = json.load(file)
        file.close()
    except:
        print("Missing"+name+".json")
        sys.exit(1)
