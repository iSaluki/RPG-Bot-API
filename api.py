from flask import Flask, request, jsonify
import json
from pymongo import MongoClient
import urllib

app = Flask(__name__)

#client = MongoClient("mongodb+srv://mb:"+urllib.parse.quote_plus("@ntholog3y")+"@cluster0.zl2rh.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
#db = client["contacts"]
#collection = db["people"]

client = MongoClient("mongodb+srv://discord:"+urllib.parse.quote_plus("79wXglvmonJBwVK0")+"@rpg-data.avgt0.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client["rpg-db"]


@app.route('/get')
def test():
    return 'You are in a forest surrounded by wolves. I hope you picked up the flaming torch?'

@app.route('/post', methods=["POST"])
def testpost():
     input_json = request.get_json(force=True) 
     user_id = int(input_json["user"])
     collection = db["users"]
     user = collection.find({"user_id":user_id})

     print(user)
     dictToSend = {"response":"OK","command":input_json["command"],"args":input_json["args"]}
     return jsonify(dictToSend)
     #dictToReturn = {'text':input_json['text']}
     #print("Recieved data:")
     #print(dictToReturn)
     #return jsonify(dictToReturn)



app.run()