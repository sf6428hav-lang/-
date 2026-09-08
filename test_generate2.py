import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Test full generate flow
print("=== Testing full generate flow ===")
stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend && source venv/bin/activate && python << "EOF"\nimport requests\nimport json\n\nurl = "http://185.213.175.66:8002/api/generate"\npayload = {"links": ["https://v.douyin.com/1CzGfFJVQD0/"]}\n\nprint(f"Calling: {url}")\nprint(f"Payload: {payload}")\n\ntry:\n    resp = requests.post(url, json=payload, timeout=300, stream=True)\n    print(f"Status: {resp.status_code}")\n    \n    for line in resp.iter_lines():\n        if line:\n            line = line.decode("utf-8")\n            if line.startswith("data: "):\n                data = json.loads(line[6:])\n                print(f"Event: {data.get(\'type\')} - {data.get(\'message\', \'\')}")\n                if data.get(\'type\') == \'complete\':\n                    if data.get(\'records\'):\n                        print(f"Records: {len(data[\'records\'])}")\n                        for r in data[\'records\'][:2]:\n                            print(f"  - {r.get(\'id\')}: {r.get(\'status\')}")\n                    break\nexcept Exception as e:\n    print(f"Error: {e}")\nEOF')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
