from pymongo import MongoClient
import logging
from time import asctime

client = MongoClient("mongodb://api:ASrBP1PUB6RUwlpk@rpg-data-shard-00-00.avgt0.mongodb.net:27017,rpg-data-shard-00-01.avgt0.mongodb.net:27017,rpg-data-shard-00-02.avgt0.mongodb.net:27017/rpg-db?ssl=true&replicaSet=atlas-6e05a9-shard-0&authSource=admin&retryWrites=true&w=majority")
db = client["rpg-db"]

logging.basicConfig(level=logging.DEBUG)

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
            inv.append({"item_id":item["item_id"], "description":item["description"], "emoji":item["emoji"], "gettable":item["gettable"], "universal":item["universal"]})
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
            user_items_here.append({"item_id":item["item_id"], "description":item["description"], "emoji":item["emoji"], "gettable":item["gettable"], "universal":item["universal"]})
    return user_items_here

def GetDefaultItemsAtLocation(_map, location):
    logging.debug(f"{asctime()} GETDEFAULTITEMSATLOCATION: passed in _map = {_map}, location = {location}")
    items = db["items"]
    default_items_here = []
    for item in items.find({"map_name":_map, "location_id":location}):
        default_items_here.append({"item_id":item["item_id"], "description":item["description"], "emoji":item["emoji"], "gettable":item["gettable"], "universal":item["universal"]})
    return default_items_here

def GetItemsForUserAtLocation(user_id, _map, location):
    logging.debug(f"{asctime()} GETITEMSFORUSERATLOCATION: passed in user_id = {user_id}, map_name = {_map}, location_id = {location}")
    
    default_items = GetDefaultItemsAtLocation(_map, location)
    logging.debug(f"{asctime()} GETITEMSFORUSERATLOCATION: default_items = {default_items}")
    user_items = GetPlayerItemsAtLocation(user_id, _map, location)
    logging.debug(f"{asctime()} GETITEMSFORUSERATLOCATION: user_items = {user_items}")
    inventory = GetInventory(user_id)
    logging.debug(f"{asctime()} GETITEMSFORUSERATLOCATION: inventory = {inventory}")

    for item in default_items:
        if item not in user_items and item not in inventory:
            user_items.append(item)
    
    return user_items

#print(GetInventory(183240527649570816))
#print(GetItems(183240527649570816, "map_tutorial", 72))
'''
User Ids: 
183240527649570816  Seth
595321346498625536
834853116003745792
'''
