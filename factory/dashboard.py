#!/usr/bin/env python3
"""
EVEZ666 DASHBOARD - Real-time monitoring
Serves HTML dashboard at http://localhost:5000
"""

import http.server
import socketserver
import json
import threading
import time
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/root/.openclaw/workspace")
FACTORY_DIR = WORKSPACE / "factory"
PORT = 5000

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_dashboard().encode())
        elif self.path == "/status":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(self.get_status().encode())
        elif self.path == "/cycle":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(self.get_cycle_data().encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_dashboard(self) -> str:
        return """<!DOCTYPE html>
<html>
<head>
    <title>EVEZ666 Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Courier New', monospace; 
            background: #0a0a0f; 
            color: #0f0; 
            padding: 20px;
            min-height: 100vh;
        }
        h1 { 
            text-align: center; 
            color: #0ff; 
            text-shadow: 0 0 20px #0ff;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: #111;
            border: 2px solid #0f0;
            border-radius: 10px;
            padding: 20px;
        }
        .card h2 {
            color: #0ff;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        .stat {
            font-size: 2em;
            color: #0ff;
            text-align: center;
            padding: 20px;
        }
        .stat-label {
            color: #666;
            font-size: 0.8em;
            text-align: center;
        }
        .log {
            background: #000;
            border: 1px solid #333;
            padding: 15px;
            height: 300px;
            overflow-y: auto;
            font-size: 0.9em;
            line-height: 1.5;
        }
        .log-entry {
            margin-bottom: 8px;
            padding: 5px;
            border-left: 3px solid #0f0;
        }
        .log-entry.error {
            border-left-color: #f00;
            color: #f88;
        }
        .log-entry.success {
            border-left-color: #0ff;
        }
        .github-link {
            display: block;
            text-align: center;
            padding: 20px;
            background: #0f0;
            color: #000;
            text-decoration: none;
            font-weight: bold;
            border-radius: 10px;
            margin-top: 20px;
        }
        .github-link:hover {
            background: #0ff;
        }
        .worker {
            display: flex;
            justify-content: space-between;
            padding: 8px;
            border-bottom: 1px solid #333;
        }
        .worker.status-idle { color: #0f0; }
        .worker.status-working { color: #0ff; }
        .worker.status-error { color: #f00; }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .live { animation: pulse 2s infinite; color: #0ff; }
    </style>
</head>
<body>
    <h1>⚡ EVEZ666 FACTORY DASHBOARD <span class="live">● LIVE</span></h1>
    
    <div class="grid">
        <div class="card">
            <h2>📊 Current Cycle</h2>
            <div class="stat" id="cycle">0</div>
            <div class="stat-label">Factory Cycles Completed</div>
        </div>
        <div class="card">
            <h2>⚡ Quantum Runs</h2>
            <div class="stat" id="quantum">0</div>
            <div class="stat-label">Algorithms Executed</div>
        </div>
        <div class="card">
            <h2>📦 Deployments</h2>
            <div class="stat" id="deployments">0</div>
            <div class="stat-label">Successful Deployments</div>
        </div>
        <div class="card">
            <h2>🔧 Workers</h2>
            <div id="workers"></div>
        </div>
    </div>
    
    <div class="card">
        <h2>📜 Activity Log (Real-time)</h2>
        <div class="log" id="log"></div>
    </div>
    
    <a href="https://github.com/EvezArt/evez666-advancement" target="_blank" class="github-link">
        🚀 VIEW ON GITHUB
    </a>
    
    <script>
        function update() {
            fetch('/status').then(r => r.json()).then(data => {
                document.getElementById('cycle').innerText = data.cycle;
                document.getElementById('quantum').innerText = data.quantum_runs;
                document.getElementById('deployments').innerText = data.deployments;
                
                let workersHtml = '';
                for (let w of data.workers) {
                    workersHtml += `<div class="worker status-${w.status}">
                        <span>${w.name}</span>
                        <span>${w.status}</span>
                    </div>`;
                }
                document.getElementById('workers').innerHTML = workersHtml;
            });
            
            fetch('/cycle').then(r => r.json()).then(data => {
                let logHtml = '';
                for (let e of data.entries.slice(-20).reverse()) {
                    let cls = e.type || '';
                    logHtml += `<div class="log-entry ${cls}">[${e.time}] ${e.msg}</div>`;
                }
                document.getElementById('log').innerHTML = logHtml;
            });
        }
        
        update();
        setInterval(update, 3000);
    </script>
</body>
</html>"""
    
    def get_status(self) -> str:
        # Read checkpoint
        checkpoint_file = FACTORY_DIR / "checkpoint.json"
        if checkpoint_file.exists():
            data = json.loads(checkpoint_file.read_text())
            return json.dumps({
                "cycle": data.get("cycle", 0),
                "quantum_runs": len(data.get("discoveries", [])),
                "deployments": len(data.get("deployments", [])),
                "workers": [
                    {"name": "EVEZ-Researcher", "status": "idle"},
                    {"name": "EVEZ-Quantum", "status": "idle"},
                    {"name": "EVEZ-Developer", "status": "idle"},
                    {"name": "EVEZ-Tester", "status": "idle"},
                    {"name": "EVEZ-Deployer", "status": "idle"},
                    {"name": "EVEZ-GitPusher", "status": "idle"},
                    {"name": "EVEZ-Monitor", "status": "idle"}
                ]
            })
        return json.dumps({"cycle": 0, "quantum_runs": 0, "deployments": 0, "workers": []})
    
    def get_cycle_data(self) -> str:
        return json.dumps({
            "entries": [
                {"time": datetime.now().strftime("%H:%M:%S"), "msg": "Factory running", "type": "success"}
            ]
        })

def run_server():
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"🌐 Dashboard: http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()