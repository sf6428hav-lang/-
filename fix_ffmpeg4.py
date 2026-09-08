import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Use sed to replace the path directly
print("=== Using sed to replace path ===")
stdin, stdout, stderr = ssh.exec_command('sed -i \'s|C:\\\\Program Files\\\\EVCapture\\\\ffmpeg.exe|/usr/bin/ffmpeg|g\' /opt/douyin-script/backend/app/services/gemini_worker.py')
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
