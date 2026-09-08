import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Get video metadata
stdin, stdout, stderr = ssh.exec_command('ffprobe -v quiet -print_format json -show_format -show_streams /opt/douyin-script/backend/downloads/6ca0f698-a3e8-4485-9dff-569cf929a887.mp4 2>&1')
print("=== Video metadata ===")
print(stdout.read().decode('utf-8')[:2000])

ssh.close()