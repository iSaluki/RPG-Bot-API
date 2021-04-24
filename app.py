from flask import Flask, request, jsonify
import json
from pymongo import MongoClient
import urllib
from time import asctime
import logging
import os

logging.basicConfig(filename="api.log", level=logging.DEBUG)

PRODUCTION = True

app = Flask(__name__)

client = MongoClient("mongodb://api:ASrBP1PUB6RUwlpk@rpg-data-shard-00-00.avgt0.mongodb.net:27017,rpg-data-shard-00-01.avgt0.mongodb.net:27017,rpg-data-shard-00-02.avgt0.mongodb.net:27017/rpg-db?ssl=true&replicaSet=atlas-6e05a9-shard-0&authSource=admin&retryWrites=true&w=majority")
db = client["rpg-db"]

authToken = "eyJhbGciOiJQUzM4NCIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.MqF1AKsJkijKnfqEI3VA1OnzAL2S4eIpAuievMgD3tEFyFMU67gCbg-fxsc5dLrxNwdZEXs9h0kkicJZ70mp6p5vdv-j2ycDKBWg05Un4OhEl7lYcdIsCsB8QUPmstF-lQWnNqnq3wra1GynJrOXDL27qIaJnnQKlXuayFntBF0j-82jpuVdMaSXvk3OGaOM-7rCRsBcSPmocaAO-uWJEGPw_OWVaC5RRdWDroPi4YL4lTkDEC-KEvVkqCnFm_40C-T_siXquh5FVbpJjb3W2_YvcqfDRj44TsRrpVhk6ohsHMNeUad_cxnFnpolIKnaXq_COv35e9EgeQIPAbgIeg"

# Emojis
x_emoji = "<:X_:833700097903689728>"

# Authentication
# Checks the request came from an authorized source.
def Authenticate(authHeader):
    logging.debug(f"{asctime()} AUTHENTICATION: Starting")
    if authHeader == authToken:
        logging.debug(f"{asctime()} AUTHENTICATION: Approved")
        return True
    else:
        logging.critical(f"{asctime()} AUTHENTICATION: Rejected")
        return False

# Database Abstraction
# A collection of functions to get data from the database and to write to the database

# Check to see if this user already exists. If they don't, add them.
def UserCheck(user_id):
    logging.debug(f"{asctime()} USERCHECK: passed in user_id={user_id}")
    users = db["users"]
    if users.count_documents({"user_id":user_id}) == 0:
        logging.debug(f"{asctime()} USERCHECK: user_id={user_id} does not exist")
        users.insert_one({"user_id":user_id, "map_name":"map_tutorial", "location_id":51})


# Returns the details of the current user
def GetUser(user_id):
    logging.debug(f"{asctime()} GETUSER: passed in user_id={user_id}")
    users = db["users"]
    for user in users.find({"user_id":user_id}):
        logging.debug(f"{asctime()} GETUSER: {user}")
        return user


# Modifies the current user's details. new_vals is a dictionary with the changes/additions
def UpdateUser(user_id, new_vals):
    logging.debug(f"{asctime()} UPDATEUSER: passed in user_id={user_id}, new_vals={new_vals}")
    users = db["users"]
    result = users.update_one(
        {"user_id" : user_id},
        {"$set": new_vals},
        upsert=True)
    logging.debug(f"{asctime()} UPDATEUSER: SUCCESS")


# Gets the user's inventory and returns list of dicts of each item and it's details
# Compare to GetInventoryDescriptions
def GetInventory(user_id):
    logging.debug(f"{asctime()} GETINVENTORY: passed in user_id={user_id}")
    user_items = db["user_items"]
    items = db["items"]
    inv = []
    for user_item in user_items.find({"user_id":user_id, "status":"inventory"}):
        for item in items.find({"item_id":user_item["item_id"]}):
            inv.append({"item_id":item["item_id"], "description":item["description"], "emoji":item["emoji"], "gettable":item["gettable"], "universal":item["universal"]})
            logging.debug(f"{asctime()} GETINVENTORY: item = {item}")
    logging.debug(f"{asctime()} GETINVENTORY: returning {inv}")
    return inv


