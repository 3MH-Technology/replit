import requests
import json

BASE = "http://127.0.0.1:30170"
s = requests.Session()

# Login
r = s.post(f"{BASE}/api/auth/login", json={"username": "moh777", "password": "Mm@123456"})
print("LOGIN:", r.status_code)

# Check cookie details
for cookie in s.cookies:
    print(f"  Cookie: {cookie.name}={cookie.value[:30]}... domain={cookie.domain} path={cookie.path} secure={cookie.secure}")

# Manually set the cookie in the header and try again
print("\n--- Manual cookie test ---")
s2 = requests.Session()
# Login to get the cookie value
r2 = s2.post(f"{BASE}/api/auth/login", json={"username": "moh777", "password": "Mm@123456"})
cookie_val = s2.cookies.get("session")
print(f"Got cookie: {cookie_val[:30]}...")

# Now manually set the cookie header
s2.headers.update({"Cookie": f"session={cookie_val}"})
r2 = s2.get(f"{BASE}/api/user/profile")
print(f"Manual cookie profile: {r2.status_code} - {r2.text[:100]}")

# Try with just the raw cookie, no session object
s3 = requests.Session()
s3.headers.update({"Cookie": f"session={cookie_val}"})
r3 = s3.get(f"{BASE}/api/user/profile")
print(f"Raw cookie profile: {r3.status_code} - {r3.text[:100]}")
