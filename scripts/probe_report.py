import requests
import json
import os
from pathlib import Path

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://data.eastmoney.com/',
}

report_name = os.environ['REPORT_NAME']
filter_str  = os.environ.get('FILTER', '')

url = 'https://datacenter-web.eastmoney.com/api/data/v1/get'
params = {
    'reportName': report_name,
    'columns': 'ALL',
    'sortTypes': '-1',
    'source': 'WEB',
    'client': 'WEB',
    'pageNumber': '1',
    'pageSize': '5',  # 只拿5条，够看字段就行
}
if filter_str:
    params['filter'] = filter_str

r = requests.get(url, params=params, headers=headers, timeout=10)
data = r.json()

result = {
    'report_name': report_name,
    'filter': filter_str,
    'success': data.get('success'),
    'message': data.get('message'),
    'fields': [],
    'sample': [],
}

if data.get('success') and data.get('result'):
    rows = data['result'].get('data') or []
    if rows:
        result['fields'] = list(rows[0].keys())
        result['sample'] = rows[:2]  # 保存2条样本
        print(f'✅ 成功！字段数: {len(result["fields"])}')
        print('字段列表:')
        for f in result['fields']:
            print(f'  {f}')
    else:
        print('⚠️ 请求成功但无数据行')
else:
    print(f'❌ 失败: {data.get("message")}')

# 保存结果
Path('results/report_fields').mkdir(parents=True, exist_ok=True)
out_path = f'results/report_fields/{report_name}.json'
Path(out_path).write_text(json.dumps(result, indent=2, ensure_ascii=False))
print(f'\n结果已保存到 {out_path}')
