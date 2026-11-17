from flask import Flask, jsonify, request
import os
import re

STORAGE_URL = os.environ.get("STORAGE_URL", "http://storage:8001")
BRUTE_FORCE_THRESHOLD = int(os.environ.get("BRUTE_FORCE_THRESHOLD", "5"))
BRUTE_FORCE_WINDOW_SECONDS = int(os.environ.get("BRUTE_FORCE_WINDOW_SECONDS", "60"))
EXFIL_BYTES = int(os.environ.get("EXFIL_BYTES", "104857600"))
SQLI_HIGH_CONFIDENCE = float(os.environ.get("SQLI_HIGH_CONFIDENCE", "0.8"))
FAILED_LOGIN_EVENTS = set(os.environ.get("FAILED_LOGIN_EVENTS", "login_failed").split(","))

SQLI_PATTERNS = [
    (re.compile(r"'\s*(or|and)\s+'?\d+'?\s*=\s*'?\d+", re.I), 0.6, "tautology ('1'='1)"),
    (re.compile(r"\bunion\b\s+(all\s+)?\bselect\b", re.I),      0.6, "UNION SELECT"),
    (re.compile(r";\s*(drop|delete|insert|update|alter)\b", re.I), 0.6, "stacked query"),
    (re.compile(r"(--|#|/\*)", re.I),                           0.2, "SQL comment"),
    (re.compile(r"\b(sleep|benchmark|waitfor\s+delay)\s*\(", re.I), 0.5, "time-based"),
    (re.compile(r"\b(select|insert|update|delete|drop|union)\b", re.I), 0.1, "SQL keyword"),
]

app = Flask(__name__)

@app.get("/healthz")
def healthz():
    return jsonify(ok=True)

def calculate_sqli_confidence(text):
    score = 0.0
    hits = []
    for pattern, weight, label in SQLI_PATTERNS:
        if pattern.search(text):
            score += weight
            hits.append(label)
    return min(score, 1.0), hits


def check_sqli(log):
    details = log.get("details")
    if not details:
        return None
    confidence = calculate_sqli_confidence(details)
    score = confidence["score"]
    hits = confidence["hits"]

    if score < 0.3:
        return None
    if score >= SQLI_HIGH_CONFIDENCE:
        severity = "high"
    elif score >= 0.5:
        severity = "medium"
    else:
        severity = "low"
    
    source_ip = log.get("source_ip")
    event_time = log.get("timestamp")

    return {
        "rule": "sql_injection",
        "severity": severity,
        "confidence": round(confidence, 2),
        "source_ip": source_ip,
        "event_time": event_time,
        "description": f"SQL injection patterns: {', '.join(hits)}"
    }


def check_exfil(log):
    pass

def check_brute_force(log):
    pass

@app.post("/analyze")
def analyze():
    log = request.get_json()
    if log.get("bytes"):
        exfil_check = check_exfil(log)
    sqli_check = check_sqli(log)
    brute_force_check = check_brute_force(log)
    return jsonify(log=log), 200
