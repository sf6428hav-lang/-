import sys
from curl_cffi import requests
import re
import json

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/1CzGfFJVQD0/'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

print('=== Testing tiktokdownload.online with full browser simulation ===\n')

session = requests.Session()

# First, get the homepage and extract all JavaScript
r_home = session.get('https://tiktokdownload.online/',
                    headers={'User-Agent': UA},
                    impersonate='chrome120',
                    timeout=15)

print(f'Homepage: {r_home.status_code}')

# Look for any hidden tokens, CSRF, or session data
html = r_home.text

# Search for token patterns
token_patterns = [
    r'csrf[_-]?token["\']?\s*[:=]\s*["\']([^"\']+)["\']',
    r'_token["\']?\s*[:=]\s*["\']([^"\']+)["\']',
    r'session[_-]?id["\']?\s*[:=]\s*["\']([^"\']+)["\']',
    r'captcha[_-]?token["\']?\s*[:=]\s*["\']([^"\']+)["\']',
    r'grecaptcha\.execute\(["\']([^"\']+)["\']',
    r'sitekey["\']?\s*[:=]\s*["\']([^"\']+)["\']',
]

print('\nSearching for tokens/session data:')
for pattern in token_patterns:
    matches = re.findall(pattern, html, re.IGNORECASE)
    if matches:
        print(f'  Found: {pattern[:50]}')
        for m in matches[:3]:
            print(f'    -> {m[:100]}')

# Look for htmx configuration
htmx_configs = re.findall(r'hx-[a-z-]+=["\']([^"\']+)["\']', html)
print(f'\nhtmx configurations: {len(htmx_configs)}')
for config in htmx_configs:
    print(f'  {config}')

# Look for form data
forms = re.findall(r'<form[^>]*>(.*?)</form>', html, re.DOTALL)
print(f'\nForms: {len(forms)}')

for i, form in enumerate(forms[:3]):
    print(f'\nForm {i+1}:')
    
    # Extract inputs
    inputs = re.findall(r'<input[^>]*>', form)
    for inp in inputs:
        name_match = re.search(r'name=["\']([^"\']+)["\']', inp)
        value_match = re.search(r'value=["\']([^"\']+)["\']', inp)
        type_match = re.search(r'type=["\']([^"\']+)["\']', inp)
        
        if name_match:
            name = name_match.group(1)
            value = value_match.group(1) if value_match else '(empty)'
            inp_type = type_match.group(1) if type_match else 'text'
            print(f'  input: name={name}, type={inp_type}, value={value[:50]}')
