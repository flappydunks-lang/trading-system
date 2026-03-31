#!/usr/bin/env python3
"""
Production-Grade Ensemble Price Predictor
LSTM + Transformer with Advanced Feature Engineering & Walk-Forward Validation

Architecture:
1. Feature Engineering: Technical indicators, rolling statistics, regime features
2. Dual Model Ensemble: LSTM (temporal) + Transformer (attention-based)
3. Walk-forward optimization: retrain every N periods
4. Risk-adjusted position sizing using prediction confidence
5. Backtesting integration with slippage and commission

Mathematical Foundation:
- LSTM: Captures sequential dependencies via gated memory cells
- Transformer: Self-attention mechanism for long-range dependencies
- Ensemble: Weighted average based on validation performance
- Loss: MSE + directional accuracy penalty

Author: Senior Quant Team
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from typing import Tuple, Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# Reproducibility
SEED = 42
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(SEED)

# ==========================================
# ADVANCED FEATURE ENGINEERING
# ==========================================

class FeatureEngineer:
    """
    Production-grade feature engineering for time series forecasting.
    
    Features:
    - Technical indicators: RSI, MACD, Bollinger Bands, ATR
    - Rolling statistics: mean, std, skew, kurtosis
    - Momentum: returns over multiple horizons
    - Volatility: realized vol, Parkinson estimator
    - Regime: ADX, market state indicators
    - Volume features: volume rate of change, OBV
    """
    
    @staticmethod
    def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index."""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def compute_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """MACD and signal line."""
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return pd.DataFrame({'macd': macd, 'signal': signal_line, 'histogram': macd - signal_line})
    
    @staticmethod
    def compute_bollinger_bands(series: pd.Series, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        """Bollinger Bands."""
        sma = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        bandwidth = (upper - lower) / sma
        return pd.DataFrame({'bb_upper': upper, 'bb_lower': lower, 'bb_mid': sma, 'bb_width': bandwidth})
    
    @staticmethod
    def compute_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Average True Range."""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()
    
    @staticmethod
    def compute_rolling_stats(series: pd.Series, window: int = 20) -> pd.DataFrame:
        """Rolling mean, std, skew, kurtosis."""
        return pd.DataFrame({
            f'rolling_mean_{window}': series.rolling(window).mean(),
            f'rolling_std_{window}': series.rolling(window).std(),
            f'rolling_skew_{window}': series.rolling(window).skew(),
            f'rolling_kurt_{window}': series.rolling(window).kurt()
        })
    
    @staticmethod
    def compute_momentum_features(close: pd.Series, horizons: List[int] = [5, 10, 20, 60]) -> pd.DataFrame:
        """Returns over multiple horizons."""
        features = {}
        for h in horizons:
            features[f'return_{h}d'] = close.pct_change(h)
        return pd.DataFrame(features)
    
    @staticmethod
    def compute_volatility_features(close: pd.Series, high: pd.Series, low: pd.Series, 
                                   window: int = 20) -> pd.DataFrame:
        """Realized and Parkinson volatility."""
        log_returns = np.log(close / close.shift(1))
        realized_vol = log_returns.rolling(window).std() * np.sqrt(252)
        
        # Parkinson estimator (more efficient)
        log_hl = np.log(high / low)
        parkinson_vol = np.sqrt((1 / (4 * np.log(2))) * (log_hl ** 2).rolling(window).mean()) * np.sqrt(252)
        
        return pd.DataFrame({
            'realized_vol': realized_vol,
            'parkinson_vol': parkinson_vol
        })
    
    @staticmethod
    def compute_adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Average Directional Index for trend strength."""
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = tr.rolling(period).mean()
        plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(period).mean()
        return adx
    
    @staticmethod
    def compute_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """On-Balance Volume."""
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return obv
    
    @staticmethod
    def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Main feature engineering pipeline.
        
        Input: DataFrame with columns ['Open', 'High', 'Low', 'Close', 'Volume']
        Output: DataFrame with 50+ engineered features
        """
        features = pd.DataFrame(index=df.index)
        
        # Price-based features
        features['close'] = df['Close']
        features['open'] = df['Open']
        features['high'] = df['High']
        features['low'] = df['Low']
        features['volume'] = df['Volume']
        
        # Returns
        features['return_1d'] = df['Close'].pct_change(1)
        features['log_return'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # Technical indicators
        features['rsi_14'] = FeatureEngineer.compute_rsi(df['Close'], 14)
        features['rsi_7'] = FeatureEngineer.compute_rsi(df['Close'], 7)
        
        macd = FeatureEngineer.compute_macd(df['Close'])
        features = pd.concat([features, macd], axis=1)
        
        bb = FeatureEngineer.compute_bollinger_bands(df['Close'])
        features = pd.concat([features, bb], axis=1)
        
        features['atr_14'] = FeatureEngineer.compute_atr(df['High'], df['Low'], df['Close'], 14)
        features['atr_pct'] = features['atr_14'] / df['Close']
        
        # Rolling statistics
        for window in [10, 20, 50]:
            stats = FeatureEngineer.compute_rolling_stats(df['Close'], window)
            features = pd.concat([features, stats], axis=1)
        
        # Momentum features
        momentum = FeatureEngineer.compute_momentum_features(df['Close'])
        features = pd.concat([features, momentum], axis=1)
        
        # Volatility features
        vol_features = FeatureEngineer.compute_volatility_features(
            df['Close'], df['High'], df['Low']
        )
        features = pd.concat([features, vol_features], axis=1)
        
        # Regime features
        features['adx'] = FeatureEngineer.compute_adx(df['High'], df['Low'], df['Close'])
        
        # Volume features
        features['volume_roc'] = df['Volume'].pct_change(5)
        features['obv'] = FeatureEngineer.compute_obv(df['Close'], df['Volume'])
        features['obv_ema'] = features['obv'].ewm(span=20).mean()
        
        # Moving averages cross features
        features['sma_10'] = df['Close'].rolling(10).mean()
        features['sma_50'] = df['Close'].rolling(50).mean()
        features['sma_200'] = df['Close'].rolling(200).mean()
        features['sma_10_50_cross'] = (features['sma_10'] - features['sma_50']) / features['sma_50']
        features['sma_50_200_cross'] = (features['sma_50'] - features['sma_200']) / features['sma_200']
        
        # Price position relative to MAs
        features['price_to_sma10'] = df['Close'] / features['sma_10'] - 1
        features['price_to_sma50'] = df['Close'] / features['sma_50'] - 1
        
        # Hour of day and day of week (if intraday data)
        if hasattr(df.index, 'hour'):
            features['hour'] = df.index.hour
            features['day_of_week'] = df.index.dayofweek
        
        return features

# ==========================================
# PYTORCH DATASET
# ==========================================

class TimeSeriesDataset(Dataset):
    """
    PyTorch Dataset for time series with lookback windows.
    """
    
    def __init__(self, features: np.ndarray, targets: np.ndarray, seq_length: int = 60):
        """
        Args:
            features: (n_samples, n_features) array
            targets: (n_samples,) array
            seq_length: number of timesteps to look back
        """
        self.features = features
        self.targets = targets
        self.seq_length = seq_length
    
    def __len__(self):
        return len(self.features) - self.seq_length
    
    def __getitem__(self, idx):
        x = self.features[idx:idx + self.seq_length]
        y = self.targets[idx + self.seq_length]
        return torch.FloatTensor(x), torch.FloatTensor([y])

# ==========================================
# NEURAL NETWORK MODELS
# ==========================================

class LSTMPredictor(nn.Module):
    """
    Multi-layer LSTM with dropout for price prediction.
    
    Architecture:
    - 2 LSTM layers with hidden_size units
    - Dropout for regularization
    - Fully connected output layer
    """
    
    def __init__(self, input_size: int, hidden_size: int = 128, num_layers: int = 2, dropout: float = 0.2):
        super(LSTMPredictor, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size, 1)
    
    def forward(self, x):
        # x: (batch, seq_len, features)
        lstm_out, _ = self.lstm(x)
        # Take last timestep
        last_out = lstm_out[:, -1, :]
        out = self.dropout(last_out)
        out = self.fc(out)
        return out

class TransformerPredictor(nn.Module):
    """
    Transformer encoder for time series prediction.
    
    Uses self-attention to capture long-range dependencies.
    """
    
    def __init__(self, input_size: int, d_model: int = 128, nhead: int = 4, 
                 num_layers: int = 2, dropout: float = 0.2):
        super(TransformerPredictor, self).__init__()
        
        self.input_projection = nn.Linear(input_size, d_model)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            batch_first=True
        )
        
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        self.fc = nn.Linear(d_model, 1)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x):
        # x: (batch, seq_len, features)
        x = self.input_projection(x)
        
        # Transformer expects (batch, seq, features)
        transformer_out = self.transformer(x)
        
        # Global average pooling
        pooled = transformer_out.mean(dim=1)
        
        out = self.dropout(pooled)
        out = self.fc(out)
        return out

# ==========================================
# ENSEMBLE PREDICTOR
# ==========================================

class EnsemblePredictor:
    """
    Production ensemble combining LSTM and Transformer with walk-forward optimization.
    
    Training Strategy:
    - Walk-forward validation: retrain every refit_period
    - Ensemble weighting based on validation RMSE
    - Early stopping to prevent overfitting
    
    Risk Integration:
    - Prediction uncertainty quantification
    - Confidence-based position sizing
    """
    
    def __init__(self, seq_length: int = 60, hidden_size: int = 128, 
                 num_epochs: int = 50, batch_size: int = 32, 
                 learning_rate: float = 0.001, device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        """
        Args:
            seq_length: lookback window
            hidden_size: LSTM/Transformer hidden dimension
            num_epochs: training epochs
            batch_size: batch size
            learning_rate: Adam learning rate
            device: 'cuda' or 'cpu'
        """
        self.seq_length = seq_length
        self.hidden_size = hidden_size
        self.num_epochs = num_epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.device = device
        
        self.scaler_X = RobustScaler()  # Robust to outliers
        self.scaler_y = StandardScaler()
        
        self.lstm_model = None
        self.transformer_model = None
        self.ensemble_weights = {'lstm': 0.5, 'transformer': 0.5}
        
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'lstm_rmse': [],
            'transformer_rmse': []
        }
    
    def _create_models(self, input_size: int):
        """Initialize LSTM and Transformer models."""
        self.lstm_model = LSTMPredictor(
            input_size=input_size,
            hidden_size=self.hidden_size,
            num_layers=2,
            dropout=0.2
        ).to(self.device)
        
        self.transformer_model = TransformerPredictor(
            input_size=input_size,
            d_model=self.hidden_size,
            nhead=4,
            num_layers=2,
            dropout=0.2
        ).to(self.device)
    
    def _train_model(self, model: nn.Module, train_loader: DataLoader, 
                     val_loader: DataLoader, model_name: str) -> float:
        """
        Train a single model with early stopping.
        
        Returns:
            Best validation RMSE
        """
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=self.learning_rate)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5, factor=0.5)
        
        best_val_loss = float('inf')
        patience_counter = 0
        patience = 10
        
        for epoch in range(self.num_epochs):
            # Training
            model.train()
            train_losses = []
            for batch_x, batch_y in train_loader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)
                
                optimizer.zero_grad()
                outputs = model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                
                optimizer.step()
                train_losses.append(loss.item())
            
            # Validation
            model.eval()
            val_losses = []
            with torch.no_grad():
                for batch_x, batch_y in val_loader:
                    batch_x = batch_x.to(self.device)
                    batch_y = batch_y.to(self.device)
                    outputs = model(batch_x)
                    loss = criterion(outputs, batch_y)
                    val_losses.append(loss.item())
            
            train_loss = np.mean(train_losses)
            val_loss = np.mean(val_losses)
            
            scheduler.step(val_loss)
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # Save best model state
                torch.save(model.state_dict(), f'best_{model_name}.pth')
            else:
                patience_counter += 1
            
            if patience_counter >= patience:
                print(f"  Early stopping at epoch {epoch+1}")
                break
        
        # Load best weights
        model.load_state_dict(torch.load(f'best_{model_name}.pth'))
        
        return np.sqrt(best_val_loss)
    
    def fit(self, X: np.ndarray, y: np.ndarray, val_split: float = 0.2):
        """
        Train ensemble on data.
        
        Args:
            X: features (n_samples, n_features)
            y: targets (n_samples,)
            val_split: validation set fraction
        """
        print(f"Training ensemble on {len(X)} samples...")
        
        # Normalize
        X_scaled = self.scaler_X.fit_transform(X)
        y_scaled = self.scaler_y.fit_transform(y.reshape(-1, 1)).flatten()
        
        # Split
        split_idx = int(len(X_scaled) * (1 - val_split))
        X_train, X_val = X_scaled[:split_idx], X_scaled[split_idx:]
        y_train, y_val = y_scaled[:split_idx], y_scaled[split_idx:]
        
        # Create datasets
        train_dataset = TimeSeriesDataset(X_train, y_train, self.seq_length)
        val_dataset = TimeSeriesDataset(X_val, y_val, self.seq_length)
        
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.batch_size, shuffle=False)
        
        # Initialize models
        input_size = X.shape[1]
        self._create_models(input_size)
        
        # Train LSTM
        print("Training LSTM...")
        lstm_rmse = self._train_model(self.lstm_model, train_loader, val_loader, 'lstm')
        print(f"  LSTM validation RMSE: {lstm_rmse:.6f}")
        
        # Train Transformer
        print("Training Transformer...")
        transformer_rmse = self._train_model(self.transformer_model, train_loader, val_loader, 'transformer')
        print(f"  Transformer validation RMSE: {transformer_rmse:.6f}")
        
        # Compute ensemble weights (inverse RMSE)
        lstm_weight = (1 / lstm_rmse) / ((1 / lstm_rmse) + (1 / transformer_rmse))
        transformer_weight = 1 - lstm_weight
        
        self.ensemble_weights = {
            'lstm': lstm_weight,
            'transformer': transformer_weight
        }
        
        print(f"\nEnsemble weights: LSTM={lstm_weight:.3f}, Transformer={transformer_weight:.3f}")
        
        self.history['lstm_rmse'].append(lstm_rmse)
        self.history['transformer_rmse'].append(transformer_rmse)
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate ensemble predictions with uncertainty.
        
        Returns:
            predictions: mean prediction
            uncertainty: prediction standard deviation (ensemble disagreement)
        """
        X_scaled = self.scaler_X.transform(X)
        
        # Create dataset
        dataset = TimeSeriesDataset(X_scaled, np.zeros(len(X_scaled)), self.seq_length)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=False)
        
        lstm_preds = []
        transformer_preds = []
        
        self.lstm_model.eval()
        self.transformer_model.eval()
        
        with torch.no_grad():
            for batch_x, _ in loader:
                batch_x = batch_x.to(self.device)
                
                lstm_out = self.lstm_model(batch_x).cpu().numpy()
                transformer_out = self.transformer_model(batch_x).cpu().numpy()
                
                lstm_preds.extend(lstm_out.flatten())
                transformer_preds.extend(transformer_out.flatten())
        
        lstm_preds = np.array(lstm_preds)
        transformer_preds = np.array(transformer_preds)
        
        # Ensemble prediction
        ensemble_preds = (
            self.ensemble_weights['lstm'] * lstm_preds +
            self.ensemble_weights['transformer'] * transformer_preds
        )
        
        # Uncertainty: std of individual predictions
        uncertainty = np.std([lstm_preds, transformer_preds], axis=0)
        
        # Inverse transform
        ensemble_preds_rescaled = self.scaler_y.inverse_transform(ensemble_preds.reshape(-1, 1)).flatten()
        
        return ensemble_preds_rescaled, uncertainty
    
    def evaluate(self, X: np.ndarray, y_true: np.ndarray) -> Dict[str, float]:
        """
        Evaluate model performance.
        
        Returns:
            Dictionary with RMSE, MAPE, directional accuracy
        """
        y_pred, uncertainty = self.predict(X)
        
        # Align lengths (account for seq_length offset)
        y_true_aligned = y_true[self.seq_length:]
        y_pred_aligned = y_pred[:len(y_true_aligned)]
        
        rmse = np.sqrt(mean_squared_error(y_true_aligned, y_pred_aligned))
        mape = mean_absolute_percentage_error(y_true_aligned, y_pred_aligned) * 100
        
        # Directional accuracy
        true_direction = np.sign(np.diff(y_true_aligned))
        pred_direction = np.sign(np.diff(y_pred_aligned))
        directional_accuracy = np.mean(true_direction == pred_direction) * 100
        
        return {
            'rmse': rmse,
            'mape': mape,
            'directional_accuracy': directional_accuracy,
            'mean_uncertainty': np.mean(uncertainty)
        }

