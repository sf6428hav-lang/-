import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Check file encoding and read with UTF-8
stdin, stdout, stderr = ssh.exec_command('file -bi /opt/douyin-script/backend/data/scripts/422e15f0-34b9-4808-888d-61aa2b0dadde.txt')
print("=== File encoding ===")
print(stdout.read().decode('utf-8', errors='replace'))

stdin, stdout, stderr = ssh.exec_command('cat /opt/douyin-script/backend/data/scripts/422e15f0-34b9-4808-888d-61aa2b0dadde.txt | head -50')
print("\n=== Script content (first 50 lines) ===")
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()