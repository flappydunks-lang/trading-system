# Production Ensemble ML Predictor - Installation & Usage

## 📦 Installation

### 1. Install PyTorch (CPU or GPU)

**CPU Version (Recommended for most users):**
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**GPU Version (NVIDIA CUDA 11.8):**
```powershell
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. Install Additional Dependencies
```powershell
pip install numpy pandas scikit-learn yfinance matplotlib seaborn
```

### 3. Verify Installation
```powershell
python -c "import torch; print(f'PyTorch {torch.__version__} installed successfully')"
```

---

## 🚀 Quick Start

### Standalone Usage (quant_predictor.py)

Run the full production pipeline:
```powershell
python quant_predictor.py
```

This will:
1. Download AAPL data (2020-2024)
2. Engineer 50+ features
3. Train LSTM + Transformer ensemble
4. Run walk-forward backtest
5. Generate equity curve visualization

**Output:**
- `best_lstm.pth` - Trained LSTM model
- `best_transformer.pth` - Trained Transformer model
- `AAPL_ensemble_backtest.png` - Performance chart

---

## 📊 Integration with Trading.py

The ensemble predictor is now integrated into **Option 1 (Analyze Stock/Crypto)**.

### How It Works:

1. **Launch Trading.py:**
   ```powershell
   python Trading.py
   ```

2. **Select Option 1:**
   - Enter ticker (e.g., `AAPL`)
   - Choose trading style (Day/Swing/Long-term)
   - Select advanced analysis mode

3. **View ML Forecast:**
   After technical analysis, you'll see two new panels:
   
   **🧮 Quantitative Finance:**
   - Risk-adjusted momentum rank
   - Mean reversion Z-score
   - Multi-factor composite (momentum + value + quality)
   - Market regime (bull/bear/sideways)
   - ML probability

   **🔮 ML Price Prediction:**
   - Next-day price forecast
   - 3-day and 7-day momentum extensions
   - Directional bias (BULLISH/BEARISH/NEUTRAL)
   - Prediction confidence
   - Ensemble uncertainty

### What You Get:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🔮 ML Price Prediction                  ┃
┃ ────────────────────────────────────── ┃
┃ Horizon   │ Prediction │ Change  │ Conf┃
┃ Next Day  │ $182.45    │ +1.2%   │ 78% ┃
┃ 3-Day     │ $185.30    │ +2.8%   │ ... ┃
┃ 7-Day     │ $189.12    │ +5.1%   │ ... ┃
┃                                         ┃
┃ Directional Bias: BULLISH | Unc: 0.023 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

---

## 🔧 Customization

### Adjust Model Parameters

Edit `_ml_price_forecast()` in `Trading.py`:

```python
predictor = EnsemblePredictor(
    seq_length=60,      # Lookback window (30-120)
    hidden_size=128,    # Model capacity (64-256)
    num_epochs=50,      # Training iterations (20-100)
    batch_size=32,      # Batch size (16-64)
    learning_rate=0.001 # Learning rate (0.0001-0.01)
)
```

**Recommendations:**
- **Day Trading:** `seq_length=30`, `num_epochs=20` (faster)
- **Swing Trading:** `seq_length=60`, `num_epochs=50` (balanced)
- **Long-term:** `seq_length=120`, `num_epochs=100` (deeper patterns)

### Tune Backtester

Edit `WalkForwardBacktester` parameters:

```python
backtester = WalkForwardBacktester(
    initial_capital=100000,     # Starting cash
    commission_pct=0.001,       # 0.1% per trade
    slippage_pct=0.0005,        # 0.05% slippage
    max_position_pct=0.95,      # Max 95% allocation
    min_confidence=0.6          # Minimum 60% confidence to trade
)
```

---

## 📈 Performance Metrics Explained

### Model Evaluation:
- **RMSE:** Root Mean Squared Error in dollars (lower = better)
- **MAPE:** Mean Absolute Percentage Error (lower = better)
- **Directional Accuracy:** % of correct up/down predictions (higher = better)

### Backtest Metrics:
- **Total Return:** Final portfolio value vs initial capital
- **Sharpe Ratio:** Risk-adjusted return (>1.5 is good, >2.0 is excellent)
- **Max Drawdown:** Largest peak-to-trough decline (lower = better)
- **Win Rate:** % of profitable trades (>55% is strong)

---

## 🧠 Mathematical Foundation

### LSTM (Long Short-Term Memory):
Captures sequential dependencies via gated memory:
```
f_t = σ(W_f · [h_{t-1}, x_t] + b_f)  # Forget gate
i_t = σ(W_i · [h_{t-1}, x_t] + b_i)  # Input gate
o_t = σ(W_o · [h_{t-1}, x_t] + b_o)  # Output gate
C_t = f_t ⊙ C_{t-1} + i_t ⊙ tanh(W_c · [h_{t-1}, x_t])
h_t = o_t ⊙ tanh(C_t)
```

### Transformer (Self-Attention):
Captures long-range dependencies without recurrence:
```
Attention(Q, K, V) = softmax(QK^T / √d_k) V
```

### Ensemble Weighting:
Inverse validation RMSE weighting:
```
w_lstm = (1/RMSE_lstm) / (1/RMSE_lstm + 1/RMSE_transformer)
pred = w_lstm × pred_lstm + w_transformer × pred_transformer
```

---

## ⚠️ Assumptions & Limitations

### Assumptions:
1. **Partial Predictability:** Markets exhibit short-term momentum/mean-reversion patterns
2. **Feature Informativeness:** Technical indicators capture exploitable signals
3. **Stationarity (weak):** Statistical properties don't change drastically
4. **Transaction Costs:** Realistic (0.1% commission + 0.05% slippage)

### Limitations:
1. **Black Swan Events:** Model cannot predict unprecedented events (COVID, flash crashes)
2. **Regime Changes:** Performance degrades during structural market shifts
3. **Overfitting Risk:** Walk-forward validation mitigates but doesn't eliminate
4. **Computational Cost:** LSTM+Transformer requires GPU for large-scale training
5. **Data Quality:** Garbage in = garbage out (ensure clean OHLCV data)

---

## 🎯 Best Practices

### 1. Use Walk-Forward Validation
- Retrain every 20-60 periods to adapt to regime changes
- Never use future data in training (strict temporal split)

### 2. Monitor Ensemble Disagreement
- High uncertainty = low confidence signal
- Skip trades when `uncertainty > threshold`

### 3. Combine with Fundamental Analysis
- ML predicts price, not value
- Use for timing, not stock selection

### 4. Risk Management
- Never allocate >95% to single position
- Use Kelly criterion for position sizing (capped)
- Respect stop-loss levels

### 5. Continuous Monitoring
- Track live Sharpe ratio
- Watch for degrading directional accuracy
- Retrain when performance slips

---

## 🔬 Advanced Usage

### Custom Feature Engineering:

```python
# Add your own features in FeatureEngineer class
@staticmethod
def compute_custom_indicator(df: pd.DataFrame) -> pd.Series:
    # Example: Kaufman Adaptive Moving Average
    change = abs(df['Close'] - df['Close'].shift(10))
    volatility = df['Close'].diff().abs().rolling(10).sum()
    efficiency_ratio = change / volatility
    return efficiency_ratio
