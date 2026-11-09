from flask import Flask, jsonify, request
import uuid, os
from datetime import datetime, timezone, timedelta

import sqlite3

app = Flask(__name__)

db = os.environ.get("DB_PATH", "/data/alerts.db")
connection = sqlite3.connect(db)
cursor = connection.cursor()

connection.row_factory = sqlite3.Row

def iso(timestamp):
    return timestamp.isoformat(timespec="seconds").replace("+00:00", "Z")

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
        
        required = ["rule", "severity"]
        missing = [f for f in required if alert.get(f) in (None, "")]
        if missing:
            return jsonify(error=f"missing fields: {', '.join(missing)}"), 400
        
        cursor.execute(f"""
                       INSERT INTO alerts (
                        id,
                        rule,
                        severity,
                        confidence,
                        source_ip,
                        event_time,
                        received_at,
                        description
                        )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                       """, (alert["id"], alert["rule"], alert["severity"], alert.get("confidence"), alert.get("source_ip"), alert.get("event_time"), alert["received_at"], alert.get("description")))
        connection.commit()
        return jsonify(alert), 201
    except Exception as e:
        return jsonify(f"Unable to post alert {e}"), 500

# get alerts
@app.get("/alerts")
def get_alerts():
    try:
        alerts = connection.execute(
            "SELECT * FROM alerts ORDER BY received_at DESC"
        ).fetchall()
        return jsonify(alerts=[dict(r) for r in alerts]), 200
    except Exception as e:
        return jsonify(f"Unable to get alerts: {e}"), 500
    
# post a failed login
@app.post("/failed-logins")
def post_failed_logins():
    body = request.get_json()
    source_ip = body.get("source_ip")
    
    required = ["source_ip"]
    missing = [f for f in required if body.get(f) in (None, "")]
    if missing:
        return jsonify(error=f"missing fields: {', '.join(missing)}"), 400
    
    window = int(body.get("window_seconds", 60))
    now = datetime.now(timezone.utc)

    with connection:
        connection.execute(
            "INSERT INTO failed_logins (source_ip, received_at) VALUES (?, ?)",
            (source_ip, iso(now))
        )
        count = connection.execute(
            "SELECT COUNT(*) FROM failed_logins WHERE source_ip = ? AND received_at > ?",
            (source_ip, iso(now - timedelta(seconds=window)))
        ).fetchone()[0]
    return jsonify(source_ip=source_ip, count=count, window_seconds=window), 201

@app.get("/failed-logins")
def get_failed_logins():
    try:
        failed_logins = connection.execute(
            "SELECT * FROM failed_logins ORDER BY received_at DESC"
        ).fetchall()
        return jsonify(failed_logins=failed_logins), 200
    except Exception as e:
        return jsonify(f"Unable to get failed logins: {e}"), 500
    
@app.get("/audits")
def get_audits():
    try:
        audits = connection.execute(
            "SELECT * FROM audit_records ORDER BY received_at"
        ).fetchall()
        return jsonify(audits=audits), 200
    except Exception as e:
        return jsonify(f"Unable to get audit records"), 500
    
@app.post("/audits")
def post_audits():
    body = request.get_json()
    required = ["request_id", "method", "path", "status"]
    
    missing = [f for f in required if body.get(f) in (None, "")]
    if missing:
        return jsonify(error=f"missing fields: {', '.join(missing)}"), 400
    
    try:
        received_at = body.get("received_at") or iso(datetime.now(timezone.utc))
        cursor.execute(f"""
                        INSERT INTO audit_records (
                            request_id,
                            method,
                            path,
                            source_ip,
                            status,
                            received_at
                            )
                                VALUES (?, ?, ?, ?, ?, ?)
                        """, (body["request_id"], body["method"], body["path"], body.get("source_ip"), body["status"], received_at))
        connection.commit()
        return jsonify(id=cursor.lastrowid), 201
    except Exception as e:
        return jsonify(error=f"unable to post audit: {e}"), 500


# create tables on startup
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