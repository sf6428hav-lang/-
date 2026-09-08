import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Restart backend
print("=== Restarting backend ===")
stdin, stdout, stderr = ssh.exec_command('systemctl restart douyin-script')
stdout.channel.recv_exit_status()
print("Restarted")

import time
time.sleep(3)

# Check status
print("\n=== Check status ===")
stdin, stdout, stderr = ssh.exec_command('systemctl is-active douyin-script')
status = stdout.read().decode('utf-8').strip()
print(f"Status: {status}")

# Check logs
print("\n=== Recent logs ===")
stdin, stdout, stderr = ssh.exec_command('journalctl -u douyin-script -n 20 --no-pager')
print(stdout.read().decode('utf-8'))

ssh.close()