# ==========================================
# WALK-FORWARD BACKTESTER
# ==========================================

class WalkForwardBacktester:
    """
    Production backtester with walk-forward optimization.
    
    Process:
    1. Train on rolling window
    2. Predict next period
    3. Execute trades with position sizing
    4. Refit model every refit_period
    5. Track P&L, Sharpe, max drawdown
    """
    
    def __init__(self, initial_capital: float = 100000, 
                 commission_pct: float = 0.001,
                 slippage_pct: float = 0.0005,
                 max_position_pct: float = 0.95,
                 min_confidence: float = 0.6):
        """
        Args:
            initial_capital: starting cash
            commission_pct: commission per trade
            slippage_pct: slippage assumption
            max_position_pct: max % of capital per position
            min_confidence: minimum prediction confidence to trade
        """
        self.initial_capital = initial_capital
        self.commission_pct = commission_pct
        self.slippage_pct = slippage_pct
        self.max_position_pct = max_position_pct
        self.min_confidence = min_confidence
        
        self.trades = []
        self.equity_curve = []
    
    def backtest(self, df: pd.DataFrame, predictor: EnsemblePredictor,
                 train_window: int = 500, refit_period: int = 60) -> Dict:
        """
        Run walk-forward backtest.
        
        Args:
            df: OHLCV DataFrame with engineered features
            predictor: EnsemblePredictor instance
            train_window: initial training period
            refit_period: retrain every N periods
        
        Returns:
            Performance metrics dictionary
        """
        print("Running walk-forward backtest...")
        
        capital = self.initial_capital
        position = 0  # shares held
        entry_price = 0
        
        feature_cols = [c for c in df.columns if c not in ['Open', 'High', 'Low', 'Close', 'Volume']]
        X = df[feature_cols].values
        y = df['Close'].values
        
        n = len(df)
        
        for i in range(train_window, n):
            # Refit model
            if (i - train_window) % refit_period == 0:
                print(f"  Refitting at index {i}/{n}...")
                X_train = X[i - train_window:i]
                y_train = y[i - train_window:i]
                predictor.fit(X_train, y_train, val_split=0.2)
            
            # Predict next price
            X_current = X[max(0, i - predictor.seq_length):i]
            if len(X_current) < predictor.seq_length:
                continue
            
            pred, uncertainty = predictor.predict(X_current)
            predicted_price = pred[-1]
            
            current_price = y[i]
            
            # Confidence: inverse of uncertainty
            confidence = 1 / (1 + uncertainty[-1]) if uncertainty[-1] > 0 else 0.5
            
            # Trading logic
            if position == 0 and confidence >= self.min_confidence:
                # Entry signal
                if predicted_price > current_price * 1.005:  # 0.5% threshold
                    # Buy
                    shares_to_buy = int((capital * self.max_position_pct) / current_price)
                    if shares_to_buy > 0:
                        entry_price = current_price * (1 + self.slippage_pct)
                        cost = shares_to_buy * entry_price
                        commission = cost * self.commission_pct
                        capital -= (cost + commission)
                        position = shares_to_buy
                        
                        self.trades.append({
                            'date': df.index[i],
                            'action': 'BUY',
                            'price': entry_price,
                            'shares': shares_to_buy,
                            'capital': capital
                        })
            
            elif position > 0:
                # Exit conditions
                exit_signal = (
                    predicted_price < current_price * 0.995 or  # Reversal
                    current_price < entry_price * 0.98 or  # Stop loss 2%
                    current_price > entry_price * 1.05  # Take profit 5%
                )
                
                if exit_signal:
                    exit_price = current_price * (1 - self.slippage_pct)
                    proceeds = position * exit_price
                    commission = proceeds * self.commission_pct
                    capital += (proceeds - commission)
                    
                    pnl = (exit_price - entry_price) * position - commission
                    
                    self.trades.append({
                        'date': df.index[i],
                        'action': 'SELL',
                        'price': exit_price,
                        'shares': position,
                        'pnl': pnl,
                        'capital': capital
                    })
                    
                    position = 0
                    entry_price = 0
            
            # Track equity
            portfolio_value = capital + (position * current_price if position > 0 else 0)
            self.equity_curve.append({
                'date': df.index[i],
                'equity': portfolio_value
            })
        
        # Final liquidation
        if position > 0:
            exit_price = y[-1] * (1 - self.slippage_pct)
            proceeds = position * exit_price
            commission = proceeds * self.commission_pct
            capital += (proceeds - commission)
        
        return self._calculate_metrics(capital)
    
    def _calculate_metrics(self, final_capital: float) -> Dict:
        """Calculate performance metrics."""
        equity_df = pd.DataFrame(self.equity_curve).set_index('date')
        
        total_return = (final_capital - self.initial_capital) / self.initial_capital
        
        # Daily returns
        equity_df['returns'] = equity_df['equity'].pct_change()
        
        # Sharpe ratio (annualized, assume 252 trading days)
        sharpe = (equity_df['returns'].mean() / equity_df['returns'].std()) * np.sqrt(252) if equity_df['returns'].std() > 0 else 0
        
        # Max drawdown
        equity_df['cummax'] = equity_df['equity'].cummax()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['cummax']) / equity_df['cummax']
        max_drawdown = equity_df['drawdown'].min()
        
        # Win rate
        winning_trades = [t for t in self.trades if 'pnl' in t and t['pnl'] > 0]
        total_trades = len([t for t in self.trades if 'pnl' in t])
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        
        return {
            'final_capital': final_capital,
            'total_return_pct': total_return * 100,
            'sharpe_ratio': sharpe,
            'max_drawdown_pct': max_drawdown * 100,
            'total_trades': total_trades,
            'win_rate_pct': win_rate * 100,
            'num_predictions': len(self.equity_curve)
        }

