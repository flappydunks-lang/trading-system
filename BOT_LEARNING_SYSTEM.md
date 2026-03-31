# Trading Bot - Prediction Tracking & Learning System

## Overview

The trading bot now automatically tracks its predictions and learns from right/wrong calls. When it wakes up (next time you run it or make trades), it checks if past predictions were correct and analyzes patterns.

## How It Works

### 1. **Making a Prediction (Bot)**
When the bot analyzes a stock and makes a trading decision:
```
Bot: "I predict AAPL will go UP to $200 by Feb 15 (HIGH confidence)"
    ↓
Automatically saved to trading_predictions.json with:
  - Ticker: AAPL
  - Direction: UP
  - Target price: $200
  - Target date: 2026-02-15
  - Confidence: HIGH
  - Reasoning: Oversold RSI + positive earnings surprise
  - Sources cited: SEC, Finnhub, NewsData
  - Current price: $192 (entry price)
```

### 2. **Checking Outcomes (On Next Run)**
When bot wakes up or on startup:
```
Bot checks: "Was AAPL prediction correct?"
Current price: $198 ✅
Outcome: DIRECTION CORRECT (predicted UP, went UP)
Accuracy score: 92% (was $2 away from target)
Profit: +3.1%
    ↓
Automatically logged to database
```

### 3. **Learning from Patterns**
Bot analyzes ALL past predictions to find what works:
```
Analyzed 20 predictions:
  ✅ "Oversold" scenarios: 85% accuracy (7 out of 8)
  ✅ "Earnings surprise" scenarios: 80% accuracy (4 out of 5)
  ⚠️ "Rumor-based" scenarios: 40% accuracy (2 out of 5)
  
Learning: Focus on oversold + fundamentals, avoid rumors
```

### 4. **Improving Confidence Calibration**
Bot tracks if its confidence matches reality:
```
Predictions Bot said were "HIGH confidence": 70% actually correct
Predictions Bot said were "MEDIUM confidence": 55% actually correct
Predictions Bot said were "LOW confidence": 30% actually correct

Adjustment: Need to be more cautious on HIGH confidence calls!
```

## Classes Added

### `PredictionTracker`
Saves and loads predictions to `trading_predictions.json`

**Key Methods:**
- `save_prediction()` - Save a new prediction when bot makes a trade
- `get_pending_predictions()` - Get all predictions not yet verified
- `log_outcome()` - Record what actually happened to a prediction

**Data Structure:**
```json
{
  "prediction_id": "AAPL_20260203_143022",
  "ticker": "AAPL",
  "timestamp": "2026-02-03T14:30:22",
  "direction": "UP",
  "confidence": "HIGH",
  "price_at_prediction": 192.45,
  "target_price": 200.00,
  "target_date": "2026-02-15",
  "reasoning": "Oversold RSI + earnings surprise",
  "sources_cited": ["SEC Edgar", "Finnhub", "NewsData.IO"],
  "outcome": {
    "actual_price": 198.20,
    "outcome_date": "2026-02-08T10:15:00",
    "direction_correct": true,
    "accuracy_score": 92.3,
    "profit_pct": 3.1,
    "notes": "Beaten to target date, gap up on analyst upgrade"
  }
}
```

### `OutcomeAnalyzer`
Analyzes prediction accuracy and patterns

**Key Methods:**
- `check_and_update_outcomes()` - Check if predictions hit targets
- `get_accuracy_summary()` - Overall accuracy stats by confidence level
- `get_scenario_analysis()` - Which prediction types work best

**Output Example:**
```python
{
  "total_predictions": 25,
  "completed_outcomes": 18,
  "pending_outcomes": 7,
  "directional_accuracy_pct": 72.2,
  "average_accuracy_score": 81.5,
  "average_profit_pct": 2.4,
  "scenarios": {
    "HIGH": {"total": 8, "accuracy": 75.0, "avg_profit": 2.8},
    "MEDIUM": {"total": 7, "accuracy": 71.4, "avg_profit": 2.1},
    "LOW": {"total": 3, "accuracy": 66.7, "avg_profit": 1.5}
  }
}
```

### `LearningEngine`
Generates learning briefs for the bot

**Key Methods:**
- `get_bot_learning_brief()` - Generates summary for bot to review before trading

