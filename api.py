from flask import Flask, request, jsonify
import json
from pymongo import MongoClient
import urllib
import pprint

app = Flask(__name__)

#client = MongoClient("mongodb+srv://mb:"+urllib.parse.quote_plus("@ntholog3y")+"@cluster0.zl2rh.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
#db = client["contacts"]
#collection = db["people"]

client = MongoClient("mongodb+srv://discord:"+urllib.parse.quote_plus("79wXglvmonJBwVK0")+"@rpg-data.avgt0.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client["rpg-db"]


@app.route('/get')
def get():
    user_id = int(request.args.get("user"))
    print(user_id)
    #user_id = int(input_json["user"])
    collection = db["users"]
    for user in collection.find({"user_id":user_id}):
        print(user["user_id"], user["map"])
        _map = user["map"]
        loc = user["location"]
    collection = db[_map]
    for loc in collection.find({"location_id":loc}):
        print(loc["name"],loc["description"])
        
    return loc["description"]

@app.route('/post', methods=["POST"])
def testpost():
    input_json = request.get_json(force=True) 
    user_id = int(input_json["user"])
    collection = db["users"]
    for user in collection.find({"user_id":user_id}):
        print(user["user_id"], user["map"])
        _map = user["map"]
        loc = user["location"]
        #d = user["_id"]

    if loc == 1:
        loc = 2
    else:
        loc = 1     
    new_val = {"location": loc}
    result = collection.update_one(
        {"user_id" : user_id},
        {"$set": new_val},
        upsert=True)
 

    dictToSend = {"response":"OK","command":input_json["command"],"args":input_json["args"]}
    return jsonify(dictToSend)
    #dictToReturn = {'text':input_json['text']}
    #print("Recieved data:")
    #print(dictToReturn)
    #return jsonify(dictToReturn)



#def move(user_id,moveTo):
#    input_json = request.get_json(force=True) 
#    user_id = int(input_json["user"])
#    collection = db["users"]

#    for user in collection.find({"user_id":user_id}):
#         loc = user["location"]
#       collection = db["map_tutorial"]
#    for locations in collection.find({"location_id":loc}):
#        allowedMove = location.linksTo
#    if moveTo is in allowedMove:
#            update db to moveTo
#            respond to discord and say the user has moved  



app.run()