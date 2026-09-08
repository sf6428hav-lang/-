import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Use Python with raw string to handle the path correctly
python_script = r'''
# Read the file
with open('/opt/douyin-script/backend/app/services/gemini_worker.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the path - use raw string for Windows path
old_path = r'C:\Program Files\EVCapture\ffmpeg.exe'
new_path = '/usr/bin/ffmpeg'
content = content.replace(old_path, new_path)

# Write back
with open('/opt/douyin-script/backend/app/services/gemini_worker.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
with open('/opt/douyin-script/backend/app/services/gemini_worker.py', 'r', encoding='utf-8') as f:
    new_content = f.read()
    if new_path in new_content:
        print('SUCCESS: Path replaced')
    else:
        print('FAILED: Path not found')
        # Print line 9 exactly
        lines = new_content.split('\n')
        print(f'Line 9: {lines[8]}')
        print(f'Looking for: {old_path}')
        print(f'In line: {old_path in lines[8]}')
'''

stdin, stdout, stderr = ssh.exec_command('python3 << "PYEOF"\n' + python_script + '\nPYEOF')
stdout.channel.recv_exit_status()
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
