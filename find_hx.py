import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('tiktokdownload_home.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 查找所有 hx- 属性
hx_attrs = re.findall(r'hx-[a-z-]+=["\']([^"\']+)["\']', html)
print(f'所有 hx 属性值:')
for attr in hx_attrs:
    print(f'  {attr}')

print('\n=== 查找包含 hx- 属性的标签 ===')

# 查找 form 标签及其 hx 属性
forms_with_hx = re.findall(r'<form[^>]*hx-[a-z-]+[^>]*>', html)
print(f'\n带 hx 属性的 form: {len(forms_with_hx)}')
for f in forms_with_hx:
    print(f'  {f}')

# 查找 button 标签及其 hx 属性
buttons_with_hx = re.findall(r'<button[^>]*hx-[a-z-]+[^>]*>', html)
print(f'\n带 hx 属性的 button: {len(buttons_with_hx)}')
for b in buttons_with_hx:
    print(f'  {b}')

# 查找所有包含 hx- 属性的标签
all_hx_tags = re.findall(r'<[a-z]+[^>]*hx-[a-z-]+=[^>]*>', html)
print(f'\n所有带 hx 属性的标签: {len(all_hx_tags)}')
for t in all_hx_tags[:20]:
    print(f'  {t[:200]}')

# 查找 script 标签中的 htmx 配置
scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
for i, script in enumerate(scripts):
    if 'htmx' in script.lower() or 'hx-' in script.lower() or 'fetch' in script.lower():
        print(f'\nScript {i+1} (包含 htmx/fetch):')
        print(script[:3000])
