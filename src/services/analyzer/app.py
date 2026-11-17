from flask import Flask, jsonify, request
import os

STORAGE_URL = os.environ.get("STORAGE_URL", "http://storage:8001")
BRUTE_FORCE_THRESHOLD = int(os.environ.get("BRUTE_FORCE_THRESHOLD", "5"))
BRUTE_FORCE_WINDOW_SECONDS = int(os.environ.get("BRUTE_FORCE_WINDOW_SECONDS", "60"))
EXFIL_BYTES = int(os.environ.get("EXFIL_BYTES", "104857600"))
SQLI_HIGH_CONFIDENCE = float(os.environ.get("HIGH_CONFIDENCE", "0.8"))
FAILED_LOGIN_EVENTS = set(os.environ.get("FAILED_LOGIN_EVENTS", "login_failed").split(","))


app = Flask(__name__)

@app.get("/healthz")
def healthz():
    return jsonify(ok=True)

def check_sqli(log):
    pass

def check_efil(log):
    pass

def check_brute_force(log):
    pass

@app.post("/analyze")
def analyze():
    log = request.get_json()
    return jsonify(log=log), 200
