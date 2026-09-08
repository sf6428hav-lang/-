import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Verify the file content
print("=== Verify parser_douyin.py ===")
stdin, stdout, stderr = ssh.exec_command('head -20 /opt/douyin-script/backend/app/services/parser_douyin.py')
print(stdout.read().decode('utf-8'))

# Check if curl_cffi is installed
print("\n=== Check curl_cffi ===")
stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend && source venv/bin/activate && python -c "from curl_cffi import requests; print(\'curl_cffi OK\')"')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

# Check backend logs
print("\n=== Backend logs ===")
stdin, stdout, stderr = ssh.exec_command('tail -10 /tmp/project.log')
print(stdout.read().decode('utf-8'))

ssh.close()