# Gets a list of inventory items and returns a list of their descriptions only
# Compare to GetInventory
def GetInventoryDescriptions(user_id):
    logging.debug(f"{asctime()} GETINVENTORY: passed in user_id={user_id}")
    user_items = db["user_items"]
    items = db["items"]
    inv = []
    for user_item in user_items.find({"user_id":user_id, "status":"inventory"}):
        for item in items.find({"item_id":user_item["item_id"]}):
            inv.append(item["emoji"]+" "+item["description"])
            logging.debug(f"{asctime()} GETINVENTORYDESCRIPTIONS: item={item}")
    logging.debug(f"{asctime()} GETINVENTORYDESCRIPTIONS: returning {inv}")
    return inv


# Get the items that the player has dropped at the given location
# Returns a list of dictionaries, one for each item. Full details returned
def GetPlayerItemsAtLocation(user_id, _map, location):
    logging.debug(f"{asctime()} GETPLAYERITEMSATLOCATION: passed in user_id={user_id}, _map={_map}, location={location}")
    user_items = db["user_items"]
    items = db["items"]
    user_items_here = []
    for user_item in user_items.find({"user_id":user_id, "status":"dropped", "map_name":_map, "location_id":location}):
        for item in items.find({"item_id":user_item["item_id"]}):
            user_items_here.append({"item_id":item["item_id"], "description":item["description"], "emoji":item["emoji"], "gettable":item["gettable"], "universal":item["universal"]})
            logging.debug(f"{asctime()} GETPLAYERITEMSATLOCATION: item={item}")
    logging.debug(f"{asctime()} GETPLAYERITEMSATLOCATION: returning {user_items_here}")
    return user_items_here


# Get the default items for a given map location
# Returns a list of dictionaries, one for each item. Full details returned
def GetDefaultItemsAtLocation(_map, location):
    logging.debug(f"{asctime()} GETDEFAULTITEMSATLOCATION: passed in _map={_map}, location={location}")
    items = db["items"]
    default_items_here = []
    for item in items.find({"map_name":_map, "location_id":location}):
        logging.debug(f"{asctime()} GETDEFAULTITEMSATLOCATION: item={item}")
        default_items_here.append({"item_id":item["item_id"], "description":item["description"], "emoji":item["emoji"], "gettable":item["gettable"], "universal":item["universal"]})
    logging.debug(f"{asctime()} GETDEFAULTITEMSATLOCATION: returning {default_items_here}")
    return default_items_here


# Get a list of objects that the user should see at this location. Take account of their inventory and what they have previously dropped.
# COMPARE: GetItemsForUserAtLocation - uses this function to help it build a list of items that the player should see.
# THIS: Simply returns a list of items that the user has previously dropped here
def GetPlayerItemsDroppedAtLocation(user_id, _map, location):
    logging.debug(f"{asctime()} GETPLAYERITEMSATDROPPEDLOCATION: passed in user_id={user_id}, _map={_map}, location={location}")
    user_items = db["user_items"]
    items = db["items"]
    user_items_here = []
    for user_item in user_items.find({"user_id":user_id, "status":"dropped", "map_name":_map, "location_id":location}):
        for item in items.find({"item_id":user_item["item_id"]}):
            user_items_here.append({"item_id":item["item_id"], "description":item["description"], "emoji":item["emoji"], "gettable":item["gettable"], "universal":item["universal"]})
    logging.debug(f"{asctime()} GETPLAYERITEMSATDROPPEDLOCATION: user_items_here={user_items_here}")
    return user_items_here


# Get a list of the items that a player shoudl see at this location.
# COMPARE: GetPlayerItemsDroppedAtLocation - returns the items that a pplayer dropped at the location
# THIS: Includes the items from GetPlayerItemsAtLocation, but also includes the default items at this location that the user has not already interacted with
def GetItemsForUserAtLocation(user_id, _map, location):
    default_items = GetDefaultItemsAtLocation(_map, location)
    logging.debug(f"{asctime()} GETPLAYERITEMSATLOCATION: default_items = {default_items}")
    user_items_here = GetPlayerItemsDroppedAtLocation(user_id, _map, location)
    logging.debug(f"{asctime()} GETPLAYERITEMSATLOCATION: user_items = {user_items}")
    inventory = GetInventory(user_id)
    logging.debug(f"{asctime()} GETPLAYERITEMSATLOCATION: inventory = {inventory}")

    for item in default_items:
        if item not in user_items and item not in inventory:
            user_items_here.append(item)
    
    return user_items_here


