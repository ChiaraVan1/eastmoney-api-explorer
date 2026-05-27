import requests
import re
from pathlib import Path

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://data.eastmoney.com/',
}

PAGES = [
    ('https://quote.eastmoney.com/zs980080.html', 'https://quote.eastmoney.com'),
    ('https://data.eastmoney.com/gzfx/detail/600519.html', 'https://data.eastmoney.com'),
    ('https://data.eastmoney.com/xg/xg/', 'https://data.eastmoney.com'),
    ('https://data.eastmoney.com/bbsj/', 'https://data.eastmoney.com'),
]

found_rpts = set()
found_js = set()

for page_url, base_url in PAGES:
    try:
        r = requests.get(page_url, headers={'User-Agent': headers['User-Agent'], 'Referer': base_url + '/'}, timeout=10)
        print(f'{page_url}: {r.status_code}')
        if r.status_code != 200:
            continue

        # 直接在 HTML 里找 RPT_
        rpts = re.findall(r'RPT_[A-Z0-9_]+', r.text)
        found_rpts.update(rpts)
        print(f'  HTML 直接找到 {len(rpts)} 个')

        # 收集 JS 链接
        js_links = re.findall(r'["\']((?:https?:)?//[^"\']+\.js[^"\']*)["\']', r.text)
        js_links += re.findall(r'src=["\'](/[^"\']+\.js[^"\']*)["\']', r.text)
        for link in js_links:
            if link.startswith('//'):
                link = 'https:' + link
            elif link.startswith('/'):
                link = base_url + link
            found_js.add(link)

    except Exception as e:
        print(f'{page_url} 失败: {e}')

print(f'\n共找到 {len(found_js)} 个 JS 文件，开始扫描...')
for link in sorted(found_js):
    try:
        js = requests.get(link, headers=headers, timeout=10)
        rpts = re.findall(r'RPT_[A-Z0-9_]+', js.text)
        if rpts:
            found_rpts.update(rpts)
            print(f'  {link}: +{len(rpts)} 个')
    except Exception as e:
        print(f'  {link} 失败: {e}')

Path('results').mkdir(exist_ok=True)
sorted_rpts = sorted(found_rpts)
Path('results/report_names.txt').write_text('\n'.join(sorted_rpts))

print(f'\n共发现 {len(sorted_rpts)} 个报表名:')
for r in sorted_rpts:
    print(f'  {r}')