**Output Example:**
```
📊 YOUR TRADING BOT'S PREDICTION RECORD:

Overall Performance:
  • Total Predictions: 25
  • Completed: 18
  • Pending: 7
  • Directional Accuracy: 72.2%
  • Avg Accuracy Score: 81.5/100
  • Avg Profit: 2.4%

By Confidence Level:
  • HIGH: 75% accuracy (8 predictions, avg +2.8%)
  • MEDIUM: 71% accuracy (7 predictions, avg +2.1%)
  • LOW: 67% accuracy (3 predictions, avg +1.5%)

Best Performing Scenarios:
  • Oversold: 87% success (7 attempts)
  • Earnings: 80% success (5 attempts)
  • Breakout: 60% success (4 attempts)

Key Learning:
  ✅ You're best at: Oversold predictions (87% win rate)
  ⚠️  You struggle with: Rumor predictions (40% win rate)

🎯 Recommendation: Focus on high-confidence plays where you have >70% accuracy!
```

## PaperTradingManager Integration

Added 4 new methods to the paper trading system:

### `save_prediction_for_trade()`
When bot makes a trading decision, save it as a prediction
```python
self.paper_trading.save_prediction_for_trade(
    ticker="AAPL",
    direction="UP",
    target_price=200,
    target_date="2026-02-15",
    confidence="HIGH",
    reasoning="Oversold + earnings beat",
    sources=["SEC", "Finnhub"],
    current_price=192
)
```

### `check_prediction_outcomes()`
On startup, check all pending predictions
```python
results = self.paper_trading.check_prediction_outcomes()
# Returns: {"checked": 5, "updated": 2, "updated_predictions": ["AAPL_...", "TSLA_..."]}
```

### `get_bot_learning_summary()`
Get a brief for the bot to review before trading
```python
brief = self.paper_trading.get_bot_learning_summary()
print(brief)  # Prints learning dashboard
```

### `show_prediction_accuracy()`
Display the accuracy dashboard to user
```python
self.paper_trading.show_prediction_accuracy()
```

## Menu Option

**New Menu Option 16: "🤖 Bot Learning Dashboard"**

When selected:
1. Checks all pending predictions for outcomes
2. Displays learning brief (what bot learned)
3. Shows accuracy summary by confidence level
4. Lists best and worst performing prediction scenarios

## Usage Example

### Making a Prediction
```
User: "Analyze AAPL"
Bot: "AAPL is oversold with positive catalysts. Predict UP to $200 by Feb 15. HIGH confidence."
System: ✓ Prediction saved (ID: AAPL_20260203_143022)
```

### Next Session
```
User starts bot
System checks: "Any predictions to verify?"
  ✓ Updated AAPL prediction: UP to $200, actual $198 ✅ CORRECT
  ✓ Updated TSLA prediction: DOWN to $240, actual $242 ❌ INCORRECT
  
Learning Brief displays:
  📊 Overall: 72% directional accuracy
  ✅ Best scenario: Oversold patterns (85% success)
  ⚠️ Worst scenario: Rumors (40% success)
```

### View Dashboard
```
User selects Option 16: Bot Learning Dashboard
  ✓ Checked 7 pending predictions, updated 2
  
  🤖 Learning Brief:
    18 completed predictions
    72.2% directional accuracy
    HIGH confidence: 75% accuracy
    MEDIUM confidence: 71% accuracy
    
  Best Scenarios:
    ✅ Oversold: 87% (7 attempts)
    ✅ Earnings: 80% (5 attempts)
    
  Worst Scenarios:
    ⚠️ Rumors: 40% (5 attempts)
```

## Key Features

✅ **Automatic tracking** - Bot predictions saved automatically  
✅ **Outcome verification** - Checks current prices against targets  
✅ **Accuracy scoring** - Compares predicted target to actual price  
✅ **Pattern discovery** - Finds which scenarios (keywords) work best  
✅ **Confidence calibration** - Tracks if HIGH confidence = high accuracy  
✅ **P&L tracking** - Records profit % for each prediction  
✅ **Learning brief** - Bot reviews past performance before new trades  
✅ **Dashboard** - View accuracy and improvement areas  

## Data Storage

All predictions stored in: `trading_predictions.json`

Located in working directory, persists across sessions.

Format: JSON array of prediction objects

## Future Enhancements

Potential additions:
- Weighting high-accuracy scenarios in new prediction generation
- Adjusting confidence dynamically based on historical accuracy
- Setting minimum confidence thresholds before executing trades
- Tracking which sources (SEC vs Finnhub vs NewsData) are most reliable
- Automatic halt on low-accuracy scenarios
- Backtesting new predictions against historical accuracy patterns

---
**Feature:** Prediction Tracking & Learning System for Trading Bot  
**Status:** ✅ Complete and Integrated  
**Type:** Bot-only feature (NOT advisor)  
**Storage:** trading_predictions.json  
**Menu Location:** Option 16 (Bot Learning Dashboard)
