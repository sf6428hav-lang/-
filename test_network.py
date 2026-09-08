import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

services = [
    'https://tiktokdownload.online',
    'https://nowatermarkdl.com',
    'https://tiktokdownloader.com',
    'https://easydown.vip',
    'https://yinziai.com',
    'https://snaptik.life',
]

print('=== 深度网络请求分析 ===\n')

for base_url in services:
    print(f'\n{"="*60}')
    print(f'🔍 {base_url}')
    print(f'{"="*60}\n')
    
    session = requests.Session()
    
    try:
        # 访问主页
        r_home = session.get(base_url + '/',
                            headers={'User-Agent': UA},
                            impersonate='chrome120',
                            timeout=15)
        
        if r_home.status_code != 200:
            print(f'❌ 主页访问失败: {r_home.status_code}')
            continue
        
        print(f'✅ 主页访问成功')
        
        # 保存 cookies
        print(f'🍪 Cookies: {len(session.cookies)} 个')
        for cookie in list(session.cookies)[:5]:
            print(f'   {cookie.name}={cookie.value[:30]}...')
        
        # 分析 HTML 中的所有 URL
        html = r_home.text
        all_urls = re.findall(r'https?://[^"\'<>\s]+', html)
        api_urls = [u for u in all_urls if '/api/' in u or '/ajax' in u]
        print(f'🔗 API URLs: {len(api_urls)} 个')
        for u in api_urls[:5]:
            print(f'   {u}')
        
        # 查找 form 标签
        forms = re.findall(r'<form[^>]*>(.*?)</form>', html, re.DOTALL)
        print(f'📝 Forms: {len(forms)} 个')
        for i, form in enumerate(forms[:2]):
            print(f'   Form {i+1}:')
            # 提取 action
            action_match = re.search(r'action=["\']([^"\']+)["\']', form)
            if action_match:
                print(f'     action: {action_match.group(1)}')
            # 提取 input fields
            inputs = re.findall(r'<input[^>]*>', form)
            for inp in inputs[:5]:
                name_match = re.search(r'name=["\']([^"\']+)["\']', inp)
                type_match = re.search(r'type=["\']([^"\']+)["\']', inp)
                if name_match:
                    print(f'     input: {name_match.group(1)} ({type_match.group(1) if type_match else "text"})')
        
        # 尝试提交表单
        for form in forms[:1]:
            action_match = re.search(r'action=["\']([^"\']+)["\']', form)
            if action_match:
                action = action_match.group(1)
                if not action.startswith('http'):
                    action = base_url + action
                
                # 收集所有 input fields
                form_data = {}
                inputs = re.findall(r'<input[^>]*>', form)
                for inp in inputs:
                    name_match = re.search(r'name=["\']([^"\']+)["\']', inp)
                    value_match = re.search(r'value=["\']([^"\']+)["\']', inp)
                    if name_match:
                        name = name_match.group(1)
                        value = value_match.group(1) if value_match else ''
                        # 替换 URL 字段
                        if 'url' in name.lower() or 'link' in name.lower():
                            form_data[name] = url
                        elif 'token' in name.lower() or 'csrf' in name.lower():
                            form_data[name] = value
                        else:
                            form_data[name] = value
                
                print(f'\n📤 提交表单: {action}')
                print(f'   Data: {form_data}')
                
                r_form = session.post(action,
                                    data=form_data,
                                    headers={'User-Agent': UA, 'Referer': base_url + '/'},
                                    impersonate='chrome120',
                                    timeout=15)
                
                print(f'   Status: {r_form.status_code}')
                print(f'   Content-Type: {r_form.headers.get("content-type", "unknown")}')
                
                if r_form.status_code == 200:
                    # 检查 JSON
                    try:
                        data = r_form.json()
                        print(f'   ✅ JSON response')
                        print(f'   Keys: {list(data.keys())[:10]}')
                        data_str = json.dumps(data)
                        if 'video' in data_str.lower() or 'url' in data_str.lower():
                            print(f'   🎬 包含视频信息!')
                    except:
                        # 检查 HTML
                        if 'video' in r_form.text.lower() or 'mp4' in r_form.text.lower():
                            print(f'   🎬 HTML 包含视频引用')
                            video_urls = re.findall(r'https?://[^"\'<>\s]+', r_form.text)
                            video_cdn = [u for u in video_urls if 'douyinvod' in u or 'bytedance' in u or 'zjcdn' in u]
                            if video_cdn:
                                print(f'   ✅ 找到 {len(video_cdn)} 个视频 URL!')
                                print(f'   第一个: {video_cdn[0][:100]}...')
    
    except Exception as e:
        print(f'❌ 错误: {str(e)[:150]}')

print('\n\n=== 分析完成 ===\n')
