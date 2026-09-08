import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Check what's in the database
print("=== Check database ===")
stdin, stdout, stderr = ssh.exec_command("""cd /opt/douyin-script/backend && sqlite3 data/database.sqlite "SELECT id, title, status, created_at FROM scripts ORDER BY created_at DESC LIMIT 3" """)
print(stdout.read().decode('utf-8', errors='replace'))

# Get full logs
print("\n=== Full logs ===")
stdin, stdout, stderr = ssh.exec_command('cat /tmp/project.log')
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()