# Get details of the current location
def GetLocation(_map, location):
    logging.debug(f"{asctime()} GETLOCATION: passed in _map={_map}, location={location}")
    this_map = db[_map]
    for loc in this_map.find({"location_id":location}):
        logging.debug(f"{asctime()} GETLOCATION: loc = {loc}")
    for meta in this_map.find({"location_id":"meta"}):
        logging.debug(f"{asctime()} GETLOCATION: meta = {meta}")
    loc["type"] = meta["type"]
    loc["start_location"] = meta["start_location"]
    if meta["type"] == "grid":
        loc["width"] = meta["width"]
    return(loc)


# Get the description of the current location for the user
def LocationDescription(user_id, _map, location):
    logging.debug(f"{asctime()} LOCATIONDESCRIPTION: passed in _map={_map}, location={location}")
    loc = GetLocation(_map, location)
    logging.debug(f"{asctime()} LOCATIONDESCRIPTION: loc = {loc}")
    description = loc["name"]+": "+loc["description"]

    items_here = GetItemsForUserAtLocation(user_id, _map, location)
    logging.debug(f"{asctime()} LOCATIONDESCRIPTION: description={description} items_here={items_here}")   
    if len(items_here) > 0:
        for item in items_here:
            description += "\n" + item["emoji"] + " " + item["description"]
    logging.debug(f"{asctime()} LOCATIONDESCRIPTION: description={description}")   

    return description


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
    authHeader = request.headers.get('Authentication')
    authenticated = Authenticate(authHeader)
    logging.debug(f"{asctime()} SECURITY: Auth header sent")
    if authenticated:
        pass
        logging.debug(f"{asctime()} SECURITY: Auth header approved")
    else:
        return "Authentication Error"
        logging.critical(f"{asctime()} SECURITY: Auth header rejected")

    user_request = request.get_json(force=True) 
    logging.debug(f"{asctime()} GETPOST: user_request = {user_request}")
    user_id = int(user_request["user"])
    command = user_request["command"].lower()
    argsIncluded = False
    if "args" in user_request:
        args = user_request["args"]
        argsIncluded = True
    
    UserCheck(user_id)

    notImplemented = x_emoji+" This feature has not yet been implemented"
    if command == "buy":
        reply = notImplemented
    elif command == "drop":
        reply = notImplemented
    elif command == "fight":
        reply = notImplemented
    elif command == "search":
        reply = notImplemented
    elif command == "inventory":
        inventory = GetInventoryDescriptions(user_id)
        if len(inventory) == 0:
            reply = x_emoji+" Nothing in your inventory!"
            logging.debug(f"{asctime()} INVENTORY: Inventory empty, returning placeholder")
        else:
            reply = ""
            for item in inventory:
                reply += item + "\n"
    elif command == "location":
        reply = Location(user_id)
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
        reply = "Unknown command, "+command+" "+args

    if argsIncluded:
        dict_to_send = {"response":"OK", "command":user_request["command"], "args":user_request["args"], "reply":reply}
    else:
        dict_to_send = {"response":"OK", "command":user_request["command"], "reply":reply}
    logging.debug(f"{asctime()} GETPOST: dict_to_send = {dict_to_send}")
    return jsonify(dict_to_send)


# Process the location command.
# Get the user so we can extract their current location.
# Use the LocationDescription function to get the description for the user location.
def Location(user_id):
    logging.debug(f"{asctime()} LOCATION: passed in user_id={user_id}")

    user = GetUser(user_id)
    logging.debug(f"{asctime()} LOCATION: user={user}")

    description = LocationDescription(user_id, user["map_name"], user["location_id"])
    return description

# Process the search command.
# Find objects that the user can pickup in their current location
# And then pick them up
# To implement



# Process the move command.
# Make sure the desired move is possible.
# Move to that location and build the new location's description as the reply.
# If an invalid move has been made, build an appropriate reply.
def Move(user_id, args):
    logging.debug(f"{asctime()} MOVE: passed in user_id={user_id}, args={args}")

    user = GetUser(user_id)
    logging.debug(f"{asctime()} MOVE: user={user}")

    loc = GetLocation(user["map_name"], user["location_id"])
    logging.debug(f"{asctime()} MOVE: loc={loc}")

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
            new_loc = user["location_id"]
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
        
        logging.debug(f"{asctime()} MOVE: old location:{user['location_id']} direction:{direction} new location:{new_loc}")

        # Update the user to show their new location
        new_val = {"location_id": new_loc}
        UpdateUser(user_id, new_val)

        reply = LocationDescription(user_id, user["map_name"], new_loc)

    else:
        reply = x_emoji+"That is not a valid move from here!"
    return reply

if PRODUCTION:
    pass
else:
    app.run(host='0.0.0.0', port=8080)
