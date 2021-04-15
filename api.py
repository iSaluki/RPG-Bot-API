from flask import Flask, request, jsonify
app = Flask(__name__)


@app.route('/')
def test():
    return 'Basic API call'

@app.route('/post', methods=["POST"])
def testpost():
     input_json = request.get_json(force=True) 
     dictToReturn = {'text':input_json['text']}
     print("Recieved data:")
     print(dictToReturn)
     return jsonify(dictToReturn)

app.run()