from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/testEndpoint")
def testEndpoint():
    return jsonify(ok=True)