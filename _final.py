import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# 直接看完整日志，找出所有错误
print("=== 完整日志 ===")
stdin, stdout, stderr = ssh.exec_command('cat /tmp/project.log')
print(stdout.read().decode())

# 检查生成的剧本文件
print("\n=== 生成的文件 ===")
stdin, stdout, stderr = ssh.exec_command('find /opt/douyin-script/backend/data/scripts -name "*.txt" -type f -printf "%T@ %p\n" 2>/dev/null | sort -rn | head -3')
files = stdout.read().decode().strip()
print(files)

# 如果有最新的文件，读取并显示（用正确编码）
if files:
    for line in files.split('\n'):
        if line.strip():
            filepath = line.split(' ', 1)[1]
            print(f"\n=== {filepath} ===")
            stdin, stdout, stderr = ssh.exec_command(f'cat "{filepath}"')
            content = stdout.read()
            # Print as bytes to avoid encoding issues
            print(content.decode('utf-8', errors='replace')[:1000])

ssh.close()