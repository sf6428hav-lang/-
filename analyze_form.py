import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

# 读取保存的HTML
with open('tiktokdownload_home.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 提取表单及其上下文
forms = re.findall(r'<form[^>]*>(.*?)</form>', html, re.DOTALL)
print(f'找到 {len(forms)} 个表单\n')

for i, form in enumerate(forms):
    print(f'=== 表单 {i+1} ===')
    print(f'内容:\n{form}\n')
    
    # 查找表单前后的JavaScript
    form_pos = html.find(form)
    if form_pos > 0:
        # 查找表单前的script标签
        before_form = html[max(0, form_pos-2000):form_pos]
        scripts_before = re.findall(r'<script[^>]*>(.*?)</script>', before_form, re.DOTALL)
        if scripts_before:
            print(f'表单前的JavaScript ({len(scripts_before)} 个):')
            for j, script in enumerate(scripts_before[-3:]):  # 最后3个
                if script.strip():
                    print(f'\nScript {j+1}:')
                    print(script[:1000])
    
    # 查找表单后的JavaScript
    after_form = html[form_pos+len(form):form_pos+len(form)+2000]
    scripts_after = re.findall(r'<script[^>]*>(.*?)</script>', after_form, re.DOTALL)
    if scripts_after:
        print(f'\n表单后的JavaScript ({len(scripts_after)} 个):')
        for j, script in enumerate(scripts_after[:3]):  # 前3个
            if script.strip():
                print(f'\nScript {j+1}:')
                print(script[:1000])

print('\n=== 查找全局JavaScript ===')

# 查找所有script标签
all_scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
print(f'总共找到 {len(all_scripts)} 个script标签\n')

# 查找包含表单提交的JavaScript
for i, script in enumerate(all_scripts):
    if 'submit' in script.lower() or 'fetch' in script.lower() or 'ajax' in script.lower() or 'XMLHttpRequest' in script:
        print(f'\nScript {i+1} 包含表单/网络请求相关代码:')
        print(script[:2000])
        print('\n' + '='*60 + '\n')