```

### Multi-Asset Ensemble:

```python
# Train separate models for correlated assets
predictors = {}
for ticker in ['AAPL', 'MSFT', 'GOOGL']:
    predictors[ticker] = train_model(ticker)

# Aggregate predictions for portfolio-level forecast
```

### Hyperparameter Optimization:

```python
from sklearn.model_selection import ParameterGrid

param_grid = {
    'seq_length': [30, 60, 90],
    'hidden_size': [64, 128, 256],
    'learning_rate': [0.0001, 0.001, 0.01]
}

best_params = None
best_sharpe = -np.inf

for params in ParameterGrid(param_grid):
    predictor = EnsemblePredictor(**params)
    results = backtest(predictor)
    if results['sharpe_ratio'] > best_sharpe:
        best_sharpe = results['sharpe_ratio']
        best_params = params
```

---

## 📞 Support & Issues

**Common Issues:**

1. **"Import torch could not be resolved"**
   - Run: `pip install torch`
   - Verify: `python -c "import torch"`

2. **Out of Memory (GPU)**
   - Reduce `batch_size` to 16
   - Reduce `hidden_size` to 64
   - Use CPU: `device='cpu'`

3. **Slow Training**
   - Reduce `num_epochs` to 20-30
   - Enable GPU if available
   - Use smaller `seq_length`

4. **Poor Predictions**
   - Check data quality (no NaNs, gaps)
   - Increase `train_window` (500+ bars)
   - Add more features
   - Tune `refit_period`

---

## 📚 References

**Papers:**
- Hochreiter & Schmidhuber (1997): "Long Short-Term Memory"
- Vaswani et al. (2017): "Attention Is All You Need"
- Pardo (2008): "The Evaluation and Optimization of Trading Strategies"

**Libraries:**
- PyTorch: https://pytorch.org/docs/stable/index.html
- scikit-learn: https://scikit-learn.org/stable/
- yfinance: https://pypi.org/project/yfinance/

---

## ✅ Production Checklist

Before deploying live:

- [ ] Backtest on 3+ years of data
- [ ] Achieve Sharpe > 1.5 out-of-sample
- [ ] Verify walk-forward retraining works
- [ ] Test on multiple tickers
- [ ] Document model version & hyperparameters
- [ ] Set up monitoring dashboard
- [ ] Implement emergency stop (max drawdown kill switch)
- [ ] Paper trade for 1 month minimum
- [ ] Review SEC compliance (if applicable)
- [ ] Secure model files (no public access)

---

**Built by Senior Quant Team | Production-Ready | Open for Enhancement**
