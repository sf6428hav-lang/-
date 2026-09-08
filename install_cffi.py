import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Install curl_cffi in the venv
print("=== Installing curl_cffi ===")
stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend && source venv/bin/activate && pip install curl_cffi 2>&1')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

# Verify
print("\n=== Verify curl_cffi ===")
stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend && source venv/bin/activate && python -c "from curl_cffi import requests; print(\'curl_cffi OK\')"')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
