import requests
import json
import time
import os

BASE = "http://127.0.0.1:30170"
s = requests.Session()

# Login as admin
r = s.post(f"{BASE}/api/auth/login", json={"username": "moh777", "password": "Mm@123456"})
print(f"Login: {r.json()}")

# Create server
r = s.post(f"{BASE}/add", json={"name": "Bomb spam"})
print(f"Create: {r.json()}")

# Get server key
r = s.get(f"{BASE}/servers")
servers = r.json().get("servers", [])
print(f"Servers: {len(servers)}")
key = servers[0]["key"]
print(f"Key: {key}")

# Create file
r = s.post(f"{BASE}/files/save/{key}", json={
    "file": "Bomb spam.py",
    "content": "import time, sys\ncounter=0\nwhile True:\n counter+=1\n print(f'[BOMB SPAM] Running {counter}...')\n sys.stdout.flush()\n time.sleep(2)\n"
})
print(f"Save file: {r.json()}")

# Set startup
r = s.post(f"{BASE}/server/set-startup/{key}", json={"file": "Bomb spam.py"})
print(f"Set startup: {r.json()}")

# Start
print("Starting...")
r = s.post(f"{BASE}/server/action/{key}/start")
print(f"Start: {r.json()}")

# Poll stats
for i in range(5):
    time.sleep(2)
    r = s.get(f"{BASE}/server/stats/{key}")
    d = r.json()
    print(f"  Poll {i+1}: status={d.get('status')}, cpu={d.get('cpu')}, mem={d.get('mem')}, logs_len={len(d.get('logs',''))}")
    if d.get("logs"):
        print(f"  Last log lines: {d['logs'].strip().split(chr(10))[-3:]}")

# Check if process exists in running_procs
print(f"\nChecking running_procs...")
print(f"Key in running_procs: {key}")
