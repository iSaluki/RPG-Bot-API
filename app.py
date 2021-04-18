from flask import Flask, request, jsonify
import json
from pymongo import MongoClient
import urllib
import pprint

verbose = True

app = Flask(__name__)
client = MongoClient("mongodb+srv://discord:"+urllib.parse.quote_plus("79wXglvmonJBwVK0")+"@rpg-data.avgt0.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client["rpg-db"]

# Database Abstraction
# A collection of functions to get data from the database and to write to the database
def GetUser(user_id):
    collection = db["users"]
    for user in collection.find({"user_id":user_id}):
        if verbose:
            print("GETUSER:", user)
        return user


def UpdateUser(user_id, new_vals):
    collection = db["users"]
    result = collection.update_one(
        {"user_id" : user_id},
        {"$set": new_vals},
        upsert=True)
    if verbose:
        print("UPDATEUSER:", new_vals)


def GetLocation(user_id, _map, location):
    collection = db[_map]
    for loc in collection.find({"location_id":location}):
        if verbose:
            print("GETLOCATION: ", loc)
    for meta in collection.find({"location_id":"meta"}):
        if verbose:
            print("GETLOCATION:", meta)
    loc["type"] = meta["type"]
    loc["start_pos"] = meta["start_pos"]
    if loc["type"] == "grid":
        loc["width"] == meta["width"]
    return(loc)


def LocationDescription(user_id):
    user = GetUser(user_id)
    if verbose:
        print("LOCATIONDESCRIPTION:",user)
    loc = GetLocation(user_id, user["map"], user["location"])
    if verbose:
        print("LOCATIONDESCRIPTION:",loc)
    return loc["name"]+": "+loc["description"]


# Health check for DigitalOcean
@app.route('/alive')
def healthcheck():
    return "The API is functional"


@app.route('/get')
def get():
    user_id = int(request.args.get("user"))
#   print(user_id)
    user = GetUser(user_id)
    loc = GetLocation(user_id)

    collection = db[_map]
    for loc in collection.find({"location_id":loc}):
        print(loc["name"],loc["description"])
        
    return loc["description"]


# This is the entry point when a command has been issued from the bot.
# Extract the command details from the supplied data and call the appropriate function.
# Send the reply back to the bot to be displayed to the user.
@app.route('/post', methods=["POST"])
def testpost():
    user_request = request.get_json(force=True) 
    if verbose:
        print("GETPOST:", user_request)
    user_id = int(user_request["user"])
    command = user_request["command"].lower()
    args = user_request["args"]

    if command == "move":
        reply = Move(user_id, args)
    elif command == "get":
        reply = Get(user_id, args)
    else:
        reply = "I don't know how to "+command+" "+args

    dict_to_send = {"response":"OK","command":user_request["command"],"args":user_request["args"], "reply":reply}
    if verbose:
        print("GETPOST:", dict_to_send)
    return jsonify(dict_to_send)

# Process the move command.
# Make sure the desired move is possible.
# Move to that location and build the new location's description as the reply.
# If an invalid move has been made, build an appropriate reply.
def Move(user_id, args):
    user = GetUser(user_id)
    if verbose:
        print("MOVE:",user)
    loc = GetLocation(user_id, user["map"], user["location"])
    if verbose:
        print("MOVE:",loc)

    direction = args[0].lower()
    if direction in ["n", "north"]:
        direction = "n"
    elif direction in ["ne", "north east", "northeast"]:
        direction = "ne"
    elif direction in ["e", "east"]:
        direction = "e"
    elif direction in ["se", "south east", "southeast"]:
        direction = "se"
    elif direction in ["s", "south"]:
        direction = "s"
    elif direction in ["sw", "south west", "southwest"]:
        direction = "sw"
    elif direction in ["w", "west"]:
        direction = "w"
    elif direction in ["nw", "north west", "northwest"]:
        direction = "nw"
    
    if direction in loc["links_to"]:
        if loc["type"] == "grid":
            # Determine the new cell
            new_loc = user["location"]
            if direction == "n":
                new_loc -= loc["width"]
            elif direction == "ne":
                new_loc -= loc["width"] + 1
            elif direction == "e":
                new_loc += 1
            elif direction == "se":
                new_loc += loc["width"] + 1
            elif direction == "s":
                new_loc += loc["width"]
            elif direction == "sw":
                new_loc += loc["width"] - 1
            elif direction == "w":
                new_loc -= 1
            elif direction == "nw":
                new_loc -= loc["width"] - 1
        
        if verbose:
            print("MOVE: old location:", user["location"], "direction:", direction, "new location", new_loc)

        # Update the user to show their new location
        new_val = {"location": new_loc}
        UpdateUser(user_id, new_val)

        reply = LocationDescription(user_id)


    else:
        reply = "That is not a valid move from here!"

    return reply



    #collection = db["users"]
    #for user in collection.find({"user_id":user_id}):
    #    print(user["user_id"], user["map"])
    #    _map = user["map"]
    #    loc = user["location"]
        #d = user["_id"]

    #if loc == 1:
    #    loc = 2
    #else:
    #    loc = 1     
    #new_val = {"location": loc}
    #result = collection.update_one(
    #    {"user_id" : user_id},
    #    {"$set": new_val},
    #    upsert=True)
 

    #dictToReturn = {'text':input_json['text']}
    #print("Recieved data:")
    #print(dictToReturn)
    #return jsonify(dictToReturn)


# PLAYER MOVEMENT BACKEND (PSEUDO)
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
#    else:
#            respond to discord and say that you can't travel here OR that this location doesn't exist


#Leave both lines commented out for production with Gunicorn

#app.run(host='0.0.0.0', port=8080)
#app.run(host='localhost', port=8080)