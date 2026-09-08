import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Check what's in parser_douyin.py
print("=== Current parser_douyin.py ===")
stdin, stdout, stderr = ssh.exec_command('head -20 /opt/douyin-script/backend/app/services/parser_douyin.py')
print(stdout.read().decode('utf-8', errors='replace'))

# Test media-parser with this douyin link
print("\n=== Test media-parser with douyin link ===")
stdin, stdout, stderr = ssh.exec_command('''
cd /opt/douyin-script/backend && source venv/bin/activate && python3 -c "
import httpx, json
resp = httpx.post('http://127.0.0.1:8051/api/parse', json={'text': 'https://v.douyin.com/1CzGfFJVQD0/'}, timeout=60)
data = resp.json()
print('succ:', data.get('succ'))
print('title:', data.get('data', {}).get('title', 'N/A'))
print('video_url:', data.get('data', {}).get('video_url', 'N/A')[:200])
print('retdesc:', data.get('retdesc', 'N/A'))
"
''', timeout=60)
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()