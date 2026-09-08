import paramiko, base64
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# 1. 检查当前服务状态
print("=== 1. 服务状态 ===")
stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep -E "8002|8051"')
print(stdout.read().decode())

# 2. 直接测试生成请求，看完整日志
print("\n=== 2. 测试生成请求 ===")
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -X POST http://localhost:8002/api/generate '
    '-H "Content-Type: application/json" '
    '-d \'{"links":["https://novelquickapp.com/s/laBIj58ouLY/"]}\'',
    timeout=180
)
result = stdout.read().decode()
print(result[:3000])

# 3. 检查后端日志中是否有错误
print("\n=== 3. 后端日志 ===")
stdin, stdout, stderr = ssh.exec_command('tail -30 /tmp/project.log')
print(stdout.read().decode())

ssh.close()