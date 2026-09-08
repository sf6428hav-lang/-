import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Check downloaded video
print("=== Video info ===")
stdin, stdout, stderr = ssh.exec_command('file /opt/douyin-script/backend/downloads/6ca0f698-a3e8-4485-9dff-569cf929a887.mp4')
print(stdout.read().decode('utf-8'))

stdin, stdout, stderr = ssh.exec_command('ls -lh /opt/douyin-script/backend/downloads/6ca0f698-a3e8-4485-9dff-569cf929a887.mp4')
print(stdout.read().decode('utf-8'))

# Check extracted audio
print("\n=== Audio files ===")
stdin, stdout, stderr = ssh.exec_command('ls -lh /opt/douyin-script/backend/downloads/*.mp3 2>/dev/null | tail -3')
print(stdout.read().decode('utf-8') or "No mp3 files")

# Check extracted frames
print("\n=== Frame files ===")
stdin, stdout, stderr = ssh.exec_command('ls -lh /opt/douyin-script/backend/downloads/*.jpg 2>/dev/null | wc -l')
print(f"Frame count: {stdout.read().decode('utf-8').strip()}")

stdin, stdout, stderr = ssh.exec_command('ls /opt/douyin-script/backend/downloads/*.jpg 2>/dev/null | head -3')
print(stdout.read().decode('utf-8'))

ssh.close()