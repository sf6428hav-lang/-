import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# Check current prompt
print("=== Current prompt ===")
stdin, stdout, stderr = ssh.exec_command('head -20 /opt/douyin-script/backend/app/prompt_template.py')
print(stdout.read().decode('utf-8'))

# Check the frame quality from the frames in the temp dir
# Let me extract frames manually to check
print("\n=== Extract sample frames to check ===")
stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend && mkdir -p /tmp/test_frames && ffmpeg -y -i downloads/6ca0f698-a3e8-4485-9dff-569cf929a887.mp4 -vf "fps=1,scale=640:-2" -q:v 10 /tmp/test_frames/frame_%04d.jpg 2>&1 | tail -3')
print(stdout.read().decode('utf-8'))

stdin, stdout, stderr = ssh.exec_command('ls -lh /tmp/test_frames/ | head -10')
print(stdout.read().decode('utf-8'))

ssh.close()