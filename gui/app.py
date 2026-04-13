"""FinalAI Quantum — Desktop Trading Application

Professional desktop GUI wrapping Trading.py.
Launch: python gui/app.py (or double-click the desktop shortcut)
"""

import os, sys, threading, json, queue
from pathlib import Path
from datetime import datetime, timedelta

# Ensure repo root is on path so Trading.py can be imported
REPO = Path(__file__).resolve().parent.parent
os.chdir(REPO)
sys.path.insert(0, str(REPO))

import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk

# Load .env before importing Trading
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except Exception:
    pass

# Dark theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Lazy import Trading.py (heavy) ──────────────────────────────────
_trading_mod = None
def T():
    global _trading_mod
    if _trading_mod is None:
        import importlib
        _trading_mod = importlib.import_module("Trading")
    return _trading_mod

# Thread-safe output queue for background tasks
_output_q = queue.Queue()


class OutputPanel(ctk.CTkFrame):
    """Scrollable text output panel with colored text."""

    def __init__(self, parent, **kw):
        super().__init__(parent, **kw)
        self.textbox = ctk.CTkTextbox(self, font=("Consolas", 13), wrap="word",
                                       state="disabled", fg_color="#1a1a2e")
        self.textbox.pack(fill="both", expand=True, padx=5, pady=5)

    def append(self, text, tag=None):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", text + "\n")
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def clear(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")


class StatusBar(ctk.CTkFrame):
    """Bottom status bar with broker + API status."""

    def __init__(self, parent, **kw):
        super().__init__(parent, height=30, **kw)
        self.label = ctk.CTkLabel(self, text="Initializing...", font=("Segoe UI", 11),
                                   text_color="#888888", anchor="w")
        self.label.pack(side="left", padx=10, fill="x", expand=True)

    def set(self, text):
        self.label.configure(text=text)


class AnalyzeTab(ctk.CTkFrame):
    """Stock/Crypto analysis tab."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # Top bar
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(top, text="Ticker:", font=("Segoe UI", 14)).pack(side="left", padx=(0, 5))
        self.ticker_entry = ctk.CTkEntry(top, width=120, placeholder_text="AAPL",
                                          font=("Segoe UI", 14))
        self.ticker_entry.pack(side="left", padx=5)
        self.ticker_entry.bind("<Return>", lambda e: self.run_analysis())

        ctk.CTkButton(top, text="Analyze", command=self.run_analysis,
                       font=("Segoe UI", 13, "bold"), width=100).pack(side="left", padx=10)

        self.style_var = ctk.StringVar(value="day")
        ctk.CTkSegmentedButton(top, values=["day", "swing", "long"],
                                variable=self.style_var, font=("Segoe UI", 12)).pack(side="left", padx=10)

        # Output
        self.output = OutputPanel(self)
        self.output.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def run_analysis(self):
        ticker = self.ticker_entry.get().strip().upper()
        if not ticker:
            return
        self.output.clear()
        self.output.append(f"Analyzing {ticker}...")
        self.app.status.set(f"Analyzing {ticker}...")

        def _work():
            try:
                mod = T()
                import yfinance as yf
                is_day = self.style_var.get() == "day"
                period = "5d" if is_day else ("3mo" if self.style_var.get() == "swing" else "1y")
                interval = "1m" if is_day else "1d"

                df = yf.download(ticker, period=period, interval=interval, progress=False)
                if hasattr(df.columns, 'levels'):
                    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
                if df is None or df.empty:
                    _output_q.put(("append", f"No data for {ticker}"))
                    return

                indicators = mod.TechnicalAnalyzer.calculate_indicators(df)
                if indicators is None:
                    _output_q.put(("append", "Could not calculate indicators"))
                    return

                price = float(df['Close'].iloc[-1])
                try:
                    import requests
                    fh = os.getenv('FINNHUB_API_KEY', '')
                    if fh:
                        r = requests.get(f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={fh}", timeout=3)
                        if r.status_code == 200:
                            c = r.json().get('c', 0)
                            if c > 0:
                                price = float(c)
                except Exception:
                    pass

                indicators.price = price
                indicators.close = price

                # Run analysis
                analyzer = mod.AIAnalyzer.__new__(mod.AIAnalyzer)
                analyzer.api_key = None
                signal = analyzer._fallback_analysis(
                    ticker, indicators, 100000, 0.01, desired_rrr=2.5,
                    is_day_trading=is_day)

                if signal is None:
                    _output_q.put(("append", "No signal generated"))
                    return

                # Format output
                lines = [
                    f"{'='*50}",
                    f"  {ticker} @ ${price:.2f}",
                    f"  Signal: {signal.action} ({signal.confidence:.0f}% confidence)",
                    f"  Stop Loss: ${signal.stop_loss:.2f}",
                    f"  Take Profit 1: ${signal.take_profit_1:.2f}",
                    f"  Take Profit 2: ${signal.take_profit_2:.2f}",
                    f"  Take Profit 3: ${signal.take_profit_3:.2f}",
                    f"{'='*50}",
                    f"",
                    f"  RSI(14): {indicators.rsi_14:.1f}",
                    f"  MACD: {indicators.macd:.4f} (Signal: {indicators.macd_signal:.4f})",
                    f"  ADX: {indicators.adx:.1f}" if indicators.adx else "",
                    f"  ATR: {indicators.atr:.4f} ({indicators.atr_percent:.2f}%)" if indicators.atr_percent else "",
                    f"  SMA20: {indicators.sma_20:.2f} | SMA50: {indicators.sma_50:.2f}",
                    f"  EMA8: {indicators.ema_8:.2f} | EMA21: {indicators.ema_21:.2f}",
                    f"  Volume Ratio: {indicators.volume_ratio:.2f}x" if indicators.volume_ratio else "",
                    f"  Market Regime: {indicators.market_regime}" if indicators.market_regime else "",
                    f"",
                    f"  Risk/Share: ${abs(price - signal.stop_loss):.2f}",
                    f"  Reward/Share: ${abs(signal.take_profit_1 - price):.2f}",
                    f"  R:R Ratio: 1:{abs(signal.take_profit_1 - price) / max(0.01, abs(price - signal.stop_loss)):.1f}",
                ]
                if hasattr(signal, 'primary_reason') and signal.primary_reason:
                    lines.append(f"\n  Reason: {signal.primary_reason}")
                if hasattr(signal, 'supporting_signals') and signal.supporting_signals:
                    lines.append(f"\n  Supporting signals:")
                    for s in signal.supporting_signals[:10]:
                        lines.append(f"    - {s}")

                _output_q.put(("clear", None))
                for line in lines:
                    if line:
                        _output_q.put(("append", line))
                _output_q.put(("status", f"{ticker}: {signal.action} @ ${price:.2f} ({signal.confidence:.0f}%)"))
            except Exception as e:
                _output_q.put(("append", f"Error: {e}"))
                _output_q.put(("status", f"Error analyzing {ticker}"))

        threading.Thread(target=_work, daemon=True).start()


class SwarmTab(ctk.CTkFrame):
    """Swarm Intelligence tab — 12 AI agents."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(top, text="Ticker:", font=("Segoe UI", 14)).pack(side="left", padx=(0, 5))
        self.ticker_entry = ctk.CTkEntry(top, width=120, placeholder_text="AAPL",
                                          font=("Segoe UI", 14))
        self.ticker_entry.pack(side="left", padx=5)

        ctk.CTkLabel(top, text="Rounds:", font=("Segoe UI", 13)).pack(side="left", padx=(15, 5))
        self.rounds_var = ctk.StringVar(value="3")
        ctk.CTkOptionMenu(top, values=["2", "3", "4", "5"], variable=self.rounds_var,
                           width=60, font=("Segoe UI", 12)).pack(side="left")

        ctk.CTkButton(top, text="Run Swarm", command=self.run_swarm,
                       font=("Segoe UI", 13, "bold"), width=120,
                       fg_color="#8B5CF6", hover_color="#7C3AED").pack(side="left", padx=10)

        self.output = OutputPanel(self)
        self.output.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def run_swarm(self):
        ticker = self.ticker_entry.get().strip().upper()
        if not ticker:
            return
        self.output.clear()
        self.output.append(f"Running Swarm Intelligence on {ticker} ({self.rounds_var.get()} rounds)...")
        self.output.append("This takes 1-3 minutes (12 agents x multiple rounds via Groq API)\n")

        def _work():
            try:
                mod = T()
                import yfinance as yf
                df = yf.download(ticker, period='5d', interval='1m', progress=False)
                if hasattr(df.columns, 'levels'):
                    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
                if df is None or df.empty:
                    _output_q.put(("append", f"No data for {ticker}"))
                    return

                indicators = mod.TechnicalAnalyzer.calculate_indicators(df)
                if indicators is None:
                    _output_q.put(("append", "Could not calculate indicators"))
                    return
                indicators.price = float(df['Close'].iloc[-1])

                swarm = mod.SwarmIntelligence()
                rounds = int(self.rounds_var.get())

                # Run swarm (this calls Groq API)
                result = swarm.analyze(ticker, indicators, rounds=rounds)

                action = result.get('action', 'HOLD')
                conf = result.get('confidence', 0)
                breakdown = result.get('breakdown', {})
                reasons = result.get('reasons', [])

                _output_q.put(("append", f"\n{'='*50}"))
                _output_q.put(("append", f"  CONSENSUS: {action} ({conf:.1f}% confidence)"))
                _output_q.put(("append", f"{'='*50}"))
                if breakdown:
                    _output_q.put(("append", f"\n  BUY:  {breakdown.get('buy', 0):.1f}%"))
                    _output_q.put(("append", f"  SELL: {breakdown.get('sell', 0):.1f}%"))
                    _output_q.put(("append", f"  HOLD: {breakdown.get('hold', 0):.1f}%"))
                if reasons:
                    _output_q.put(("append", "\n  Top reasons:"))
                    for r in reasons[:5]:
                        _output_q.put(("append", f"    - {r}"))

                # Leaderboard
                _output_q.put(("append", "\n  Agent Leaderboard:"))
                for a in sorted(swarm.agents, key=lambda x: x.accuracy, reverse=True):
                    _output_q.put(("append", f"    {a.name}: {a.accuracy*100:.0f}% acc, {a.weight:.1f}x weight ({a.total_calls} calls)"))

                _output_q.put(("status", f"Swarm: {action} on {ticker} ({conf:.0f}%)"))
            except Exception as e:
                _output_q.put(("append", f"\nError: {e}"))

        threading.Thread(target=_work, daemon=True).start()


class BacktestTab(ctk.CTkFrame):
    """Blind Prediction Test tab."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(top, text="Ticker:", font=("Segoe UI", 14)).pack(side="left", padx=(0, 5))
        self.ticker_entry = ctk.CTkEntry(top, width=100, placeholder_text="AAPL",
                                          font=("Segoe UI", 14))
        self.ticker_entry.pack(side="left", padx=5)

        ctk.CTkLabel(top, text="Start:", font=("Segoe UI", 13)).pack(side="left", padx=(10, 3))
        self.start_entry = ctk.CTkEntry(top, width=110, font=("Segoe UI", 13))
        self.start_entry.insert(0, (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'))
        self.start_entry.pack(side="left")

        ctk.CTkLabel(top, text="Cutoff:", font=("Segoe UI", 13)).pack(side="left", padx=(10, 3))
        self.cutoff_entry = ctk.CTkEntry(top, width=110, font=("Segoe UI", 13))
        self.cutoff_entry.insert(0, (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))
        self.cutoff_entry.pack(side="left")

        ctk.CTkLabel(top, text="Horizon:", font=("Segoe UI", 13)).pack(side="left", padx=(10, 3))
        self.horizon_var = ctk.StringVar(value="5")
        ctk.CTkOptionMenu(top, values=["3", "5", "10", "20"], variable=self.horizon_var,
                           width=60, font=("Segoe UI", 12)).pack(side="left")

        ctk.CTkButton(top, text="Test Prediction", command=self.run_test,
                       font=("Segoe UI", 13, "bold"), width=140,
                       fg_color="#059669", hover_color="#047857").pack(side="left", padx=10)

        self.output = OutputPanel(self)
        self.output.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def run_test(self):
        ticker = self.ticker_entry.get().strip().upper()
        start = self.start_entry.get().strip()
        cutoff = self.cutoff_entry.get().strip()
        horizon = int(self.horizon_var.get())
        if not ticker:
            return

        self.output.clear()
        self.output.append(f"Blind test: {ticker} | Window: {start} -> {cutoff} | Reveal: {horizon} days\n")

        def _work():
            try:
                mod = T()
                import yfinance as yf

                # Fetch analysis window only
                df = yf.download(ticker, start=start, end=cutoff, interval='1d', progress=False)
                if hasattr(df.columns, 'levels'):
                    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
                if df is None or len(df) < 20:
                    _output_q.put(("append", "Not enough data (need 20+ bars)"))
                    return

                price = float(df['Close'].iloc[-1])
                _output_q.put(("append", f"Bot sees {len(df)} candles ending at ${price:.2f}\n"))

                # Analyze
                indicators = mod.TechnicalAnalyzer.calculate_indicators(df)
                if indicators is None:
                    _output_q.put(("append", "Could not compute indicators"))
                    return
                indicators.price = price
                indicators.close = price

                analyzer = mod.AIAnalyzer.__new__(mod.AIAnalyzer)
                analyzer.api_key = None
                signal = analyzer._fallback_analysis(ticker, indicators, 100000, 0.01, desired_rrr=2.5)
                if signal is None:
                    _output_q.put(("append", "No signal"))
                    return

                _output_q.put(("append", f"PREDICTION: {signal.action} ({signal.confidence:.0f}%)"))
                _output_q.put(("append", f"SL: ${signal.stop_loss:.2f} | TP: ${signal.take_profit_1:.2f}\n"))

                # Reveal future
                end_reveal = (datetime.strptime(cutoff, '%Y-%m-%d') + timedelta(days=horizon + 5)).strftime('%Y-%m-%d')
                future = yf.download(ticker, start=cutoff, end=end_reveal, interval='1d', progress=False)
                if hasattr(future.columns, 'levels'):
                    future.columns = [c[0] if isinstance(c, tuple) else c for c in future.columns]
                future = future.head(horizon)

                if future.empty:
                    _output_q.put(("append", "No future data available"))
                    return

                final = float(future['Close'].iloc[-1])
                chg = (final - price) / price * 100

                correct = (signal.action == 'BUY' and chg > 0) or \
                          (signal.action == 'SELL' and chg < 0) or \
                          (signal.action == 'HOLD' and abs(chg) < 1.5)

                _output_q.put(("append", f"ACTUAL: ${price:.2f} -> ${final:.2f} ({chg:+.2f}%)"))
                _output_q.put(("append", f"VERDICT: {'CORRECT' if correct else 'WRONG'}\n"))

                _output_q.put(("append", "Future candles:"))
                for idx, row in future.iterrows():
                    d_chg = (float(row['Close']) - price) / price * 100
                    date_str = idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx)[:10]
                    _output_q.put(("append", f"  {date_str}: ${float(row['Close']):.2f} ({d_chg:+.2f}%)"))

                _output_q.put(("status", f"Backtest: {signal.action} -> {chg:+.1f}% = {'CORRECT' if correct else 'WRONG'}"))
            except Exception as e:
                _output_q.put(("append", f"Error: {e}"))

        threading.Thread(target=_work, daemon=True).start()


class PortfolioTab(ctk.CTkFrame):
    """IBKR portfolio and positions tab."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkButton(top, text="Refresh Positions", command=self.refresh,
                       font=("Segoe UI", 13), width=150).pack(side="left", padx=5)
        ctk.CTkButton(top, text="Account Info", command=self.show_account,
                       font=("Segoe UI", 13), width=130).pack(side="left", padx=5)

        self.output = OutputPanel(self)
        self.output.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def refresh(self):
        self.output.clear()
        self.output.append("Fetching IBKR positions...\n")

        def _work():
            try:
                mod = T()
                broker = mod.IBKRTrader()
                if not broker.is_ready():
                    _output_q.put(("append", "IBKR not connected. Start TWS first."))
                    return

                positions = broker.list_positions()
                if not positions:
                    _output_q.put(("append", "No open positions."))
                    broker.disconnect()
                    return

                total_pnl = 0
                _output_q.put(("append", f"{'Symbol':<10} {'Qty':>8} {'Side':<6} {'Entry':>10} {'P&L':>12}"))
                _output_q.put(("append", "-" * 50))
                for p in positions:
                    pnl = p.get('unrealized_pl', 0)
                    total_pnl += pnl
                    _output_q.put(("append",
                        f"{p['symbol']:<10} {p['qty']:>8.0f} {p['side']:<6} "
                        f"${p['avg_entry_price']:>9.2f} ${pnl:>+11.2f}"))
                _output_q.put(("append", "-" * 50))
                _output_q.put(("append", f"{'Total P&L:':<36} ${total_pnl:>+11.2f}"))
                broker.disconnect()
            except Exception as e:
                _output_q.put(("append", f"Error: {e}"))

        threading.Thread(target=_work, daemon=True).start()

    def show_account(self):
        self.output.clear()
        self.output.append("Fetching IBKR account...\n")

        def _work():
            try:
                mod = T()
                broker = mod.IBKRTrader()
                if not broker.is_ready():
                    _output_q.put(("append", "IBKR not connected. Start TWS first."))
                    return
                acct = broker.get_account()
                if acct:
                    _output_q.put(("append", f"  Status:       {acct.get('status', '?')}"))
                    _output_q.put(("append", f"  Cash:         ${acct.get('cash', 0):,.2f}"))
                    _output_q.put(("append", f"  Equity:       ${acct.get('equity', 0):,.2f}"))
                    _output_q.put(("append", f"  Buying Power: ${acct.get('buying_power', 0):,.2f}"))
                    _output_q.put(("append", f"\n  {broker.status_line()}"))
                else:
                    _output_q.put(("append", "Could not fetch account"))
                broker.disconnect()
            except Exception as e:
                _output_q.put(("append", f"Error: {e}"))

        threading.Thread(target=_work, daemon=True).start()


