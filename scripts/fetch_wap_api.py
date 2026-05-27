import requests
import re
import json
from pathlib import Path

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
    'Referer': 'https://wap.eastmoney.com/',
}

r = requests.get(
    'https://wap.eastmoney.com/quote/stock/0.980080.html',
    headers=headers, timeout=10
)
print(f'WAP页面 status: {r.status_code}')

# 找 JS 文件
js_links = set()
for link in re.findall(r'["\']((?:https?:)?//[^"\']+\.js[^"\']*)["\']', r.text):
    if link.startswith('//'):
        link = 'https:' + link
    js_links.add(link)
print(f'找到 {len(js_links)} 个 JS 文件')

# 在页面和JS里找所有 eastmoney API URL
api_urls = set()
rpt_names = set()

def scan_text(text):
    # 找 RPT_
    rpt_names.update(re.findall(r'RPT_[A-Z0-9_]+', text))
    # 找 eastmoney API URL
    api_urls.update(re.findall(r'https?://[a-zA-Z0-9.\-]+eastmoney\.com/[^\s"\'<>]+', text))

scan_text(r.text)

for link in js_links:
    try:
        js = requests.get(link, headers=headers, timeout=10)
        scan_text(js.text)
        print(f'  扫描: {link}')
    except Exception as e:
        print(f'  失败: {link} - {e}')

# 保存结果
Path('results/wap_api').mkdir(parents=True, exist_ok=True)

result = {
    'rpt_names': sorted(rpt_names),
    'api_urls': sorted(api_urls),
}

Path('results/wap_api/980080.json').write_text(
    json.dumps(result, indent=2, ensure_ascii=False)
)

print(f'\nRPT_ 报表名 ({len(rpt_names)} 个):')
for r in sorted(rpt_names):
    print(f'  {r}')

print(f'\nAPI URLs ({len(api_urls)} 个):')
for u in sorted(api_urls):
    print(f'  {u}')
