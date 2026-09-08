import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

print("=== Manual test ===")
stdin, stdout, stderr = ssh.exec_command('''cd /opt/douyin-script/backend && source venv/bin/activate && python3 -c "
from pathlib import Path
from app.services.gemini_worker import generate_script

video = Path('/opt/douyin-script/backend/downloads/6ca0f698-a3e8-4485-9dff-569cf929a887.mp4')
print(f'Testing with: {video}')
print(f'File exists: {video.exists()}')
print(f'File size: {video.stat().st_size / 1024 / 1024:.2f} MB')

try:
    result = generate_script(video)
    print(f'\\n=== Result ({len(result)} chars) ===')
    print(result[:1000])
except Exception as e:
    print(f'ERROR: {e}')
"''', timeout=180)
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()