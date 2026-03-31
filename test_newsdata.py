import requests, json
from pathlib import Path

config = json.load(open('config/config.json'))
nk = config.get('newsdata_api_key', '')

print('Testing NewsData.IO with 30s timeout...')
print(f'Key prefix: {nk[:6]}...')
try:
    r = requests.get(
        'https://newsdata.io/api/1/news',
        params={'q': 'NVDA', 'apikey': nk, 'language': 'en'},
        timeout=30
    )
    print(f'HTTP Status: {r.status_code}')
    data = r.json()
    print(f'Response keys: {list(data.keys())}')
    status = data.get('status')
    print(f'Status: {status}')
    msg = data.get('message')
    if msg:
        print(f'Message: {msg}')
    results = data.get('results')
    if results:
        print(f'Articles: {len(results)}')
        for a in results[:3]:
            title = a.get('title', '')
            print(f'  - {title[:90]}')
    else:
        print('No results returned.')
        print(f'Full response (first 500 chars): {json.dumps(data)[:500]}')
except requests.exceptions.Timeout:
    print('TIMED OUT even at 30 seconds')
except requests.exceptions.ConnectionError as e:
    print(f'CONNECTION ERROR: {e}')
except Exception as e:
    print(f'Error type: {type(e).__name__}: {e}')
