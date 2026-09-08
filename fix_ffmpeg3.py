import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Read the file
print("=== Reading gemini_worker.py ===")
stdin, stdout, stderr = ssh.exec_command('cat /opt/douyin-script/backend/app/services/gemini_worker.py')
content = stdout.read().decode('utf-8')

# Replace the Windows path with Linux path
print("=== Replacing path ===")
old_path = 'C:\\Program Files\\EVCapture\\ffmpeg.exe'
new_path = '/usr/bin/ffmpeg'
content = content.replace(old_path, new_path)

# Write back
print("=== Writing back ===")
stdin, stdout, stderr = ssh.exec_command('cat > /opt/douyin-script/backend/app/services/gemini_worker.py << "EOF"\n' + content + '\nEOF')
stdout.channel.recv_exit_status()

# Verify
print("\n=== Verifying ===")
stdin, stdout, stderr = ssh.exec_command('grep -n "FFMPEG" /opt/douyin-script/backend/app/services/gemini_worker.py')
output = stdout.read().decode('utf-8')
print(output)

if '/usr/bin/ffmpeg' in output:
    print("✅ Path successfully updated!")
else:
    print("❌ Path still not updated")

ssh.close()
