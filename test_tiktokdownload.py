import sys
from curl_cffi import requests
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

print('=== 深入分析 tiktokdownload.online ===\n')

session = requests.Session()

# 访问主页
r_home = session.get('https://tiktokdownload.online/',
                    headers={'User-Agent': UA},
                    impersonate='chrome120',
                    timeout=15)

if r_home.status_code == 200:
    html = r_home.text
    
    # 保存完整HTML
    with open('tiktokdownload_home.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    # 提取所有表单
    forms = re.findall(r'<form[^>]*>(.*?)</form>', html, re.DOTALL)
    print(f'找到 {len(forms)} 个表单\n')
    
    for i, form in enumerate(forms):
        print(f'表单 {i+1}:')
        
        # 提取 action
        action_match = re.search(r'action=["\']([^"\']+)["\']', form)
        if action_match:
            action = action_match.group(1)
            print(f'  action: {action}')
        else:
            print('  action: 未找到')
            continue
        
        # 提取 method
        method_match = re.search(r'method=["\']([^"\']+)["\']', form, re.IGNORECASE)
        method = method_match.group(1).upper() if method_match else 'POST'
        print(f'  method: {method}')
        
        # 提取所有 input fields
        inputs = re.findall(r'<input[^>]*>', form)
        print(f'  inputs: {len(inputs)} 个')
        for inp in inputs:
            name_match = re.search(r'name=["\']([^"\']+)["\']', inp)
            type_match = re.search(r'type=["\']([^"\']+)["\']', inp)
            value_match = re.search(r'value=["\']([^"\']+)["\']', inp)
            placeholder_match = re.search(r'placeholder=["\']([^"\']+)["\']', inp)
            
            if name_match:
                name = name_match.group(1)
                type_val = type_match.group(1) if type_match else 'text'
                value = value_match.group(1) if value_match else ''
                placeholder = placeholder_match.group(1) if placeholder_match else ''
                print(f'    - {name} (type={type_val}, value={value}, placeholder={placeholder})')
        
        # 提取 textarea
        textareas = re.findall(r'<textarea[^>]*>', form)
        if textareas:
            print(f'  textareas: {len(textareas)} 个')
            for ta in textareas:
                name_match = re.search(r'name=["\']([^"\']+)["\']', ta)
                if name_match:
                    print(f'    - {name_match.group(1)}')
        
        # 提取 select
        selects = re.findall(r'<select[^>]*>', form)
        if selects:
            print(f'  selects: {len(selects)} 个')
        
        print()
    
    # 尝试提交第一个表单
    if forms:
        form = forms[0]
        action_match = re.search(r'action=["\']([^"\']+)["\']', form)
        if action_match:
            action = action_match.group(1)
            if not action.startswith('http'):
                action = 'https://tiktokdownload.online' + action
            
            # 收集所有 input fields
            form_data = {}
            inputs = re.findall(r'<input[^>]*>', form)
            for inp in inputs:
                name_match = re.search(r'name=["\']([^"\']+)["\']', inp)
                value_match = re.search(r'value=["\']([^"\']+)["\']', inp)
                type_match = re.search(r'type=["\']([^"\']+)["\']', inp)
                
                if name_match:
                    name = name_match.group(1)
                    value = value_match.group(1) if value_match else ''
                    type_val = type_match.group(1) if type_match else 'text'
                    
                    # 根据字段类型填充数据
                    if 'url' in name.lower() or 'link' in name.lower() or name == 'id':
                        form_data[name] = url
                    elif 'token' in name.lower() or 'csrf' in name.lower():
                        form_data[name] = value
                    elif type_val == 'hidden':
                        form_data[name] = value
                    else:
                        form_data[name] = value if value else 'test'
            
            print(f'提交表单: {action}')
            print(f'Data: {form_data}\n')
            
            # 提交表单
            r_form = session.post(action,
                                data=form_data,
                                headers={'User-Agent': UA, 'Referer': 'https://tiktokdownload.online/'},
                                impersonate='chrome120',
                                timeout=15)
            
            print(f'Status: {r_form.status_code}')
            print(f'Content-Type: {r_form.headers.get("content-type", "unknown")}')
            print(f'URL: {r_form.url}')
            
            # 保存响应
            with open('tiktokdownload_response.html', 'w', encoding='utf-8') as f:
                f.write(r_form.text)
            
            if r_form.status_code == 200:
                # 检查 JSON
                try:
                    data = r_form.json()
                    print(f'\n✅ JSON response')
                    print(f'Keys: {list(data.keys())[:10]}')
                    
                    # 深度分析
                    data_str = json.dumps(data, ensure_ascii=False, indent=2)
                    print(f'\n完整响应:')
                    print(data_str[:2000])
                    
                except Exception as e:
                    print(f'\n不是 JSON: {e}')
                    
                    # 检查 HTML
                    if 'video' in r_form.text.lower() or 'mp4' in r_form.text.lower():
                        print(f'\n🎬 HTML 包含视频引用')
                        video_urls = re.findall(r'https?://[^"\'<>\s]+', r_form.text)
                        video_cdn = [u for u in video_urls if 'douyinvod' in u or 'bytedance' in u or 'zjcdn' in u or 'douyin' in u.lower()]
                        if video_cdn:
                            print(f'✅ 找到 {len(video_cdn)} 个视频 URL!')
                            for i, vurl in enumerate(video_cdn[:5]):
                                print(f'  {i+1}. {vurl}')
                    else:
                        print(f'\nHTML 响应前500字符:')
                        print(r_form.text[:500])
            else:
                print(f'\n响应前500字符:')
                print(r_form.text[:500])

print('\n分析完成')
