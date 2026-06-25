import requests
import json
import time
import os
import shutil

BASE = "http://127.0.0.1:30170"
s = requests.Session()

PASS = 0
FAIL = 0

def test(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} - {detail}")

# 1. Login as admin
print("\n=== 1. ADMIN LOGIN ===")
r = s.post(f"{BASE}/api/auth/login", json={"username": "moh777", "password": "Mm@123456"})
test("Admin login success", r.status_code == 200 and r.json().get("success") and r.json().get("is_admin"))

# 2. Profile
print("\n=== 2. PROFILE ===")
r = s.get(f"{BASE}/api/user/profile")
d = r.json()
test("Profile returns admin", d.get("is_admin"))
test("Profile max_bots = 999999", d.get("max_bots") == 999999)

# 3. Register a new user
print("\n=== 3. REGISTER NEW USER ===")
r = s.post(f"{BASE}/api/auth/register-otp", json={"username": "newuser1", "password": "Pass123", "email": "new@test.com"})
d = r.json()
test("Registration success", d.get("success") and d.get("skip_otp"))

# 4. List servers (should be empty for admin)
print("\n=== 4. LIST SERVERS ===")
r = s.get(f"{BASE}/servers")
d = r.json()
test("Servers list OK", d.get("success"))
initial_count = len(d.get("servers", []))
print(f"  Initial server count: {initial_count}")

# 5. Create server "Bomb spam"
print("\n=== 5. CREATE SERVER ===")
r = s.post(f"{BASE}/add", json={"name": "Bomb spam"})
d = r.json()
test("Server created", d.get("success"))
if d.get("success"):
    server_key = d["servers"][0]["key"]
    print(f"  Server key: {server_key}")
else:
    # Get servers and find the key
    r = s.get(f"{BASE}/servers")
    d = r.json()
    server_key = d["servers"][0]["key"]
    print(f"  Using existing key: {server_key}")

# 6. Verify server in list
print("\n=== 6. VERIFY SERVER LIST ===")
r = s.get(f"{BASE}/servers")
d = r.json()
found = any(srv.get("key") == server_key for srv in d.get("servers", []))
test("Server appears in list", found)

# 7. Create Bomb spam.py
print("\n=== 7. CREATE Bomb spam.py ===")
py_content = """import time
import sys
print("[BOMB SPAM] Starting...")
counter = 0
while True:
    counter += 1
    print(f"[BOMB SPAM] Running iteration {counter}...")
    sys.stdout.flush()
    time.sleep(2)
"""
r = s.post(f"{BASE}/files/save/{server_key}", json={"file": "Bomb spam.py", "content": py_content})
d = r.json()
test("File saved", d.get("success"))

# 8. Set startup file
print("\n=== 8. SET STARTUP FILE ===")
r = s.post(f"{BASE}/server/set-startup/{server_key}", json={"file": "Bomb spam.py"})
d = r.json()
test("Startup file set", d.get("success"))

# 9. Start the bot
print("\n=== 9. START BOT ===")
r = s.post(f"{BASE}/server/action/{server_key}/start")
d = r.json()
test("Bot start requested", d.get("success"))

# 10. Check stats after start
print("\n=== 10. CHECK BOT RUNNING ===")
time.sleep(4)
r = s.get(f"{BASE}/server/stats/{server_key}")
d = r.json()
test("Bot status is Running", d.get("status") == "Running", f"Got: {d.get('status')}")
test("Bot has logs", len(d.get("logs", "")) > 50, f"Log length: {len(d.get('logs', ''))}")
print(f"  Status: {d.get('status')}, CPU: {d.get('cpu')}, MEM: {d.get('mem')}")
if d.get("logs"):
    log_lines = d["logs"].strip().split("\n")
    for ln in log_lines[-3:]:
        print(f"  LOG: {ln}")

# 11. Stop the bot
print("\n=== 11. STOP BOT ===")
r = s.post(f"{BASE}/server/action/{server_key}/stop")
d = r.json()
test("Bot stopped", d.get("success"))
time.sleep(1)
r = s.get(f"{BASE}/server/stats/{server_key}")
d = r.json()
test("Bot status is Offline after stop", d.get("status") == "Offline", f"Got: {d.get('status')}")

# 12. Test admin renewal exemption
print("\n=== 12. ADMIN RENEWAL EXEMPTION ===")
owner, folder = server_key.split("::") if "::" in server_key else ("moh777", server_key)
meta_path = os.path.join("USERS", owner, "servers", folder, "meta.json")
with open(meta_path, "r") as f:
    meta = json.load(f)
meta["last_renewed"] = time.time() - (10 * 24 * 3600)  # 10 days ago
with open(meta_path, "w") as f:
    json.dump(meta, f, indent=2)
print(f"  Set last_renewed to 10 days ago (expired)")

# Try restart - should work because admin
r = s.post(f"{BASE}/server/action/{server_key}/restart")
d = r.json()
test("Admin can start expired bot", d.get("success"), f"Got: {d.get('message', 'no message')}")

# Stop again
time.sleep(2)
s.post(f"{BASE}/server/action/{server_key}/stop")

# 13. Test file manager
print("\n=== 13. FILE MANAGER ===")
r = s.get(f"{BASE}/files/list/{server_key}")
d = r.json()
test("File list OK", d.get("success"))
files_found = [f["name"] for f in d.get("files", [])]
test("Bomb spam.py in file list", "Bomb spam.py" in files_found, f"Files: {files_found}")

# 14. Delete test server
print("\n=== 14. DELETE TEST SERVER ===")
r = s.post(f"{BASE}/server/delete/{server_key}")
d = r.json()
test("Server deleted", d.get("success"))

# Verify deletion
r = s.get(f"{BASE}/servers")
d = r.json()
still_exists = any(srv.get("key") == server_key for srv in d.get("servers", []))
test("Server removed from list", not still_exists)

# 15. Delete test users
print("\n=== 15. DELETE TEST USER ===")
r = s.post(f"{BASE}/api/admin/user/delete", json={"username": "newuser1"})
d = r.json()
test("Test user deleted", d.get("success"))

# Summary
print(f"\n{'='*50}")
print(f"RESULTS: {PASS} passed, {FAIL} failed out of {PASS+FAIL} tests")
print(f"{'='*50}")

# Clean up test data directories
for d in ["USERS", "DATA"]:
    p = os.path.join(d)
    if os.path.exists(p):
        shutil.rmtree(p)
        print(f"Cleaned up: {p}")
