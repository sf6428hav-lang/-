import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Check how uvicorn is started
print("=== Check uvicorn process ===")
stdin, stdout, stderr = ssh.exec_command('ps aux | grep uvicorn')
print(stdout.read().decode('utf-8'))

# Check if there are any other log files
print("\n=== Check log files ===")
stdin, stdout, stderr = ssh.exec_command('find /opt/douyin-script/backend -name "*.log" -type f')
print(stdout.read().decode('utf-8'))

# Check nohup.out
print("\n=== Check nohup.out ===")
stdin, stdout, stderr = ssh.exec_command('ls -lh /opt/douyin-script/backend/nohup.out 2>/dev/null || echo "No nohup.out"')
print(stdout.read().decode('utf-8'))

ssh.close()