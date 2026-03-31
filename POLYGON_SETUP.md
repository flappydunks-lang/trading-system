# Polygon.io Setup Guide

## ✅ Integration Complete!

Your Trading.py now uses **Polygon.io for day trading** and **yfinance for everything else**.

---

## 📊 How It Works

### **Day Trading (Polygon.io)** - Real-time ⚡
Used for these intervals:
- ✅ 1 minute (`1m`)
- ✅ 5 minutes (`5m`)
- ✅ 15 minutes (`15m`)
- ✅ 30 minutes (`30m`)
- ✅ 1 hour (`1h`)

**Benefits:**
- Real-time data (no delay!)
- All exchanges aggregated
- Better accuracy than IEX
- Professional-grade data

### **Swing/Long-term (yfinance)** - Free 📈
Used for these intervals:
- ✅ Daily (`1d`)
- ✅ Weekly (`1wk`)
- ✅ Monthly (`1mo`)

**Benefits:**
- Completely free
- Unlimited calls
- Perfect for swing trading
- Historical data

---

## 🔑 Get Your Polygon.io API Key

### **Step 1: Sign Up (Free)**
1. Go to: https://polygon.io
2. Click "Get Free API Key"
3. Sign up with email
4. Verify your email

### **Step 2: Get Your Key**
1. Login to dashboard: https://polygon.io/dashboard/api-keys
2. Copy your API key (looks like: `ABC123xyz...`)

### **Step 3: Add to Trading.py**
Run preflight setup:
```powershell
python Trading.py
# Choose option 18 (Preflight Setup)
```

Or manually add to `.env` file:
```
POLYGON_API_KEY="your-key-here"
```

Or set via PowerShell:
```powershell
setx POLYGON_API_KEY "your-key-here"
```

---

## 📊 Free Tier Limits

**What you get FREE:**
- ✅ 5 API calls per minute
- ✅ Real-time stock data
- ✅ 2 years historical data
- ✅ All exchanges (SIP equivalent)
- ✅ Crypto & forex data

**Is 5 calls/min enough?**
- ✅ Yes for monitoring 1-5 stocks
- ✅ Yes for focused day trading
- ❌ No for scanning 50+ tickers
- ❌ No for high-frequency strategies

**Example:** Scan 1 stock every 60 seconds = 1 call/min ✅

---

## 💰 Upgrade Options

### **Starter Plus - $29/month**
- Unlimited API calls
- Perfect for active day traders
- Scan as many stocks as you want

### **When to upgrade?**
- You day trade frequently
- Need to scan 10+ stocks simultaneously
- Hit the 5 calls/min limit often

---

## 🚀 Using Polygon in Trading.py

### **Automatic Mode**
The app automatically chooses the best data source:

1. Select **Day Trading** mode (option 1 in analyze ticker)
2. Choose **1m-1h interval**
3. Polygon.io is used automatically! 📊

### **What You'll See**
```
📊 Day trading mode: Using Polygon.io for 5m data
✓ Polygon.io: Fetched 390 bars for AAPL
```

### **If Polygon Fails**
```
Polygon rate limit hit, falling back to yfinance
📈 Using yfinance for 5m data
```

The app gracefully falls back to yfinance if:
- No API key configured
- Rate limit exceeded (5/min)
- Polygon API error
- Network issue

---

## 🧪 Test Your Setup

### **1. Add API Key**
```powershell
python Trading.py
# Option 18 → Enter Polygon key
```

### **2. Test Day Trading**
```powershell
python Trading.py
# Option 1 (Analyze ticker)
# Enter: AAPL
# Choose: Day Trading (1)
# Interval: 5 minutes
```

Watch for:
```
📊 Day trading mode: Using Polygon.io for 5m data
✓ Polygon.io: Fetched 390 bars for AAPL
```

### **3. Test Swing Trading**
```powershell
# Option 1 (Analyze ticker)
# Enter: TSLA
# Choose: Swing Trading (2)
# Interval: Daily
```

Watch for:
```
📈 Using yfinance for 1d data
Successfully fetched 100 bars for TSLA
```

---

## ❓ FAQ

**Q: Do I need Polygon to use the app?**
A: No! It works fine with just yfinance. Polygon is optional for better day trading.

**Q: Can I use Alpaca instead?**
A: No, we removed Alpaca in favor of Polygon.io (better data, simpler setup).

**Q: What happens if I don't add a Polygon key?**
A: Everything still works! You'll use yfinance for all intervals (15-20 min delayed data).

**Q: Is the free tier enough?**
A: Yes for most traders! You can monitor a few stocks continuously. Upgrade if you need more.

**Q: Does the position monitor use Polygon?**
A: Yes! It automatically uses Polygon for intraday scanning if you have a key.

**Q: Can I switch back to yfinance?**
A: Yes, just don't set the POLYGON_API_KEY. The app auto-falls back.

---

## 🎯 Recommended Setup

**Beginner/Swing Trader:**
- Use yfinance only (no Polygon needed)
- Analyze daily/weekly charts
- Zero cost

**Active Day Trader:**
- Get Polygon free tier
- Monitor 1-5 stocks
- Real-time 5m/15m charts

**Professional Day Trader:**
- Upgrade to Polygon Starter Plus ($29/mo)
- Unlimited scanning
- Multi-ticker monitoring

---

## 🔧 Troubleshooting

**"No Polygon key found"**
- Run preflight (option 18)
- Or add to .env: `POLYGON_API_KEY="..."`

**"Rate limit hit"**
- Free tier = 5 calls/min
- Wait 60 seconds or upgrade
- App auto-falls back to yfinance

**"Polygon API error"**
- Check your API key is correct
- Verify internet connection
- App will use yfinance instead

**Data looks wrong**
- Check ticker symbol is correct
- Try different interval
- Compare with yfinance data

---

## 📝 Summary

✅ **Day Trading (1m-1h)** → Polygon.io (real-time, 5 calls/min free)
✅ **Swing Trading (1d+)** → yfinance (free, unlimited)
✅ **Auto-fallback** → Always works even without Polygon
✅ **Optional** → Works great with or without Polygon key

**Get started:** https://polygon.io/dashboard/signup
