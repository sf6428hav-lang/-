import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('185.213.175.66', username='root', password='@3h09m6hHvLb', timeout=10)

# 1. 检查下载的视频文件
print("=== 下载的视频 ===")
stdin, stdout, stderr = ssh.exec_command('ls -lh /opt/douyin-script/backend/downloads/*.mp4 | tail -5')
print(stdout.read().decode())

# 2. 用ffprobe检查视频元数据
print("\n=== 视频元数据 ===")
stdin, stdout, stderr = ssh.exec_command('ffprobe -v quiet -print_format json -show_format /opt/douyin-script/backend/downloads/6ca0f698-a3e8-4485-9dff-569cf929a887.mp4 2>&1')
print(stdout.read().decode()[:1000])

# 3. 下载视频时到底用了什么URL
print("\n=== 下载日志 ===")
stdin, stdout, stderr = ssh.exec_command('grep -i "download" /tmp/project.log | tail -10')
print(stdout.read().decode())

# 4. 测试：直接用media-parser返回的video_url下载，看看内容
print("\n=== 重新下载测试 ===")
stdin, stdout, stderr = ssh.exec_command('cd /opt/douyin-script/backend/downloads && curl -L -o test_download.mp4 "https://v3-share.qznovel.com/66d446598de03b0e3284439edb9b9fff/6a9e31b5/video/tos/cn/tos-cn-v-6fcc8e/oMicEh0POOSIOt1etjkaaQiMHBGBglQABg90DA/?a=8662&ch=0&cr=7&dr=3&er=0&cd=0%7C0%7C0%7C1&cv=1&bt=1517&cs=0&ds=3&eid=38656&ft=Gb_rbuOFqyygZmo0P1FxbgkVQ9w6x&mime_type=video_mp4&qs=0&rc=O2Y8O2lmOTRmODkzNzNoOEBpamx0O3c5cmdyPDMzNGhoM0BjYDNeXmAwNWAxX140YDUyYSMwLS5hMmQ0bS5hLS1kXy9zcw%3D%3D&btag=c0000e00028000&dy_q=1788748558&end=30&feature_id=f0150a16a324336cda5d6dd0b69ed299&l=20260907103557597B6D99AE85881D3F43&start=0&tuola=mp4" 2>&1 | tail -5')
print(stdout.read().decode())

stdin, stdout, stderr = ssh.exec_command('ls -lh /opt/douyin-script/backend/downloads/test_download.mp4 2>/dev/null && ffprobe -v quiet -print_format json -show_format /opt/douyin-script/backend/downloads/test_download.mp4 2>&1')
print(stdout.read().decode()[:1000])

ssh.close()