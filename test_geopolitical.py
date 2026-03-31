import os, requests
from dotenv import load_dotenv
load_dotenv('c:/Users/aravn/.env')

api_key = os.getenv('NEWSDATA_API_KEY')
finnhub_key = os.getenv('FINNHUB_API_KEY')

print("=== NewsData.IO - Trump Iran ===")
try:
    r = requests.get('https://newsdata.io/api/1/news', params={
        'apikey': api_key,
        'q': 'trump iran',
        'language': 'en',
        'category': 'politics,business,world'
    }, timeout=30)
    data = r.json()
    print(f"  HTTP {r.status_code}")
    data = r.json()
    print(f"  Keys: {list(data.keys())}")
    results = data.get('results', [])
    if results and isinstance(results, list):
        for i, a in enumerate(results[:5], 1):
            title = a.get('title', '?') if isinstance(a, dict) else str(a)
            src = a.get('source_id', '?') if isinstance(a, dict) else '?'
            date = a.get('pubDate', '?') if isinstance(a, dict) else '?'
            print(f"  {i}. {title}")
            print(f"     Source: {src} | Date: {date}")
    else:
        print(f"  No results. Full response: {str(data)[:500]}")
except Exception as e:
    print(f"  Error: {e}")

print("\n=== Finnhub - General News ===")
try:
    r = requests.get('https://finnhub.io/api/v1/news', params={
        'category': 'general',
        'token': finnhub_key
    }, timeout=15)
    articles = r.json()
    relevant = [a for a in articles if 'iran' in (a.get('headline', '') + a.get('summary', '')).lower()]
    print(f"  Total articles: {len(articles)}, Iran mentions: {len(relevant)}")
    for a in relevant[:5]:
        print(f"  - {a['headline'][:120]}")
    if not relevant:
        print("  No Iran mentions. Sample headlines:")
        for a in articles[:5]:
            print(f"  - {a['headline'][:120]}")
except Exception as e:
    print(f"  Error: {e}")
