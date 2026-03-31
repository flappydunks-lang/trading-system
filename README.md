# FinalAI Quantum Trading - Web Interface

Convert your professional trading analysis system into a web application for friends!

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Web App
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501` in your browser.

### 3. Share with Friends
```
# Local Network (same WiFi)
http://[YOUR_IP]:8501

# Public Internet (expose with ngrok)
ngrok http 8501
# Share the URL with friends!
```

## 📚 Features

### 🏠 Dashboard
- Overview of all trading features
- Quick access to all analysis modules
- Performance metrics

### 📈 Stock Analysis
- Full technical analysis for any ticker
- AI-powered trade signals with confidence
- Support/Resistance levels
- Risk:Reward ratios
- Entry, stop loss, and take profit targets

### 🔍 Market Scanner
- Scan 50+ stocks simultaneously
- Auto-detect trading opportunities
- Filter by confidence level
- Risk:Reward ranking

### 📰 News & Sentiment
- Real-time headlines for any stock
- Sentiment analysis (positive/negative/neutral)
- SEC filings tracking
- Insider trading activity

### 💼 Portfolio Tools
- Efficient Frontier analysis
- Risk Parity optimization
- Correlation matrix visualization
- Sharpe ratio optimization

### 📊 Technical Analysis
- 80+ technical indicators
- Interactive candlestick charts
- RSI, MACD, Bollinger Bands, ATR, ADX
- Ichimoku, Keltner Channels, Williams %R
- Support/Resistance detection

### 🤖 AI Strategies
- Momentum strategy
- Mean reversion strategy
- Multi-factor analysis
- Pairs trading
- ML classification

### 📝 Paper Trading
- Risk-free virtual trading
- Track open positions
- Monitor P&L in real-time
- Performance analytics

### 🎯 Theme Research
- AI-powered theme analysis
- Investment opportunity discovery
- Risk factor identification
- Company rankings by relevance

## 🔑 API Keys (Optional)

### For Full AI Analysis
1. Get [Anthropic API key](https://console.anthropic.com)
   - Free tier available
   - Set env var: `ANTHROPIC_API_KEY`

### For Real-time Intraday Data
1. Get [Polygon.io API key](https://polygon.io)
   - Free tier: 5 calls/minute
   - Set env var: `POLYGON_API_KEY`

### For Telegram Alerts
1. Create bot via @BotFather on Telegram
2. Get your chat ID from @userinfobot
3. Set env vars:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_IDS`

## 💻 System Requirements

- Python 3.8+
- 4GB RAM minimum
- Internet connection (for market data)
- Modern web browser (Chrome, Safari, Firefox, Edge)

## 🌐 Deployment Options

### Option 1: Streamlit Cloud (Free)
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo and deploy
4. Share public link with friends

### Option 2: ngrok (Public Internet)
```bash
pip install ngrok
streamlit run app.py
# In another terminal:
ngrok http 8501
# Share ngrok URL with friends
```

### Option 3: Heroku (Paid)
```bash
heroku create your-app-name
git push heroku main
```

### Option 4: AWS/Google Cloud (Enterprise)
- Use Docker container
- Scale as needed
- Production-ready infrastructure

## 🔒 Security Notes

- Don't share API keys in URLs
- Use environment variables for secrets
- Rate limit requests if exposing publicly
- Add authentication for production

## 📱 Mobile Access

The web app is fully responsive and works on:
- Desktop browsers
- Tablets (iPad, Android tablets)
- Mobile phones (iOS Safari, Chrome Mobile)

## 🆘 Troubleshooting

### "ModuleNotFoundError: No module named 'Trading'"
- Make sure `Trading.py` is in the same directory as `app.py`
- Or add path: `sys.path.insert(0, '/path/to/Trading.py')`

### "API key not found"
- Set environment variables in PowerShell:
  ```powershell
  setx ANTHROPIC_API_KEY "your-key-here"
  ```
- Or create `.env` file in project directory:
  ```
  ANTHROPIC_API_KEY=your-key-here
  POLYGON_API_KEY=your-key-here
  ```

### "No data for ticker"
- Ensure ticker exists (e.g., AAPL, MSFT, NVDA)
- Check internet connection
- Try a different ticker

## 📊 Example Workflows

### For Your Friends:
1. **Quick Signal Check** → Stock Analysis → Enter ticker → Get BUY/SELL signal
2. **Scan for Opportunities** → Market Scanner → Select universe → Get ranked opportunities
3. **Portfolio Review** → Portfolio Tools → Enter holdings → Get optimization suggestions
4. **Theme Research** → Theme Research → Enter theme (AI, Quantum, EV) → Get AI analysis

## 🎯 Next Steps

1. **Customize the universe** - Edit market universes in `MARKET_UNIVERSES` dict
2. **Add more strategies** - Create custom strategy classes
3. **Connect to your broker** - Add order execution (Alpaca, Schwab, etc.)
4. **Add real-time alerts** - Integrate Telegram or Discord notifications
5. **Mobile app** - Convert to React Native or Flutter for app stores

## 📧 Support

For issues or questions:
- Check your API key configuration
- Verify internet connection
- Ensure Trading.py is in the same directory
- Check Streamlit logs: `streamlit run app.py --logger.level=debug`

## 🎉 Share Your Trading System!

You now have a professional trading dashboard to share with friends.

**To invite friends:**
1. Run locally: Share `http://[YOUR_IP]:8501` (same WiFi)
2. Deploy free: Use Streamlit Cloud
3. Deploy paid: Use ngrok, Heroku, or AWS

Enjoy professional-grade trading analysis! 🚀📈
