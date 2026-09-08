import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Check database structure and content
stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend && sqlite3 data/database.sqlite ".schema"')
print("=== DB Schema ===")
print(stdout.read().decode('utf-8', errors='replace'))

stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend && sqlite3 data/database.sqlite "SELECT count(*) FROM scripts"')
print("\n=== Script count ===")
print(stdout.read().decode('utf-8', errors='replace'))

# Check if there are any output files
stdin, stdout, stderr = ssh.exec_command('find /opt/douyin-script/backend -name "*.txt" -newer /tmp/project.log 2>/dev/null')
print("\n=== New txt files ===")
print(stdout.read().decode('utf-8', errors='replace'))

# Check downloads directory
stdin, stdout, stderr = ssh.exec_command('ls -lh /opt/douyin-script/backend/downloads/ 2>/dev/null | tail -10')
print("\n=== Downloads ===")
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()