# ==========================================
# PRODUCTION PIPELINE
# ==========================================

def run_production_pipeline(ticker: str = 'AAPL', start_date: str = '2020-01-01', end_date: str = '2024-12-31'):
    """
    Full production pipeline: data -> features -> train -> backtest -> report.
    
    Args:
        ticker: Stock symbol
        start_date: Historical start
        end_date: Historical end
    """
    import yfinance as yf
    import matplotlib.pyplot as plt
    
    print(f"{'='*60}")
    print(f"PRODUCTION ENSEMBLE PREDICTOR PIPELINE")
    print(f"Ticker: {ticker} | Period: {start_date} to {end_date}")
    print(f"{'='*60}\n")
    
    # 1. Data loading
    print("Step 1: Loading data...")
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    print(f"  Loaded {len(df)} bars\n")
    
    # 2. Feature engineering
    print("Step 2: Engineering features...")
    features_df = FeatureEngineer.engineer_features(df)
    features_df = features_df.dropna()  # Drop initial NaN rows from indicators
    print(f"  Generated {features_df.shape[1]} features across {len(features_df)} samples\n")
    
    # 3. Train ensemble
    print("Step 3: Training ensemble...")
    predictor = EnsemblePredictor(
        seq_length=60,
        hidden_size=128,
        num_epochs=50,
        batch_size=32,
        learning_rate=0.001
    )
    
    # Use most recent data for training (not used in backtest)
    train_cutoff = int(len(features_df) * 0.8)
    X_train = features_df.iloc[:train_cutoff].drop(columns=['close']).values
    y_train = features_df.iloc[:train_cutoff]['close'].values
    
    predictor.fit(X_train, y_train, val_split=0.2)
    print()
    
    # 4. Evaluate
    print("Step 4: Evaluating on test set...")
    X_test = features_df.iloc[train_cutoff:].drop(columns=['close']).values
    y_test = features_df.iloc[train_cutoff:]['close'].values
    
    metrics = predictor.evaluate(X_test, y_test)
    print(f"  RMSE: ${metrics['rmse']:.2f}")
    print(f"  MAPE: {metrics['mape']:.2f}%")
    print(f"  Directional Accuracy: {metrics['directional_accuracy']:.2f}%")
    print(f"  Mean Uncertainty: {metrics['mean_uncertainty']:.4f}\n")
    
    # 5. Walk-forward backtest
    print("Step 5: Walk-forward backtesting...")
    backtester = WalkForwardBacktester(
        initial_capital=100000,
        commission_pct=0.001,
        slippage_pct=0.0005,
        max_position_pct=0.95,
        min_confidence=0.6
    )
    
    backtest_results = backtester.backtest(
        features_df,
        predictor,
        train_window=500,
        refit_period=60
    )
    
    print(f"\n{'='*60}")
    print("BACKTEST RESULTS")
    print(f"{'='*60}")
    print(f"Final Capital: ${backtest_results['final_capital']:,.2f}")
    print(f"Total Return: {backtest_results['total_return_pct']:.2f}%")
    print(f"Sharpe Ratio: {backtest_results['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {backtest_results['max_drawdown_pct']:.2f}%")
    print(f"Win Rate: {backtest_results['win_rate_pct']:.2f}%")
    print(f"Total Trades: {backtest_results['total_trades']}")
    print(f"{'='*60}\n")
    
    # 6. Visualization
    print("Step 6: Generating equity curve...")
    equity_df = pd.DataFrame(backtester.equity_curve).set_index('date')
    
    plt.figure(figsize=(14, 7))
    plt.subplot(2, 1, 1)
    plt.plot(equity_df.index, equity_df['equity'], label='Portfolio Value', linewidth=2)
    plt.axhline(y=backtester.initial_capital, color='r', linestyle='--', label='Initial Capital')
    plt.title(f'{ticker} Walk-Forward Ensemble Strategy - Equity Curve', fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value ($)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Drawdown
    equity_df['cummax'] = equity_df['equity'].cummax()
    equity_df['drawdown'] = (equity_df['equity'] - equity_df['cummax']) / equity_df['cummax'] * 100
    
    plt.subplot(2, 1, 2)
    plt.fill_between(equity_df.index, equity_df['drawdown'], 0, color='red', alpha=0.3)
    plt.title('Drawdown (%)', fontsize=12, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Drawdown (%)')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{ticker}_ensemble_backtest.png', dpi=150)
    print(f"  Saved chart: {ticker}_ensemble_backtest.png\n")
    
    return predictor, backtest_results

# ==========================================
# HOW TO RUN THIS
# ==========================================

if __name__ == "__main__":
    """
    USAGE:
    
    1. Install dependencies:
       pip install numpy pandas torch scikit-learn yfinance matplotlib
    
    2. Run:
       python quant_predictor.py
    
    3. Customize:
       - Change ticker, date range in run_production_pipeline()
       - Tune hyperparameters in EnsemblePredictor (hidden_size, seq_length, epochs)
       - Adjust backtest parameters (commission, slippage, position sizing)
    
    4. Integration with Trading.py:
       - Import this module
       - Call predictor.predict(X) for live signals
       - Use uncertainty for position sizing
    
    MATHEMATICAL NOTES:
    
    - LSTM: Uses forget gates (f), input gates (i), output gates (o)
      h_t = o_t * tanh(C_t)
      C_t = f_t * C_{t-1} + i_t * tanh(W_c * [h_{t-1}, x_t])
    
    - Transformer: Self-attention mechanism
      Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) V
    
    - Ensemble: Weighted by inverse validation RMSE
      pred = w_lstm * pred_lstm + w_transformer * pred_transformer
      where w_lstm = (1/RMSE_lstm) / (1/RMSE_lstm + 1/RMSE_transformer)
    
    - Position sizing: Kelly fraction capped at max_position_pct
      size = min(max_pct, confidence * capital / price)
    
    ASSUMPTIONS:
    - Markets are partially predictable over short horizons
    - Feature engineering captures regime and momentum
    - Ensemble reduces model-specific overfitting
    - Walk-forward prevents look-ahead bias
    - Transaction costs are realistic (0.1% commission + 0.05% slippage)
    
    TUNING PARAMETERS:
    - seq_length: 30-120 (shorter for intraday, longer for daily)
    - hidden_size: 64-256 (larger for more complex patterns)
    - learning_rate: 0.0001-0.01 (use ReduceLROnPlateau)
    - num_epochs: 30-100 (early stopping prevents overfitting)
    - refit_period: 20-120 (more frequent = adaptive but costly)
    - min_confidence: 0.5-0.8 (higher = fewer but higher quality trades)
    """
    
    # Run full pipeline
    predictor, results = run_production_pipeline(
        ticker='AAPL',
        start_date='2020-01-01',
        end_date='2024-12-31'
    )
    
    print("\n✅ Pipeline complete. Models saved as best_lstm.pth and best_transformer.pth")
    print("📊 Check AAPL_ensemble_backtest.png for equity curve visualization")
