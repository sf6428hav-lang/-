import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Save to local file via SFTP
sftp = ssh.open_sftp()
sftp.get('/opt/douyin-script/backend/data/scripts/422e15f0-34b9-4808-888d-61aa2b0dadde.txt', 
         'C:\\Users\\Administrator\\Documents\\网站项目\\backend\\data\\scripts\\latest_script.txt')
sftp.close()
ssh.close()
print("Downloaded to local")