import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Check current gemini_worker.py
print("=== Checking gemini_worker.py ===")
stdin, stdout, stderr = ssh.exec_command('cat /opt/douyin-script/backend/app/services/gemini_worker.py')
content = stdout.read().decode('utf-8')
print(content[:500])

# Fix ffmpeg path
print("\n=== Fixing ffmpeg path ===")
stdin, stdout, stderr = ssh.exec_command('sed -i \'s|C:\\\\Program Files\\\\EVCapture\\\\ffmpeg.exe|/usr/bin/ffmpeg|g\' /opt/douyin-script/backend/app/services/gemini_worker.py')
stdout.channel.recv_exit_status()

# Verify
stdin, stdout, stderr = ssh.exec_command('grep -n ffmpeg /opt/douyin-script/backend/app/services/gemini_worker.py')
print(stdout.read().decode('utf-8'))

ssh.close()
