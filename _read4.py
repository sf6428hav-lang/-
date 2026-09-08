import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Read with GBK encoding
stdin, stdout, stderr = ssh.exec_command('cat /opt/douyin-script/backend/data/scripts/422e15f0-34b9-4808-888d-61aa2b0dadde.txt')
content = stdout.read()
try:
    print("=== GBK ===")
    print(content.decode('gbk'))
except:
    try:
        print("=== GB2312 ===")
        print(content.decode('gb2312'))
    except:
        try:
            print("=== GB18030 ===")
            print(content.decode('gb18030'))
        except Exception as e:
            print(f"All failed: {e}")
            # Show raw bytes
            print("\n=== Raw hex (first 200 bytes) ===")
            print(content[:200].hex())

ssh.close()