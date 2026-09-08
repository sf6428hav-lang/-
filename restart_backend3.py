import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Kill existing backend
print("=== Killing existing backend ===")
stdin, stdout, stderr = ssh.exec_command('pkill -f "uvicorn app.main:app"')
stdout.channel.recv_exit_status()

import time
time.sleep(2)

# Start backend
print("\n=== Starting backend ===")
stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend && source venv/bin/activate && nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload > /tmp/douyin_backend.log 2>&1 &')
stdout.channel.recv_exit_status()

time.sleep(3)

# Check status
print("\n=== Checking backend status ===")
stdin, stdout, stderr = ssh.exec_command('ps aux | grep "uvicorn app.main:app" | grep -v grep')
output = stdout.read().decode('utf-8')
if output:
    print("Backend is running")
    print(output)
else:
    print("Backend NOT running")

# Check logs
print("\n=== Recent logs ===")
stdin, stdout, stderr = ssh.exec_command('tail -15 /tmp/douyin_backend.log')
print(stdout.read().decode('utf-8'))

ssh.close()
