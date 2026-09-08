import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# 打印 media-parser 返回的完整解析结果
test_code = '''
import httpx, json

url = "https://novelquickapp.com/s/laBIj58ouLY/"
print("=== 原始链接 ===")
print(url)

# 1. 先看重定向
print("\n=== 重定向 ===")
resp = httpx.get(url, follow_redirects=True, timeout=30, 
    headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"})
print(f"最终 URL: {resp.url}")
print(f"Status: {resp.status_code}")

# 2. 调用 media-parser
print("\n=== media-parser 解析结果 ===")
resp = httpx.post("http://127.0.0.1:8051/api/parse", json={"text": url}, timeout=60)
data = resp.json()
print(json.dumps(data, indent=2, ensure_ascii=False))

# 3. 下载视频看看
print("\n=== 下载视频测试 ===")
import subprocess, os
os.chdir("/opt/douyin-script/backend/downloads")
r = subprocess.run(["yt-dlp", "--no-download", "--print", "title", "--print", "id", url], 
                   capture_output=True, text=True, timeout=30)
print(f"yt-dlp stdout: {r.stdout}")
print(f"yt-dlp stderr: {r.stderr}")

# 4. 用 yt-dlp 看看能不能直接下载
print("\n=== yt-dlp 直接测试 ===")
r2 = subprocess.run(["yt-dlp", "--dump-json", "--no-download", url], 
                    capture_output=True, text=True, timeout=30)
if r2.returncode == 0:
    info = json.loads(r2.stdout)
    print(f"标题: {info.get('title', 'N/A')}")
    print(f"ID: {info.get('id', 'N/A')}")
    print(f"描述: {info.get('description', 'N/A')[:200]}")
else:
    print(f"yt-dlp 失败: {r2.stderr}")
'''

stdin, stdout, stderr = ssh.exec_command(f'cd /opt/douyin-script/backend && source venv/bin/activate && python3 -c \'{test_code}\'', timeout=60)
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))

ssh.close()