class SettingsTab(ctk.CTkFrame):
    """Settings and configuration."""

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # API Keys section
        ctk.CTkLabel(scroll, text="API Keys", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 10))

        self.key_entries = {}
        keys = [
            ("FINNHUB_API_KEY", "Finnhub (live equity prices)"),
            ("GROQ_API_KEY", "Groq (Swarm AI backend)"),
            ("NEWSDATA_API_KEY", "NewsData (news sentiment)"),
            ("NEWS_API_KEY", "News API (headlines)"),
            ("ANTHROPIC_API_KEY", "Anthropic (AI analysis)"),
        ]
        for env_name, label in keys:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=label, font=("Segoe UI", 12), width=250, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(row, show="*", font=("Segoe UI", 12))
            entry.pack(side="left", fill="x", expand=True, padx=5)
            val = os.getenv(env_name, "")
            if val:
                entry.insert(0, val)
            self.key_entries[env_name] = entry

        ctk.CTkButton(scroll, text="Save Keys", command=self.save_keys,
                       font=("Segoe UI", 13), width=120).pack(anchor="w", pady=10)

        # Trading config
        ctk.CTkLabel(scroll, text="Trading Configuration", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20, 10))

        try:
            config = json.loads(Path("config/config.json").read_text())
        except Exception:
            config = {}

        self.config_entries = {}
        settings = [
            ("account_size", "Account Size ($)", str(config.get("account_size", 100000))),
            ("auto_trade_risk_pct", "Risk Per Trade (%)", str(config.get("auto_trade_risk_pct", 1.0))),
            ("auto_trade_max_daily", "Max Trades/Day", str(config.get("auto_trade_max_daily", 30))),
            ("auto_trade_max_open_positions", "Max Open Positions", str(config.get("auto_trade_max_open_positions", 8))),
            ("auto_trade_max_daily_loss_pct", "Daily Loss Limit (%)", str(config.get("auto_trade_max_daily_loss_pct", 5.0))),
            ("auto_trade_min_confidence", "Min Confidence (%)", str(config.get("auto_trade_min_confidence", 80.0))),
        ]
        for key, label, default in settings:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=label, font=("Segoe UI", 12), width=250, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(row, font=("Segoe UI", 12), width=150)
            entry.insert(0, default)
            entry.pack(side="left", padx=5)
            self.config_entries[key] = entry

        ctk.CTkButton(scroll, text="Save Config", command=self.save_config,
                       font=("Segoe UI", 13), width=120).pack(anchor="w", pady=10)

        # Broker section
        ctk.CTkLabel(scroll, text="Broker", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(20, 10))
        self.broker_var = ctk.StringVar(value=os.getenv("BROKER", "alpaca"))
        ctk.CTkSegmentedButton(scroll, values=["alpaca", "ibkr"],
                                variable=self.broker_var, font=("Segoe UI", 13)).pack(anchor="w")
        ctk.CTkLabel(scroll, text="IBKR: TWS must be running on port 7497",
                      font=("Segoe UI", 11), text_color="#888888").pack(anchor="w", pady=(3, 0))

    def save_keys(self):
        env_path = REPO / ".env"
        lines = env_path.read_text().splitlines() if env_path.exists() else []
        for env_name, entry in self.key_entries.items():
            val = entry.get().strip()
            if val:
                os.environ[env_name] = val
                found = False
                for i, line in enumerate(lines):
                    if line.startswith(f"{env_name}="):
                        lines[i] = f'{env_name}="{val}"'
                        found = True
                        break
                if not found:
                    lines.append(f'{env_name}="{val}"')
        env_path.write_text("\n".join(lines) + "\n")
        messagebox.showinfo("Saved", "API keys saved to .env")

    def save_config(self):
        try:
            config = json.loads(Path("config/config.json").read_text())
        except Exception:
            config = {}
        for key, entry in self.config_entries.items():
            try:
                config[key] = float(entry.get())
            except Exception:
                pass
        Path("config/config.json").write_text(json.dumps(config, indent=2))
        messagebox.showinfo("Saved", "Config saved to config/config.json")


