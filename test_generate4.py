import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Test full generate flow
print("=== Testing full generate flow ===")
test_code = '''
import sys
sys.path.insert(0, "/opt/douyin-script/backend")
import requests
import json

url = "http://127.0.0.1:8002/api/generate"
payload = {"links": ["https://v.douyin.com/1CzGfFJVQD0/"]}

print(f"Calling: {url}")
print(f"Payload: {payload}")

try:
    resp = requests.post(url, json=payload, timeout=300, stream=True)
    print(f"Status: {resp.status_code}")
    
    for line in resp.iter_lines():
        if line:
            line = line.decode("utf-8")
            if line.startswith("data: "):
                data = json.loads(line[6:])
                print(f"Event: {data.get(\'type\')} - {data.get(\'message\', \'\')}")
                if data.get(\'type\') == \'complete\':
                    if data.get(\'records\'):
                        print(f"Records: {len(data[\'records\'])}")
                        for r in data[\'records\'][:2]:
                            print(f"  - {r.get(\'id\')}: {r.get(\'status\')}")
                    break
except Exception as e:
    print(f"Error: {e}")
'''

stdin, stdout, stderr = ssh.exec_command('python3 << "EOF"\n' + test_code + '\nEOF')
stdout.channel.recv_exit_status()
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
