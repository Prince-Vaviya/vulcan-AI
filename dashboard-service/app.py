import os
import requests
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

AI_SERVICE_URL = os.environ.get("AI_SERVICE_URL", "http://ai-service:3001")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VulcanAI - Observability Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Outfit', sans-serif;
            background: radial-gradient(circle at top right, #111827, #030712);
        }
        .glass-card {
            background: rgba(17, 24, 39, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
    </style>
</head>
<body class="text-gray-100 min-h-screen pb-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        <!-- Header -->
        <header class="flex justify-between items-center mb-8 border-b border-gray-800 pb-5">
            <div class="flex items-center space-x-3">
                <span class="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-red-500 via-orange-500 to-yellow-500 bg-clip-text text-transparent">
                    VULCAN AI
                </span>
                <span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-500/10 text-red-400 border border-red-500/20">
                    DevOps Showcase
                </span>
            </div>
            <div>
                <button onclick="fetchData()" class="px-4 py-2 bg-gradient-to-r from-orange-500 to-red-600 hover:from-orange-600 hover:to-red-700 text-white font-semibold rounded-lg shadow-md transition-all duration-300 text-sm">
                    Refresh Stats
                </button>
            </div>
        </header>

        <!-- Status Banner -->
        <div id="status-card" class="mb-8 p-6 rounded-2xl glass-card border-l-4 border-gray-500 flex flex-col md:flex-row md:items-center md:justify-between transition-all duration-500">
            <div>
                <h2 class="text-lg font-semibold text-gray-300">System Evaluation Status</h2>
                <p id="system-status" class="text-3xl font-black mt-1 text-gray-400">LOADING...</p>
            </div>
            <div class="mt-4 md:mt-0 text-left md:text-right max-w-xl">
                <p class="text-xs text-gray-400 uppercase tracking-wider">Recommended Action</p>
                <p id="system-action" class="text-sm font-medium text-gray-200 mt-1">Analyzing system metrics...</p>
            </div>
        </div>

        <!-- Metric Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <!-- CPU -->
            <div class="glass-card p-6 rounded-2xl">
                <h3 class="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-2">CPU Usage</h3>
                <div class="flex items-baseline space-x-2">
                    <span id="cpu-val" class="text-5xl font-extrabold text-white">--</span>
                    <span class="text-gray-400 font-semibold">%</span>
                </div>
                <div class="mt-4 h-20">
                    <canvas id="cpuChart"></canvas>
                </div>
            </div>

            <!-- Memory -->
            <div class="glass-card p-6 rounded-2xl">
                <h3 class="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-2">Memory Usage</h3>
                <div class="flex items-baseline space-x-2">
                    <span id="mem-val" class="text-5xl font-extrabold text-white">--</span>
                    <span class="text-gray-400 font-semibold">%</span>
                </div>
                <div class="mt-4 h-20">
                    <canvas id="memChart"></canvas>
                </div>
            </div>

            <!-- Risk Index -->
            <div class="glass-card p-6 rounded-2xl">
                <h3 class="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-2">Risk Index</h3>
                <div class="flex items-baseline space-x-2">
                    <span id="risk-val" class="text-5xl font-extrabold text-white">--</span>
                    <span class="text-gray-400 font-semibold">/100</span>
                </div>
                <div class="mt-4 h-20">
                    <canvas id="riskChart"></canvas>
                </div>
            </div>
        </div>

        <!-- System Payload & Metadata -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Details -->
            <div class="glass-card p-6 rounded-2xl">
                <h3 class="text-lg font-bold mb-4 border-b border-gray-800 pb-2">Service Discovery</h3>
                <div class="space-y-4">
                    <div class="flex justify-between items-center p-3 rounded-lg bg-gray-900/50">
                        <div>
                            <p class="font-semibold text-sm">Telemetry Service</p>
                            <p class="text-xs text-gray-500">Port 3000</p>
                        </div>
                        <span id="telemetry-badge" class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-gray-800 text-gray-400">Offline</span>
                    </div>
                    <div class="flex justify-between items-center p-3 rounded-lg bg-gray-900/50">
                        <div>
                            <p class="font-semibold text-sm">AI Engine Service</p>
                            <p class="text-xs text-gray-500">Port 3001</p>
                        </div>
                        <span id="ai-badge" class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-gray-800 text-gray-400">Offline</span>
                    </div>
                    <div class="flex justify-between items-center p-3 rounded-lg bg-gray-900/50">
                        <div>
                            <p class="font-semibold text-sm">Dashboard Web Portal</p>
                            <p class="text-xs text-gray-500">Port 3002</p>
                        </div>
                        <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-green-500/10 text-green-400 border border-green-500/20">Online</span>
                    </div>
                </div>
            </div>

            <!-- JSON payload -->
            <div class="glass-card p-6 rounded-2xl flex flex-col">
                <h3 class="text-lg font-bold mb-4 border-b border-gray-800 pb-2">Raw Metrics payload</h3>
                <pre id="raw-json" class="flex-grow p-4 rounded-xl bg-black/60 text-emerald-400 text-xs overflow-x-auto font-mono select-all max-h-60">Waiting for data...</pre>
            </div>
        </div>
    </div>

    <script>
        function createChart(canvasId, color) {
            const ctx = document.getElementById(canvasId).getContext('2d');
            return new Chart(ctx, {
                type: 'line',
                data: {
                    labels: Array(10).fill(''),
                    datasets: [{
                        data: Array(10).fill(0),
                        borderColor: color,
                        borderWidth: 2,
                        pointRadius: 0,
                        fill: false,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { display: false },
                        y: { display: false, min: 0, max: 100 }
                    }
                }
            });
        }

        const cpuChart = createChart('cpuChart', '#f97316');
        const memChart = createChart('memChart', '#3b82f6');
        const riskChart = createChart('riskChart', '#ef4444');

        function pushChartValue(chart, val) {
            chart.data.datasets[0].data.shift();
            chart.data.datasets[0].data.push(val);
            chart.update();
        }

        async function fetchData() {
            try {
                const res = await fetch('/api/data');
                const result = await res.json();
                
                document.getElementById('raw-json').textContent = JSON.stringify(result, null, 2);
                
                if (result.status === 'error') {
                    setErrorState(result.error);
                    return;
                }
                
                const aiData = result.ai_data || {};
                const telemetry = aiData.telemetry || {};
                const cpu = telemetry.cpu_usage || 0;
                const mem = telemetry.memory_usage || 0;
                const risk = telemetry.risk_index || 0;
                
                document.getElementById('cpu-val').textContent = cpu;
                document.getElementById('mem-val').textContent = mem;
                document.getElementById('risk-val').textContent = risk;

                pushChartValue(cpuChart, cpu);
                pushChartValue(memChart, mem);
                pushChartValue(riskChart, risk);

                const status = aiData.system_status || 'UNKNOWN';
                const action = aiData.recommended_actions || 'No recommendation.';
                
                const banner = document.getElementById('status-card');
                const statusTxt = document.getElementById('system-status');
                const actionTxt = document.getElementById('system-action');
                
                statusTxt.textContent = status;
                actionTxt.textContent = action;
                
                if (status === 'HEALTHY') {
                    banner.className = 'mb-8 p-6 rounded-2xl glass-card border-l-4 border-green-500 flex flex-col md:flex-row md:items-center md:justify-between transition-all duration-500 bg-green-950/10';
                    statusTxt.className = 'text-3xl font-black mt-1 text-green-400';
                } else if (status === 'WARNING') {
                    banner.className = 'mb-8 p-6 rounded-2xl glass-card border-l-4 border-yellow-500 flex flex-col md:flex-row md:items-center md:justify-between transition-all duration-500 bg-yellow-950/10';
                    statusTxt.className = 'text-3xl font-black mt-1 text-yellow-400';
                } else {
                    banner.className = 'mb-8 p-6 rounded-2xl glass-card border-l-4 border-red-500 flex flex-col md:flex-row md:items-center md:justify-between transition-all duration-500 bg-red-950/20';
                    statusTxt.className = 'text-3xl font-black mt-1 text-red-400';
                }

                document.getElementById('telemetry-badge').className = 'px-2.5 py-0.5 rounded-full text-xs font-semibold bg-green-500/10 text-green-400 border border-green-500/20';
                document.getElementById('telemetry-badge').textContent = 'Online';
                document.getElementById('ai-badge').className = 'px-2.5 py-0.5 rounded-full text-xs font-semibold bg-green-500/10 text-green-400 border border-green-500/20';
                document.getElementById('ai-badge').textContent = 'Online';

            } catch (err) {
                setErrorState(err.toString());
            }
        }

        function setErrorState(errorMsg) {
            const banner = document.getElementById('status-card');
            const statusTxt = document.getElementById('system-status');
            const actionTxt = document.getElementById('system-action');
            
            banner.className = 'mb-8 p-6 rounded-2xl glass-card border-l-4 border-red-500 flex flex-col md:flex-row md:items-center md:justify-between transition-all duration-500 bg-red-950/20';
            statusTxt.className = 'text-3xl font-black mt-1 text-red-500';
            statusTxt.textContent = 'CRITICAL ERROR';
            actionTxt.textContent = errorMsg || 'Unable to connect to upstream services.';

            document.getElementById('telemetry-badge').className = 'px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20';
            document.getElementById('telemetry-badge').textContent = 'Offline';
            document.getElementById('ai-badge').className = 'px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/20';
            document.getElementById('ai-badge').textContent = 'Offline';
        }

        setInterval(fetchData, 3000);
        fetchData();
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/data")
def api_data():
    try:
        response = requests.get(AI_SERVICE_URL, timeout=5)
        return jsonify({
            "status": "success",
            "ai_data": response.json()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3002)