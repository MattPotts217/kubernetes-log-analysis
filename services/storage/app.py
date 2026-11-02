from flask import Flask, jsonify, request
import uuid
from datetime import datetime, timezone

app = Flask(__name__)

# api health check endpoint
@app.get("/healthz")
def healthz():
    return jsonify(ok=True)

# post an alert
@app.post("/alerts")
def save_alert():
    try:
        alert = request.get_json()
        alert["id"] = str(uuid.uuid4())
        alert["received_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        return jsonify(alert), 201
    except:
        return jsonify("Unable to post alert"), 500

# get alerts
@app.get("/alerts")
def get_alerts():
    return jsonify(alerts=[]), 501