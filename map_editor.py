#import pymongo
from pymongo import MongoClient
import datetime
import urllib
import pprint

client = MongoClient("mongodb+srv://api:"+urllib.parse.quote_plus("ASrBP1PUB6RUwlpk")+"@rpg-data.avgt0.mongodb.net/rpg-db?retryWrites=true&w=majority")
db = client["rpg-db"]
collection = db["map_tutorial"]

def Menu():
    print("\n\nWelcome to map manager.")
    print("===========================")
    print("\nChoose from the following options...")
    print("  A. Add new location.")
    print("  F. Find existing location and display it.")
    print("  U. Update existing location.")
    print("  D. Delete a location.")
    print("  Q. Quit the program.\n")
    choice = input("Please make a choice: ").upper()
    while len(choice) != 1 or choice not in "AFUDQ":
        choice = input("You must chose A, F, U, D or Q. What is your choice? ").upper()
    return choice

def AddNew():
    print("\n\nAdd a new location.")
    print("------------------")
    print("\nProvide a reponse for each of these location details...")
    id = input("What is the location's id? ")
    while not id.isdigit():
        id = input("The id should be a number. Enter the location id: ")
    name = input("What is the name of this location? ")
    while len(name) < 3:
        name = input("That doesn't look like a valid name. Enter their name: ")
    description = input("Provide a description for this location: ")
    while len(description) < 6:
        description = input("That's a bit short. Enter a description for this location: ")
    links = []
    #linkNo = 0
    link = "bob"
    while len(link) > 0:
        link = input(f"Which directions can I go from this location? (current:{links}). Enter to stop: ").lower()
        if link in ["n", "ne", "e", "se", "s", "sw", "w", "nw"]:
            links.append(link) #[str(linkNo)] = link
            #linkNo += 1
        elif len(link) > 0:
            print("Not a valid direction.")
    location = {
        "location_id":id,
        "name":name,
        "description":description,
        "links_to":links,
        }
    locationId = collection.insert_one(location).inserted_id

def Find():
    print("\n\nFind a location.")
    print("---------------")
    print("\nWhat is the location id for the location you'd like to view...")
    id = input("What is the locations's id? ")
    while not id.isdigit() and id.upper() != "ALL":
        id = input("The id should be a number. Enter the location id: ")
    if id.upper() == "ALL":
        for location in collection.find():
            pprint.pprint(location)
    else:
        id = int(id)
        for location in collection.find({"location_id":id}):
            pprint.pprint(location)

def Delete():
    print("\n\nDelete a location.")
    print("------------------")
    print("\nGive an id for the location you would like to delete...")
    id = input("What is the location's id? ")
    while not id.isdigit():
        id = input("The id should be a number. Enter the location id: ")
    id = int(id)
    for location in collection.find({"location_id":id}):
        pprint.pprint(location)
    confirm = input("Is this the location you would like to delete? ").upper()
    if confirm[0] == "Y":
        collection.delete_one({"_id":location['_id']})


quitApp = False
while not quitApp:
    choice = Menu()
    if choice == "A":
        AddNew()
    elif choice =="F":
        Find()
    elif choice == "D":
        Delete()
    elif choice == "Q":
        quitApp = True
