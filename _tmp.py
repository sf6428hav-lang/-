import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Add import os to gemini_worker.py
print("=== Fix gemini_worker.py ===")
stdin, stdout, stderr = ssh.exec_command('sed -i "1i import os" /opt/douyin-script/backend/app/services/gemini_worker.py')
stdout.channel.recv_exit_status()

stdin, stdout, stderr = ssh.exec_command('head -12 /opt/douyin-script/backend/app/services/gemini_worker.py')
print(stdout.read().decode('utf-8', errors='replace'))

# Restart backend
print("\n=== Restart backend ===")
stdin, stdout, stderr = ssh.exec_command('kill -9 $(lsof -ti :8002) 2>/dev/null; sleep 2; cd /opt/douyin-script/backend && source venv/bin/activate && nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 > /tmp/project.log 2>&1 &')
stdout.channel.recv_exit_status()
time.sleep(4)

stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep 8002')
result = stdout.read().decode('utf-8', errors='replace')
print("Port:", result if result else "NOT LISTENING")

# Check logs for errors
print("\n=== Check startup logs ===")
stdin, stdout, stderr = ssh.exec_command('tail -10 /tmp/project.log')
print(stdout.read().decode('utf-8', errors='replace'))

# Test
print("\n=== Test red fruit ===")
stdin, stdout, stderr = ssh.exec_command('curl -s -X POST http://localhost:8002/api/generate -H "Content-Type: application/json" -d \'{"links":["https://novelquickapp.com/s/laBIj58ouLY/"]}\' 2>&1', timeout=300)
result = stdout.read().decode('utf-8', errors='replace')
print(result[:3000])

# Check logs after test
print("\n\n=== Logs after test ===")
stdin, stdout, stderr = ssh.exec_command('tail -30 /tmp/project.log')
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()