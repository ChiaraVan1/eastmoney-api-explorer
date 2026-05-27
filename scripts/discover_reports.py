import requests
import re
import json
from pathlib import Path

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://data.eastmoney.com/',
}

# 多扫几个页面，覆盖更多报表名
PAGES = [
    'https://data.eastmoney.com/gzfx/detail/980080.html',
    'https://data.eastmoney.com/gzfx/detail/600519.html',
    'https://data.eastmoney.com/center.html',
    'https://data.eastmoney.com/xg/xg/',
    'https://data.eastmoney.com/bbsj/',
]

found_rpts = set()
found_js = set()

for page_url in PAGES:
    try:
        r = requests.get(page_url, headers=headers, timeout=10)
        print(f'{page_url}: {r.status_code}')

        # 直接在页面 HTML 里找
        rpts = re.findall(r'RPT_[A-Z0-9_]+', r.text)
        found_rpts.update(rpts)

        # 收集 JS 链接
        js_links = re.findall(r'src="(https?://[^"]+\.js[^"]*)"', r.text)
        found_js.update(js_links)
    except Exception as e:
        print(f'{page_url} 失败: {e}')

# 扫 JS 文件
print(f'\n共找到 {len(found_js)} 个 JS 文件，开始扫描...')
for link in sorted(found_js):
    try:
        js = requests.get(link, headers=headers, timeout=10)
        rpts = re.findall(r'RPT_[A-Z0-9_]+', js.text)
        found_rpts.update(rpts)
        print(f'  {link}: +{len(rpts)} 个')
    except Exception as e:
        print(f'  {link} 失败: {e}')

# 保存结果
Path('results').mkdir(exist_ok=True)
sorted_rpts = sorted(found_rpts)
Path('results/report_names.txt').write_text('\n'.join(sorted_rpts))

print(f'\n共发现 {len(sorted_rpts)} 个报表名，已保存到 results/report_names.txt')
for r in sorted_rpts:
    print(f'  {r}')
