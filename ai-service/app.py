import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

TELEMETRY_SERVICE_URL = os.environ.get("TELEMETRY_SERVICE_URL", "http://telemetry-service:3000")

@app.route("/")
def home():
    try:
        response = requests.get(TELEMETRY_SERVICE_URL, timeout=5)
        telemetry_data = response.json()
        
        cpu = telemetry_data.get("cpu_usage", 0)
        mem = telemetry_data.get("memory_usage", 0)
        risk = telemetry_data.get("risk_index", 0)
        
        if risk > 80 or cpu > 90 or mem > 90:
            status = "CRITICAL"
            action = "Urgent: Scale resources or restart failing nodes immediately."
        elif risk > 50 or cpu > 70 or mem > 70:
            status = "WARNING"
            action = "Monitor closely: Resources are elevated. Optimize background processes."
        else:
            status = "HEALTHY"
            action = "Nominal: System operating within normal thresholds."
            
        return jsonify({
            "service": "AI Service",
            "status": "running",
            "telemetry": telemetry_data,
            "system_status": status,
            "recommended_actions": action,
            "efficiency": 95
        })
    except Exception as e:
        return jsonify({
            "service": "AI Service",
            "status": "error",
            "error": str(e),
            "system_status": "CRITICAL",
            "recommended_actions": "Unable to contact Telemetry Service. Check network connectivity."
        }), 500

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001)