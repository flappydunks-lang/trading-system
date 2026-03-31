"""Verify fixes: test Finnhub relevance filtering + NewsData with 30s timeout."""
import requests, json, os
from datetime import datetime, timedelta
from pathlib import Path

config = json.load(open('config/config.json'))
fk = config.get('finnhub_api_key', '')
nk = config.get('newsdata_api_key', '')

ticker = "NVDA"

# Test 1: Finnhub relevance
print("=" * 60)
print(f"FINNHUB RELEVANCE TEST - {ticker}")
print("=" * 60)
d1 = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
d2 = datetime.now().strftime('%Y-%m-%d')
r = requests.get(
    f'https://finnhub.io/api/v1/company-news?symbol={ticker}&from={d1}&to={d2}&token={fk}',
    timeout=15
)
items = r.json()
print(f"Total from API: {len(items)}")

# Simulate the relevance filter
relevant = []
irrelevant_samples = []
for item in items:
    headline = item.get('headline', '')
    summary = item.get('summary', '')
    text = (headline + ' ' + summary).lower()
    is_relevant = ('nvda' in text or '$nvda' in text or 'nvidia' in text)
    if is_relevant:
        relevant.append(headline)
    elif len(irrelevant_samples) < 5:
        irrelevant_samples.append(headline)

print(f"Relevant (mention NVDA/nvidia): {len(relevant)}")
print(f"Filtered out: {len(items) - len(relevant)}")
print(f"\nSample RELEVANT articles:")
for h in relevant[:5]:
    print(f"  ✓ {h[:90]}")
print(f"\nSample FILTERED OUT (irrelevant):")
for h in irrelevant_samples:
    print(f"  ✗ {h[:90]}")

# Test 2: NewsData with 30s timeout
print()
print("=" * 60)
print(f"NEWSDATA.IO TEST (30s timeout) - {ticker}")
print("=" * 60)
try:
    r = requests.get(
        'https://newsdata.io/api/1/news',
        params={'q': ticker, 'apikey': nk, 'language': 'en'},
        timeout=30
    )
    print(f"HTTP Status: {r.status_code}")
    data = r.json()
    results = data.get('results', [])
    print(f"Articles: {len(results)}")
    for a in results[:5]:
        print(f"  ✓ [{a.get('pubDate', '?')[:10]}] {a.get('title', '')[:90]}")
except requests.exceptions.Timeout:
    print("STILL timing out at 30s — their servers may be having issues")
except Exception as e:
    print(f"Error: {e}")

print()
print("=" * 60)
print("VERDICT")
print("=" * 60)
if len(relevant) > 0:
    print(f"✓ Finnhub: Will now feed {len(relevant)} RELEVANT articles instead of {len(items)} junk")
else:
    print("⚠ Finnhub: No relevant articles for NVDA this week")
