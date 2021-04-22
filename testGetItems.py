from pymongo import MongoClient
import logging
from time import asctime

client = MongoClient("mongodb://api:ASrBP1PUB6RUwlpk@rpg-data-shard-00-00.avgt0.mongodb.net:27017,rpg-data-shard-00-01.avgt0.mongodb.net:27017,rpg-data-shard-00-02.avgt0.mongodb.net:27017/rpg-db?ssl=true&replicaSet=atlas-6e05a9-shard-0&authSource=admin&retryWrites=true&w=majority")
db = client["rpg-db"]

logging.basicConfig(level=logging.INFO)

def GetUser(user_id):
    logging.debug(f"{asctime()} GETUSER: passed in user_id = {user_id}")
    collection = db["users"]
    for user in collection.find({"user_id":user_id}):
        logging.debug(f"{asctime()} GETUSER: {user}")
        return user


def GetInventory(user_id):
    logging.debug(f"{asctime()} GETINVENTORY: passed in user_id = {user_id}")
    user_items = db["user_items"]
    items = db["items"]
    inv = []
    for user_item in user_items.find({"user_id":user_id, "status":"inventory"}):
        for item in items.find({"item_id":user_item["item_id"]}):
            inv.append({"item_id":item["item_id"], "description":item["description"], "gettable":item["gettable"], "universal":item["universal"]})
    return inv

def GetInventoryDescriptions(user_id):
    logging.debug(f"{asctime()} GETINVENTORY: passed in user_id = {user_id}")
    user_items = db["user_items"]
    items = db["items"]
    inv = []
    for user_item in user_items.find({"user_id":user_id, "status":"inventory"}):
        for item in items.find({"item_id":user_item["item_id"]}):
            inv.append(item["description"])
    return inv

def GetPlayerItemsAtLocation(user_id, _map, location):
    logging.debug(f"{asctime()} GETPLAYERITEMSATLOCATION: passed in user_id = {user_id}, _map = {_map}, location = {location}")
    user_items = db["user_items"]
    items = db["items"]
    user_items_here = []
    for user_item in user_items.find({"user_id":user_id, "status":"dropped", "map_name":_map, "location_id":location}):
        for item in items.find({"item_id":user_item["item_id"]}):
            user_items_here.append({"item_id":item["item_id"], "description":item["description"], "gettable":item["gettable"], "universal":item["universal"]})
    return user_items_here

def GetDefaultItemsAtLocation(_map, location):
    logging.debug(f"{asctime()} GETDEFAULTITEMSATLOCATION: passed in _map = {_map}, location = {location}")
    items = db["items"]
    default_items_here = []
    for item in items.find({"map_name":_map, "location_id":location}):
        default_items_here.append({"item_id":item["item_id"], "description":item["description"], "gettable":item["gettable"], "universal":item["universal"]})
    return default_items_here

def GetItems(user_id, _map, location):
    logging.debug(f"{asctime()} GETITEMS: passed in user_id = {user_id}, map_name = {_map}, location_id = {location}")
    user = GetUser(user_id)
    logging.info(f"User = {user}")
    collection = db["items"]

    # Get all the items in the user's inventory
    inv = GetInventory(user_id)

    #Find all the items that default to the current location
    items = {}
    for item in collection.find({"default_map":user["map_name"], "default_location":user["location_id"]}):
        if item["universal"]:
            items["item_id"] = item["item_id"]
            items["description"] = item["description"]
            items["gettable"] = item["gettable"]
    logging.info(f"Items found in location {items}")

    #Only keep the ones that the user hasn't already interacted with
    keep = {}
    for item in items:
        if item["item_id"] not in user["inventory"]:
            keep["item_id"] = item["item_id"]
            keep["description"] = item["description"]
            keep["gettable"] = item["gettable"]
    logging.info(f"Items being kept {keep}")

    # Add any items that the user has previously left here
    for user_items in user["inventory"]:
        if user_items["map_name"] == user["map_name"] and user_items["location_id"] == user["location_id"]:
            keep["item_id"] = user_items["item_id"]
            for item in collection.find({"item_id":user_items["user_id"]}):
                keep["description"] = item["description"]
                keep["gettable"] = item["gettable"]
    logging.info(f"Items being kept plus those previously left by the user {keep}")
    return keep

print(GetInventory(183240527649570816))
#print(GetItems(183240527649570816, "map_tutorial", 72))
