import requests
import json
from pathlib import Path

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://data.eastmoney.com/',
}

# 读 workflow 1 生成的报表名清单
report_names = Path('results/report_names.txt').read_text().splitlines()
report_names = [r.strip() for r in report_names if r.strip()]
print(f'共 {len(report_names)} 个报表名，开始探测...\n')

Path('results/report_fields').mkdir(parents=True, exist_ok=True)

url = 'https://datacenter-web.eastmoney.com/api/data/v1/get'

for report_name in report_names:
    params = {
        'reportName': report_name,
        'columns': 'ALL',
        'sortTypes': '-1',
        'source': 'WEB',
        'client': 'WEB',
        'pageNumber': '1',
        'pageSize': '5',
    }

    result = {
        'report_name': report_name,
        'success': False,
        'message': '',
        'fields': [],
        'sample': [],
    }

    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        data = r.json()

        result['success'] = data.get('success', False)
        result['message'] = data.get('message', '')

        if result['success'] and data.get('result'):
            rows = data['result'].get('data') or []
            if rows:
                result['fields'] = list(rows[0].keys())
                result['sample'] = rows[:2]
                print(f'✅ {report_name}: {len(result["fields"])} 个字段')
            else:
                print(f'⚠️  {report_name}: 请求成功但无数据')
        else:
            print(f'❌ {report_name}: {result["message"]}')

    except Exception as e:
        result['message'] = str(e)
        print(f'💥 {report_name}: {e}')

    out_path = Path(f'results/report_fields/{report_name}.json')
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))

print('\n全部完成，结果保存在 results/report_fields/')
