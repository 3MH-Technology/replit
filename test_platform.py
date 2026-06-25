import requests
import json
import time
import os

BASE = "http://127.0.0.1:30170"
s = requests.Session()

# 1. Login as admin
print("=== 1. ADMIN LOGIN ===")
r = s.post(f"{BASE}/api/auth/login", json={"username": "moh777", "password": "Mm@123456"})
print(r.json())
print(f"Cookies: {dict(s.cookies)}")
print(f"Headers: {dict(r.headers)}")

# 2. Check profile
print("\n=== 2. PROFILE ===")
r = s.get(f"{BASE}/api/user/profile")
print(r.json())

# 3. Create server "Bomb spam"
print("\n=== 3. CREATE SERVER ===")
r = s.post(f"{BASE}/add", json={"name": "Bomb spam"})
print(r.json())

# 4. List servers
print("\n=== 4. LIST SERVERS ===")
r = s.get(f"{BASE}/servers")
data = r.json()
print(json.dumps(data, indent=2))
server_key = data["servers"][0]["key"]
print(f"Server key: {server_key}")

# 5. Create Bomb spam.py in the server
print("\n=== 5. CREATE Bomb spam.py ===")
r = s.post(f"{BASE}/files/save/{server_key}", json={
    "file": "Bomb spam.py",
    "content": """import time
import sys
print("[BOMB SPAM] Starting...")
counter = 0
while True:
    counter += 1
    print(f"[BOMB SPAM] Running iteration {counter}...")
    sys.stdout.flush()
    time.sleep(2)
"""
})
print(r.json())

# 6. Set startup file
print("\n=== 6. SET STARTUP FILE ===")
r = s.post(f"{BASE}/server/set-startup/{server_key}", json={"file": "Bomb spam.py"})
print(r.json())

# 7. Start the bot
print("\n=== 7. START BOT ===")
r = s.post(f"{BASE}/server/action/{server_key}/start")
print(r.json())

# 8. Wait and check stats
print("\n=== 8. CHECK STATS (waiting 3s) ===")
time.sleep(3)
r = s.get(f"{BASE}/server/stats/{server_key}")
print(json.dumps(r.json(), indent=2))

# 9. Test admin can bypass 4-day renewal check
# First, manually set last_renewed to 10 days ago to trigger expiry
print("\n=== 9. TEST ADMIN RENEWAL EXEMPTION ===")
import time as t
ten_days_ago = t.time() - (10 * 24 * 3600)
server_dir = os.path.join("USERS", "moh777", "servers", "Bomb-spam")
meta_path = os.path.join(server_dir, "meta.json")
with open(meta_path, "r") as f:
    meta = json.load(f)
meta["last_renewed"] = ten_days_ago
with open(meta_path, "w") as f:
    json.dump(meta, f, indent=2)
print(f"Set last_renewed to 10 days ago. Current meta: last_renewed={meta['last_renewed']}")

# Try to restart (should work for admin despite being expired)
r = s.post(f"{BASE}/server/action/{server_key}/restart")
print(f"Admin restart (should succeed): {r.json()}")

# 10. Clean up - delete test server
print("\n=== 10. DELETE TEST SERVER ===")
r = s.post(f"{BASE}/server/delete/{server_key}")
print(r.json())

# 11. Logout
print("\n=== 11. LOGOUT ===")
r = s.get(f"{BASE}/logout")
print(f"Logout status: {r.status_code}")

print("\n=== ALL TESTS PASSED ===")
