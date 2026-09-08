import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Quick status check
stdin, stdout, stderr = ssh.exec_command('ss -tlnp | grep -E "8002|8051"')
print("Ports:", stdout.read().decode().strip())

stdin, stdout, stderr = ssh.exec_command('tail -20 /tmp/project.log')
print("Logs:", stdout.read().decode())

ssh.close()