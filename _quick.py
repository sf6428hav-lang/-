import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# 快速检查服务是否在运行
print("=== 服务状态 ===")
stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep -E "8002|8051"')
print(stdout.read().decode())

# 查看日志
print("\n=== 最近日志 ===")
stdin, stdout, stderr = ssh.exec_command('tail -20 /tmp/project.log')
print(stdout.read().decode())

# 检查进程
print("\n=== Python进程 ===")
stdin, stdout, stderr = ssh.exec_command('ps aux | grep -E "uvicorn|app.py" | grep -v grep')
print(stdout.read().decode())

ssh.close()