class FinalAIApp(ctk.CTk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("FinalAI Quantum — Trading Intelligence")
        self.geometry("1200x750")
        self.minsize(900, 600)

        # Header
        header = ctk.CTkFrame(self, height=50, fg_color="#0f172a")
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="  FinalAI Quantum", font=("Segoe UI", 20, "bold"),
                      text_color="#60a5fa").pack(side="left", padx=10)
        ctk.CTkLabel(header, text="v7.0 — Trading Intelligence Platform",
                      font=("Segoe UI", 12), text_color="#64748b").pack(side="left", padx=5)

        # Tab view
        self.tabs = ctk.CTkTabview(self, fg_color="#0f172a",
                                    segmented_button_fg_color="#1e293b",
                                    segmented_button_selected_color="#3b82f6")
        self.tabs.pack(fill="both", expand=True, padx=10, pady=(5, 0))

        # Create tabs
        t1 = self.tabs.add("  Analyze  ")
        t2 = self.tabs.add("  Swarm AI  ")
        t3 = self.tabs.add("  Backtest  ")
        t4 = self.tabs.add("  Portfolio  ")
        t5 = self.tabs.add("  Settings  ")

        self.analyze_tab = AnalyzeTab(t1, self)
        self.analyze_tab.pack(fill="both", expand=True)

        self.swarm_tab = SwarmTab(t2, self)
        self.swarm_tab.pack(fill="both", expand=True)

        self.backtest_tab = BacktestTab(t3, self)
        self.backtest_tab.pack(fill="both", expand=True)

        self.portfolio_tab = PortfolioTab(t4, self)
        self.portfolio_tab.pack(fill="both", expand=True)

        self.settings_tab = SettingsTab(t5, self)
        self.settings_tab.pack(fill="both", expand=True)

        # Status bar
        self.status = StatusBar(self, fg_color="#0f172a")
        self.status.pack(fill="x")

        # Start output queue processor
        self._process_queue()

        # Initial status
        broker = os.getenv("BROKER", "alpaca")
        fh = "OK" if os.getenv("FINNHUB_API_KEY") else "missing"
        groq = "OK" if os.getenv("GROQ_API_KEY") else "missing"
        self.status.set(f"Broker: {broker.upper()} | Finnhub: {fh} | Groq: {groq} | Ready")

    def _process_queue(self):
        """Process output from background threads."""
        try:
            while True:
                cmd, data = _output_q.get_nowait()
                # Find the currently visible output panel
                current = self.tabs.get()
                panel = None
                if "Analyze" in current:
                    panel = self.analyze_tab.output
                elif "Swarm" in current:
                    panel = self.swarm_tab.output
                elif "Backtest" in current:
                    panel = self.backtest_tab.output
                elif "Portfolio" in current:
                    panel = self.portfolio_tab.output

                if cmd == "append" and panel:
                    panel.append(data)
                elif cmd == "clear" and panel:
                    panel.clear()
                elif cmd == "status":
                    self.status.set(data)
        except queue.Empty:
            pass
        self.after(100, self._process_queue)


if __name__ == "__main__":
    app = FinalAIApp()
    app.mainloop()
