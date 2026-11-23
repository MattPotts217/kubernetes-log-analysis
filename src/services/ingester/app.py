from flask import Flask, jsonify
import os

app = Flask(__name__)

STORAGE_URL = os.environ.get("STORAGE_URL", "http://storage:8001")

@app.get("/healtz")
def healthz():
    return jsonify(ok=True)