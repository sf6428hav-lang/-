import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Check database for generated scripts
print("=== Check database ===")
stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend && source venv/bin/activate && python3 -c "
import sqlite3
conn = sqlite3.connect(\"data/database.sqlite\")
cursor = conn.cursor()
cursor.execute(\"SELECT id, title, status, created_at FROM scripts ORDER BY created_at DESC LIMIT 5\")
for row in cursor.fetchall():
    print(row)
conn.close()
"')
print(stdout.read().decode('utf-8', errors='replace'))

# Get the content of the latest script
print("\n=== Latest script content ===")
stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend && source venv/bin/activate && python3 -c "
import sqlite3
conn = sqlite3.connect(\"data/database.sqlite\")
cursor = conn.cursor()
cursor.execute(\"SELECT content FROM scripts ORDER BY created_at DESC LIMIT 1\")
row = cursor.fetchone()
if row:
    print(row[0])
conn.close()
"')
print(stdout.read().decode('utf-8', errors='replace'))

# Also check full project logs
print("\n=== Full project logs ===")
stdin, stdout, stderr = ssh.exec_command('cat /tmp/project.log')
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()