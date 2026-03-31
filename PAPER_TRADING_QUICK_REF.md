# 📝 Paper Trading - Quick Reference

## 🚀 Quick Start

### Open a Paper Trade
```
Menu → 1 → [Ticker] → Live Scan → Wait for signal → Choose "paper"
```

### View All Trades
```
Menu → 22
```

### Close Trade Manually
```
Menu → 24 → Select # → Confirm
```

---

## 🎯 Menu Options

| Option | Action |
|--------|--------|
| **22** | View paper trading summary |
| **23** | Run quantitative strategies |
| **24** | Close paper trade manually |

---

## 📊 What You'll See

### Open Trades Table
```
Ticker | Action | Entry   | Current | P&L            | Stop    | Target
AAPL   | LONG   | $180.50 | $185.00 | +$45 (+2.5%)   | $175.00 | $195.00
```

### Performance Stats
```
Total Trades: 15
Wins: 9 | Losses: 6
Win Rate: 60.0%
Total P&L: $450.00
Average P&L: $30.00
Best Trade: $120.00
```

---

## ✅ Auto-Close Rules

### LONG Trades
- Price ≤ Stop Loss → Close (stop hit)
- Price ≥ Take Profit → Close (target hit)

### SHORT Trades
- Price ≥ Stop Loss → Close (stop hit)
- Price ≤ Take Profit → Close (target hit)

---

## 💡 Pro Tips

1. **Test strategies risk-free** before live trading
2. **Monitor ML confidence** - >65% is good
3. **Check regime** - only trade with trend
4. **Review closed trades** - learn patterns
5. **Build history** - need 50+ trades for ML training

---

## 📁 File Locations

| File | Purpose |
|------|---------|
| `results/paper_trades.json` | All your trades |
| `test_paper_trading.py` | Test script |
| `PAPER_TRADING_FIXED.md` | Full documentation |

---

## 🐛 Common Issues

**"No price data"** → Wait 60s, retry  
**Trade not closing** → Use Menu 24  
**P&L shows N/A** → Price unavailable (normal)

---

## 🎓 Example Session

```bash
# 1. Start trading app
python Trading.py

# 2. Open paper trade
1 → AAPL → Live scan → paper

# 3. Check later
22

# 4. Close manually if needed
24 → 1 → Yes

# 5. View performance
22 → See stats
```

---

**All tests passed**: ✅  
**Ready to use**: Yes 🚀
