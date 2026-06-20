import os
import random
from flask import Flask, jsonify, Response
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Define Prometheus metrics
CPU_USAGE = Gauge('system_cpu_usage', 'CPU usage percentage')
MEMORY_USAGE = Gauge('system_memory_usage', 'Memory usage percentage')
RISK_INDEX = Gauge('system_risk_index', 'Custom system risk index')

@app.route("/")
def home():
    cpu = round(random.uniform(20.0, 80.0), 2)
    mem = round(random.uniform(30.0, 75.0), 2)
    risk = round((cpu + mem) / 2.0, 2)
    
    CPU_USAGE.set(cpu)
    MEMORY_USAGE.set(mem)
    RISK_INDEX.set(risk)
    
    return jsonify({
        "service": "Telemetry Service",
        "status": "running",
        "cpu_usage": cpu,
        "memory_usage": mem,
        "risk_index": risk,
        "region": os.environ.get("REGION", "india"),
        "app_env": os.environ.get("APP_ENV", "production")
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

@app.route("/metrics")
def metrics():
    cpu = round(random.uniform(20.0, 80.0), 2)
    mem = round(random.uniform(30.0, 75.0), 2)
    risk = round((cpu + mem) / 2.0, 2)
    CPU_USAGE.set(cpu)
    MEMORY_USAGE.set(mem)
    RISK_INDEX.set(risk)
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)