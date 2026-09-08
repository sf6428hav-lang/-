import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Read line 9 to see the exact format
stdin, stdout, stderr = ssh.exec_command("sed -n '9p' /opt/douyin-script/backend/app/services/gemini_worker.py")
line9 = stdout.read().decode('utf-8')
print(f'Line 9: {line9}')

# Use sed to replace - the actual path in the file
stdin, stdout, stderr = ssh.exec_command(r"sed -i 's|C:\\Program Files\\EVCapture\\ffmpeg.exe|/usr/bin/ffmpeg|g' /opt/douyin-script/backend/app/services/gemini_worker.py")
stdout.channel.recv_exit_status()

# Verify
stdin, stdout, stderr = ssh.exec_command("sed -n '9p' /opt/douyin-script/backend/app/services/gemini_worker.py")
new_line9 = stdout.read().decode('utf-8')
print(f'New Line 9: {new_line9}')

ssh.close()
