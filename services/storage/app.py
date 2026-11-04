from flask import Flask, jsonify, request
import uuid, os
from datetime import datetime, timezone

import sqlite3

app = Flask(__name__)

db = os.environ.get("DB_PATH", "/data/alerts.db")
connection = sqlite3.connect(db)
cursor = connection.cursor()

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
    try:
        alerts = cursor.fetchall()
        return jsonify(alerts=alerts), 200
    except Exception as e:
        return jsonify(f"Unable to get alerts: {e}"), 500

def create_tables():
    try:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                rule TEXT NOT NULL,
                severity TEXT NOT NULL,
                confidence REAL,
                source_ip TEXT,
                event_time TEXT,
                received_at TEXT NOT NULL,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS failed_logins (
                id INTEGER PRIMARY KEY,
                source_ip TEXT NOT NULL,
                received_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS failed_logins_ip_time
                ON failed_logins (source_ip, received_at);

            CREATE TABLE IF NOT EXISTS audit_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT NOT NULL,
                method TEXT,
                path TEXT,
                source_ip TEXT,
                status INTEGER,
                received_at TEXT NOT NULL
            );
            """
        )
        connection.commit()

    except Exception as e:
        print(f"Error while creating table {e}")

create_tables()