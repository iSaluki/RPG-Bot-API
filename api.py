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
     dictToSend = {"response":"OK","command":input_json["command"],"args":input_json["args"]}
     return jsonify(dictToSend)
     #dictToReturn = {'text':input_json['text']}
     #print("Recieved data:")
     #print(dictToReturn)
     #return jsonify(dictToReturn)



app.run()