import time
import sys
print("[BOMB SPAM] Starting...")
counter = 0
while True:
    counter += 1
    print(f"[BOMB SPAM] Running iteration {counter}...")
    sys.stdout.flush()
    time.sleep(2)
