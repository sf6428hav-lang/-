import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Read file with proper encoding
stdin, stdout, stderr = ssh.exec_command('cat /opt/douyin-script/backend/data/scripts/422e15f0-34b9-4808-888d-61aa2b0dadde.txt')
content = stdout.read()
print("=== Script content ===")
print(content.decode('utf-8'))

ssh.close()