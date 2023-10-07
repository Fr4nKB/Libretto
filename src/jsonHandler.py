import sys, json

jsonFile = {}

#name of the json file to load in jsonFile (ext. excluded)
def loadJSON(name):
    global jsonFile

    try:
        file = open("./docs/"+name+".json", "r")
        jsonFile = json.load(file)
        file.close()
        return jsonFile
    except:
        print("Missing"+name+".json")
        sys.exit(1)

def saveJSON(name, contents):
    global jsonFile

    try:
        file = open("./docs/"+name+".json", "w")
        json.dump(contents, file)
        file.close()
    except:
        print("Some error occured while saving "+name+".json")
        sys.exit(1)