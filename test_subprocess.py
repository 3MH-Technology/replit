import sys, os, subprocess, time

BASE_DIR = os.path.dirname(os.path.abspath('app.py'))
server_dir = os.path.join('USERS', 'moh777', 'servers', 'Bomb-spam')
startup_file = 'Bomb spam.py'

print(f'BASE_DIR: {BASE_DIR}')
print(f'server_dir: {os.path.abspath(server_dir)}')
print(f'startup_file: {startup_file}')
print(f'sys.executable: {sys.executable}')
print(f'File exists: {os.path.exists(os.path.join(server_dir, startup_file))}')

wrapper_code = '''
import sys, os
sys.path.insert(0, """ + repr(BASE_DIR) + """)
import runpy, subprocess, traceback, re
script = sys.argv[1]
cwd = os.getcwd()
try:
    runpy.run_path(script, run_name="__main__")
except Exception:
    traceback.print_exc()
'''

log_path = os.path.join(server_dir, 'server.log')
# Clear log
open(log_path, 'w').close()
log_file = open(log_path, 'a', encoding='utf-8', errors='ignore')

proc = subprocess.Popen(
    [sys.executable, '-u', '-c', wrapper_code, startup_file],
    cwd=server_dir,
    stdout=log_file,
    stderr=log_file,
    env={**os.environ, 'PYTHONUNBUFFERED': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
)

time.sleep(3)
print(f'Process poll: {proc.poll()}')
print(f'Process pid: {proc.pid}')

log_file.close()

with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
    print(f'Log content ({len(content)} chars):')
    print(content[:1000] if content else '(empty)')
