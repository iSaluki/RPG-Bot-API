from flask import Flask, request, jsonify
import json
from pymongo import MongoClient
import urllib
from time import asctime
import logging

logging.basicConfig(filename="api.log", level=logging.DEBUG)
app = Flask(__name__)
client = MongoClient("mongodb://api:ASrBP1PUB6RUwlpk@rpg-data-shard-00-00.avgt0.mongodb.net:27017,rpg-data-shard-00-01.avgt0.mongodb.net:27017,rpg-data-shard-00-02.avgt0.mongodb.net:27017/rpg-db?ssl=true&replicaSet=atlas-6e05a9-shard-0&authSource=admin&retryWrites=true&w=majority")


#Old string
#mongodb+srv://api:"+urllib.parse.quote_plus("ASrBP1PUB6RUwlpk")+"@rpg-data.avgt0.mongodb.net/rpg-db?retryWrites=true&w=majority


db = client["rpg-db"]
PRODUCTION = True

# Emojis

x_emoji = "<:X_:833700097903689728>"

# Database Abstraction
# A collection of functions to get data from the database and to write to the database
def GetUser(user_id):
    logging.debug(f"{asctime()} GETUSER: passed in user_id = {user_id}")
    collection = db["users"]
    for user in collection.find({"user_id":user_id}):
        logging.debug(f"{asctime()} GETUSER: {user}")
        return user



def UpdateUser(user_id, new_vals):
    logging.debug(f"{asctime()} UPDATEUSER: passed in user_id = {user_id}, new_vals = {new_vals}")
    collection = db["users"]
    result = collection.update_one(
        {"user_id" : user_id},
        {"$set": new_vals},
        upsert=True)
    logging.debug(f"{asctime()} UPDATEUSER: new_vals = {new_vals}")


def GetLocation(user_id, _map, location):
    logging.debug(f"{asctime()} GETLOCATION: passed in user_id = {user_id}, map = {map}, location = {location}")
    collection = db[_map]
    for loc in collection.find({"location_id":location}):
        logging.debug(f"{asctime()} GETLOCATION: loc = {loc}")
    for meta in collection.find({"location_id":"meta"}):
        logging.debug(f"{asctime()} GETLOCATION: meta = {meta}")
    loc["type"] = meta["type"]
    loc["start_pos"] = meta["start_pos"]
    if meta["type"] == "grid":
        loc["width"] = meta["width"]
    return(loc)


def LocationDescription(user_id):
    logging.debug(f"{asctime()} LOCATIONDESCRIPTION: passed in user_id = {user_id}")
    user = GetUser(user_id)
    logging.debug(f"{asctime()} LOCATIONDESCRIPTION: user = {user}")
    loc = GetLocation(user_id, user["map"], user["location"])
    logging.debug(f"{asctime()} LOCATIONDESCRIPTION: loc = {loc}")
    return loc["name"]+": "+loc["description"]



# Health check for DigitalOcean
@app.route('/api/alive')
def HealthCheck():
    return "The API is functional"


@app.route('/api/get')
def get():
    pass


# This is the entry point when a command has been issued from the bot.
# Extract the command details from the supplied data and call the appropriate function.
# Send the reply back to the bot to be displayed to the user.
@app.route('/api/post', methods=["POST"])
def testpost():
    logging.debug(f"{asctime()} TESTPOST: started")
    user_request = request.get_json(force=True) 
    logging.debug(f"{asctime()} GETPOST: user_request = {user_request}")
    user_id = int(user_request["user"])
    command = user_request["command"].lower()
    argsIncluded = False
    if "args" in user_request:
        args = user_request["args"]
        argsIncluded = True


     notImplemented = x_emoji+" This feature has not yet been implemented"

    if command == "buy":
        reply = notImplemented
    elif command == "drop":
        reply = notImplemented
    elif command == "fight":
        reply = notImplemented
    elif command == "get":
        reply = notImplemented
    elif command == "inventory":
        reply = notImplemented
    elif command == "location":
        reply = LocationDescription(user_id)
    elif command == "move":
        reply = Move(user_id, args)
    elif command == "open":
        reply = notImplemented
    elif command == "sell":
        reply = notImplemented
    elif command == "trade":
        reply = notImplemented
    elif command == "use":
        reply = notImplemented
    else:
        reply = "I don't know how to "+command+" "+args

    if argsIncluded:
        dict_to_send = {"response":"OK", "command":user_request["command"], "args":user_request["args"], "reply":reply}
    else:
        dict_to_send = {"response":"OK", "command":user_request["command"], "reply":reply}
    logging.debug(f"{asctime()} GETPOST: dict_to_send = {dict_to_send}")
    return jsonify(dict_to_send)


# Process the move command.
# Make sure the desired move is possible.
# Move to that location and build the new location's description as the reply.
# If an invalid move has been made, build an appropriate reply.
def Move(user_id, args):
    logging.debug(f"{asctime()} MOVE: passed in user_id = {user_id}, args = {args}")

    user = GetUser(user_id)
    logging.debug(f"{asctime()} MOVE: user = {user}")

    loc = GetLocation(user_id, user["map"], user["location"])
    logging.debug(f"{asctime()} MOVE: loc = {loc}")

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
        
        logging.debug(f"{asctime()} MOVE: old location: {user['location']} direction: {direction} new location {new_loc}")

        # Update the user to show their new location
        new_val = {"location": new_loc}
        UpdateUser(user_id, new_val)

        reply = LocationDescription(user_id)

    else:
        reply = "That is not a valid move from here!"

    return reply

if PRODUCTION:
    pass
else:
    app.run(host='0.0.0.0', port=8080)
