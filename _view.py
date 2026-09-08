import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Find the latest generated script
print("=== Find latest script ===")
stdin, stdout, stderr = ssh.exec_command('find /opt/douyin-script/backend/output -name "*.md" -type f -printf "%T@ %p\\n" 2>/dev/null | sort -rn | head -1')
latest = stdout.read().decode('utf-8').strip()
print("Latest:", latest)

if latest:
    filepath = latest.split(' ', 1)[1]
    print(f"\n=== Content of {filepath} ===")
    stdin, stdout, stderr = ssh.exec_command(f'cat "{filepath}"')
    print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()