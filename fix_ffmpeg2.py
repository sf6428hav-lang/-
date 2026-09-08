import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Read the file
print("=== Reading gemini_worker.py ===")
stdin, stdout, stderr = ssh.exec_command('cat /opt/douyin-script/backend/app/services/gemini_worker.py')
content = stdout.read().decode('utf-8')

# Replace the path
print("=== Fixing ffmpeg path ===")
content = content.replace('C:\\Program Files\\EVCapture\\ffmpeg.exe', '/usr/bin/ffmpeg')

# Write back
stdin, stdout, stderr = ssh.exec_command('cat > /opt/douyin-script/backend/app/services/gemini_worker.py << "EOF"\n' + content + '\nEOF')
stdout.channel.recv_exit_status()

# Verify
print("\n=== Verifying fix ===")
stdin, stdout, stderr = ssh.exec_command('grep -n "FFMPEG" /opt/douyin-script/backend/app/services/gemini_worker.py')
print(stdout.read().decode('utf-8'))

# Restart backend
print("\n=== Restarting backend ===")
stdin, stdout, stderr = ssh.exec_command('pkill -f "uvicorn.*app.main"')
stdout.channel.recv_exit_status()

import time
time.sleep(2)

stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend && source venv/bin/activate && nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload > /tmp/douyin_backend.log 2>&1 &')
stdout.channel.recv_exit_status()

time.sleep(3)

# Check if running
print("\n=== Checking backend status ===")
stdin, stdout, stderr = ssh.exec_command('ps aux | grep "uvicorn.*app.main" | grep -v grep')
output = stdout.read().decode('utf-8')
if output:
    print("Backend is running")
    print(output)
else:
    print("Backend NOT running")

# Check logs
print("\n=== Recent logs ===")
stdin, stdout, stderr = ssh.exec_command('tail -10 /tmp/douyin_backend.log')
print(stdout.read().decode('utf-8'))

ssh.close()
