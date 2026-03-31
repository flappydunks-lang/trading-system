"""Quick diagnostic: test all news APIs and show what data they return."""
import requests
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Load config
config = {}
config_path = Path("config/config.json")
if config_path.exists():
    with open(config_path) as f:
        config = json.load(f)

# Also load .env
env_path = Path(".env")
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k] = v.strip('"').strip("'")

fk = config.get('finnhub_api_key') or os.getenv('FINNHUB_API_KEY', '')
nk = config.get('newsdata_api_key') or os.getenv('NEWSDATA_API_KEY', '')
gk = config.get('groq_api_key') or os.getenv('GROQ_API_KEY', '')

ticker = "NVDA"

print("=" * 60)
print("API KEY STATUS")
print("=" * 60)
print(f"Finnhub:     {'SET (' + fk[:4] + '...)' if fk else 'MISSING'}")
print(f"NewsData.IO: {'SET (' + nk[:4] + '...)' if nk else 'MISSING'}")
print(f"Groq:        {'SET (' + gk[:4] + '...)' if gk else 'MISSING'}")
print()

# Test 1: Finnhub
print("=" * 60)
print(f"TEST 1: FINNHUB - Company News for {ticker}")
print("=" * 60)
if fk:
    try:
        d1 = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        d2 = datetime.now().strftime('%Y-%m-%d')
        r = requests.get(
            f'https://finnhub.io/api/v1/company-news?symbol={ticker}&from={d1}&to={d2}&token={fk}',
            timeout=10
        )
        print(f"HTTP Status: {r.status_code}")
        data = r.json()
        if isinstance(data, list):
            print(f"Articles returned: {len(data)}")
            for a in data[:5]:
                ts = a.get('datetime', 0)
                dt = datetime.fromtimestamp(ts) if ts else 'unknown'
                print(f"  [{dt}] {a.get('headline', '')[:90]}")
                print(f"    Source: {a.get('source', '?')} | URL: {a.get('url', '')[:70]}")
        else:
            print(f"Unexpected response: {str(data)[:300]}")
    except Exception as e:
        print(f"ERROR: {e}")
else:
    print("SKIPPED - no key")

print()

# Test 2: NewsData.IO
print("=" * 60)
print(f"TEST 2: NEWSDATA.IO - Ticker Search for {ticker}")
print("=" * 60)
if nk:
    try:
        r = requests.get(
            'https://newsdata.io/api/1/news',
            params={'q': ticker, 'apikey': nk, 'language': 'en'},
            timeout=10
        )
        print(f"HTTP Status: {r.status_code}")
        data = r.json()
        print(f"API status: {data.get('status')}")
        if data.get('message'):
            print(f"Message: {data['message'][:200]}")
        results = data.get('results', [])
        print(f"Articles returned: {len(results)}")
        for a in results[:5]:
            print(f"  [{a.get('pubDate', '?')}] {a.get('title', '')[:90]}")
            print(f"    Source: {a.get('source_id', '?')}")
    except Exception as e:
        print(f"ERROR: {e}")
else:
    print("SKIPPED - no key")

print()

# Test 3: Web scraping (Yahoo Finance)
print("=" * 60)
print(f"TEST 3: WEB SCRAPE - Yahoo Finance for {ticker}")
print("=" * 60)
try:
    from bs4 import BeautifulSoup
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    r = requests.get(f'https://finance.yahoo.com/quote/{ticker}/news/', headers=headers, timeout=10)
    print(f"HTTP Status: {r.status_code}")
    soup = BeautifulSoup(r.content, 'html.parser')
    # Count all links with substantial text
    links = soup.find_all('a', href=True)
    news_links = [l for l in links if l.get_text(strip=True) and len(l.get_text(strip=True)) > 20]
    print(f"Links with text > 20 chars: {len(news_links)}")
    for l in news_links[:5]:
        print(f"  - {l.get_text(strip=True)[:90]}")
        print(f"    href: {l['href'][:70]}")
except Exception as e:
    print(f"ERROR: {e}")

print()

# Test 4: Groq responsiveness
print("=" * 60)
print("TEST 4: GROQ - Quick response test")
print("=" * 60)
if gk:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=gk, base_url="https://api.groq.com/openai/v1")
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=100,
            messages=[{"role": "user", "content": "What is today's date? Just state the date."}]
        )
        print(f"Groq response: {resp.choices[0].message.content}")
        print(f"Model used: {resp.model}")
    except Exception as e:
        print(f"ERROR: {e}")
else:
    print("SKIPPED - no key")

print()
print("=" * 60)
print("DIAGNOSIS COMPLETE")
print("=" * 60)
