import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Kill existing processes
print("=== Killing existing processes ===")
stdin, stdout, stderr = ssh.exec_command('pkill -f "uvicorn.*app.main"')
stdout.channel.recv_exit_status()
print("Killed")

import time
time.sleep(2)

# Start backend
print("\n=== Starting backend ===")
stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend && source venv/bin/activate && nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload > /tmp/douyin_backend.log 2>&1 &')
stdout.channel.recv_exit_status()
print("Started")

time.sleep(3)

# Check if running
print("\n=== Check if running ===")
stdin, stdout, stderr = ssh.exec_command('ps aux | grep uvicorn | grep -v grep')
output = stdout.read().decode('utf-8')
if output:
    print("Backend is running")
    print(output)
else:
    print("Backend NOT running")

# Check logs
print("\n=== Recent logs ===")
stdin, stdout, stderr = ssh.exec_command('tail -20 /tmp/douyin_backend.log')
print(stdout.read().decode('utf-8'))

ssh.close()
