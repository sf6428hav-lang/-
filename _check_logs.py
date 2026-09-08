import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

print("=== Recent backend logs ===")
stdin, stdout, stderr = ssh.exec_command('tail -200 /tmp/project.log')
print(stdout.read().decode('utf-8'))

ssh.close()