import paramiko, sys, json
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Test douyin parsing
print("=== Testing douyin parsing ===")
stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend && source venv/bin/activate && python << "EOF"\nimport asyncio\nimport sys\nsys.path.insert(0, "/opt/douyin-script/backend")\nfrom app.services.parser_douyin import parse_douyin\n\nurl = "https://v.douyin.com/iYjQ9Y8J/"\ntry:\n    result = asyncio.run(parse_douyin(url))\n    print(f"Success!")\n    print(f"Platform: {result.platform}")\n    print(f"Video URL: {result.video_url}")\n    print(f"Metadata: {result.metadata}")\nexcept Exception as e:\n    print(f"Error: {e}")\nEOF')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
