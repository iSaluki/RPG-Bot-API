from flask import Flask, request, jsonify
import json
app = Flask(__name__)


@app.route('/get')
def test():
    return 'Basic GET call'

@app.route('/post', methods=["POST"])
def testpost():
     input_json = request.get_json(force=True) 
     print(input_json)
     dictToSend = {"Response":"OK","Command":input_json["command"]}
     return jsonify(dictToSend)
     #dictToReturn = {'text':input_json['text']}
     #print("Recieved data:")
     #print(dictToReturn)
     #return jsonify(dictToReturn)



app.run()