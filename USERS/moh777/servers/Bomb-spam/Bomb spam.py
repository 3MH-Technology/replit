import time, sys
counter=0
while True:
 counter+=1
 print(f'[BOMB SPAM] Running {counter}...')
 sys.stdout.flush()
 time.sleep(2)
