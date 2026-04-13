"""FinalAI Quantum — Full Desktop Trading Application

All 24 features from Trading.py in a professional dark-themed GUI.
Launch: python gui/app.py  (or double-click Desktop shortcut)
"""

import os, sys, threading, json, queue, time as _time
from pathlib import Path
from datetime import datetime, timedelta

REPO = Path(__file__).resolve().parent.parent
os.chdir(REPO)
sys.path.insert(0, str(REPO))

import customtkinter as ctk
from tkinter import messagebox, StringVar
import tkinter as tk

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except Exception:
    pass

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Colors
BG_DARK = "#0b0f19"
BG_CARD = "#111827"
BG_SIDEBAR = "#0f172a"
ACCENT = "#3b82f6"
ACCENT_GREEN = "#10b981"
ACCENT_RED = "#ef4444"
ACCENT_PURPLE = "#8b5cf6"
ACCENT_AMBER = "#f59e0b"
TEXT_DIM = "#64748b"
TEXT_LIGHT = "#e2e8f0"

_trading_mod = None
def T():
    global _trading_mod
    if _trading_mod is None:
        import importlib
        _trading_mod = importlib.import_module("Trading")
    return _trading_mod

_output_q = queue.Queue()


# ═══════════════════════════════════════════════════════════
# REUSABLE COMPONENTS
# ═══════════════════════════════════════════════════════════

class OutputPanel(ctk.CTkFrame):
    def __init__(self, parent, **kw):
        super().__init__(parent, fg_color=BG_DARK, corner_radius=8, **kw)
        self.textbox = ctk.CTkTextbox(self, font=("Consolas", 12), wrap="word",
                                       state="disabled", fg_color=BG_DARK,
                                       text_color=TEXT_LIGHT, corner_radius=8)
        self.textbox.pack(fill="both", expand=True, padx=4, pady=4)

    def append(self, text):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", text + "\n")
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def clear(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.configure(state="disabled")


class InputRow(ctk.CTkFrame):
    """Horizontal row with label + entry."""
    def __init__(self, parent, label, default="", width=120, **kw):
        super().__init__(parent, fg_color="transparent", **kw)
        ctk.CTkLabel(self, text=label, font=("Segoe UI", 12), width=80, anchor="w").pack(side="left")
        self.entry = ctk.CTkEntry(self, width=width, font=("Segoe UI", 12))
        self.entry.insert(0, default)
        self.entry.pack(side="left", padx=5)

    def get(self): return self.entry.get().strip()


def run_bg(output_panel, status_bar, label, fn):
    """Run fn() in background thread, routing output to panel."""
    output_panel.clear()
    output_panel.append(f"{label}...\n")
    if status_bar:
        status_bar.set(f"{label}...")
    def _w():
        try:
            fn()
        except Exception as e:
            _output_q.put(("append", f"\nError: {e}"))
            import traceback
            _output_q.put(("append", traceback.format_exc()))
    threading.Thread(target=_w, daemon=True).start()


def fetch_data(ticker, period="5d", interval="1m"):
    import yfinance as yf
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    if hasattr(df.columns, 'levels'):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    return df


def get_indicators(ticker, period="5d", interval="1m"):
    mod = T()
    df = fetch_data(ticker, period, interval)
    if df is None or df.empty:
        return None, None
    indicators = mod.TechnicalAnalyzer.calculate_indicators(df)
    if indicators:
        indicators.price = float(df['Close'].iloc[-1])
        indicators.close = float(df['Close'].iloc[-1])
    return df, indicators


def get_analyzer():
    mod = T()
    a = mod.AIAnalyzer.__new__(mod.AIAnalyzer)
    a.api_key = None
    return a


# ═══════════════════════════════════════════════════════════
# PAGE BUILDERS — each returns a frame with the full UI
# ═══════════════════════════════════════════════════════════

def build_analyze(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    top = ctk.CTkFrame(f, fg_color="transparent")
    top.pack(fill="x", padx=10, pady=8)
    ctk.CTkLabel(top, text="Ticker:", font=("Segoe UI", 13)).pack(side="left")
    ticker_e = ctk.CTkEntry(top, width=100, placeholder_text="AAPL", font=("Segoe UI", 13))
    ticker_e.pack(side="left", padx=5)
    style_v = StringVar(value="day")
    ctk.CTkSegmentedButton(top, values=["day", "swing", "long"], variable=style_v,
                            font=("Segoe UI", 11)).pack(side="left", padx=10)
    out = OutputPanel(f)
    out.pack(fill="both", expand=True, padx=10, pady=(0,8))

    def _run():
        t = ticker_e.get().strip().upper()
        if not t: return
        is_day = style_v.get() == "day"
        per = "5d" if is_day else ("3mo" if style_v.get() == "swing" else "1y")
        itv = "1m" if is_day else "1d"
        def work():
            df, ind = get_indicators(t, per, itv)
            if ind is None:
                _output_q.put(("append", f"No data for {t}")); return
            sig = get_analyzer()._fallback_analysis(t, ind, 100000, 0.01, 2.5, is_day_trading=is_day)
            if not sig:
                _output_q.put(("append", "No signal")); return
            p = ind.price
            _output_q.put(("clear", None))
            for l in [
                f"{'='*50}", f"  {t} @ ${p:.2f}", f"  Signal: {sig.action} ({sig.confidence:.0f}%)",
                f"  SL: ${sig.stop_loss:.2f}  |  TP1: ${sig.take_profit_1:.2f}  |  TP2: ${sig.take_profit_2:.2f}",
                f"{'='*50}", "",
                f"  RSI: {ind.rsi_14:.1f}  |  MACD: {ind.macd:.4f}  |  ADX: {ind.adx:.1f}" if ind.adx else "",
                f"  SMA20: {ind.sma_20:.2f}  |  SMA50: {ind.sma_50:.2f}",
                f"  EMA8: {ind.ema_8:.2f}  |  EMA21: {ind.ema_21:.2f}",
                f"  ATR: {ind.atr:.4f} ({ind.atr_percent:.2f}%)" if ind.atr_percent else "",
                f"  Vol Ratio: {ind.volume_ratio:.2f}x" if ind.volume_ratio else "",
                f"  Regime: {ind.market_regime}" if ind.market_regime else "",
                f"  R:R = 1:{abs(sig.take_profit_1-p)/max(0.01,abs(p-sig.stop_loss)):.1f}",
            ]:
                if l: _output_q.put(("append", l))
            if hasattr(sig, 'supporting_signals') and sig.supporting_signals:
                _output_q.put(("append", "\n  Signals:"))
                for s in sig.supporting_signals[:12]: _output_q.put(("append", f"    {s}"))
            _output_q.put(("status", f"{t}: {sig.action} ({sig.confidence:.0f}%)"))
        run_bg(out, app.status, f"Analyzing {t}", work)

    ctk.CTkButton(top, text="Analyze", command=_run, font=("Segoe UI", 13, "bold"),
                   width=100, fg_color=ACCENT).pack(side="left", padx=5)
    ticker_e.bind("<Return>", lambda e: _run())
    return f


def build_scanner(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    top = ctk.CTkFrame(f, fg_color="transparent")
    top.pack(fill="x", padx=10, pady=8)
    uni_v = StringVar(value="tech_leaders")
    ctk.CTkLabel(top, text="Universe:", font=("Segoe UI", 13)).pack(side="left")
    ctk.CTkOptionMenu(top, values=["tech_leaders", "sp500_top50", "crypto", "all"],
                       variable=uni_v, font=("Segoe UI", 12), width=150).pack(side="left", padx=5)
    min_conf = ctk.CTkEntry(top, width=60, font=("Segoe UI", 12))
    min_conf.insert(0, "70")
    ctk.CTkLabel(top, text="Min Conf%:", font=("Segoe UI", 12)).pack(side="left", padx=(10,3))
    min_conf.pack(side="left")
    out = OutputPanel(f)
    out.pack(fill="both", expand=True, padx=10, pady=(0,8))

    def _run():
        def work():
            mod = T()
            universes = getattr(mod, 'MARKET_UNIVERSES', {})
            tickers = list(universes.get(uni_v.get(), universes.get('tech_leaders', ['AAPL','MSFT','GOOGL'])))
            conf_thresh = float(min_conf.get() or 70)
            _output_q.put(("append", f"Scanning {len(tickers)} tickers (min conf {conf_thresh}%)...\n"))
            hits = []
            for t in tickers:
                try:
                    df, ind = get_indicators(t, "5d", "1m")
                    if ind is None: continue
                    sig = get_analyzer()._fallback_analysis(t, ind, 100000, 0.01, 2.5, is_day_trading=True)
                    if sig and sig.action != 'HOLD' and sig.confidence >= conf_thresh:
                        hits.append((t, sig.action, sig.confidence, ind.price))
                        _output_q.put(("append", f"  {'BUY' if sig.action=='BUY' else 'SELL'} {t} @ ${ind.price:.2f} ({sig.confidence:.0f}%)"))
                except Exception: continue
            if not hits:
                _output_q.put(("append", "\nNo signals above threshold."))
            else:
                _output_q.put(("append", f"\n{len(hits)} signal(s) found."))
            _output_q.put(("status", f"Scanner: {len(hits)} hits from {len(tickers)} tickers"))
        run_bg(out, app.status, f"Scanning {uni_v.get()}", work)

    ctk.CTkButton(top, text="Scan", command=_run, font=("Segoe UI", 13, "bold"),
                   width=80, fg_color=ACCENT).pack(side="left", padx=10)
    return f


def build_news(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    top = ctk.CTkFrame(f, fg_color="transparent")
    top.pack(fill="x", padx=10, pady=8)
    ticker_e = ctk.CTkEntry(top, width=100, placeholder_text="AAPL", font=("Segoe UI", 13))
    ctk.CTkLabel(top, text="Ticker:", font=("Segoe UI", 13)).pack(side="left")
    ticker_e.pack(side="left", padx=5)
    out = OutputPanel(f)
    out.pack(fill="both", expand=True, padx=10, pady=(0,8))

    def _run():
        t = ticker_e.get().strip().upper() or "AAPL"
        def work():
            import requests
            _output_q.put(("append", f"Fetching news for {t}...\n"))
            # NewsData
            nd = os.getenv('NEWSDATA_API_KEY', '')
            if nd:
                try:
                    r = requests.get(f"https://newsdata.io/api/1/news?apikey={nd}&q={t}&language=en&size=5", timeout=8)
                    if r.status_code == 200:
                        for art in r.json().get('results', [])[:5]:
                            _output_q.put(("append", f"  [{art.get('pubDate','')[:10]}] {art['title']}"))
                except Exception: pass
            # News API
            na = os.getenv('NEWS_API_KEY', '')
            if na:
                try:
                    r = requests.get(f"https://newsapi.org/v2/everything?q={t}&apiKey={na}&pageSize=5&sortBy=publishedAt", timeout=8)
                    if r.status_code == 200:
                        _output_q.put(("append", "\n  Latest headlines:"))
                        for art in r.json().get('articles', [])[:5]:
                            _output_q.put(("append", f"  [{art.get('publishedAt','')[:10]}] {art['title']}"))
                except Exception: pass
            if not nd and not na:
                _output_q.put(("append", "No news API keys configured. Add NEWSDATA_API_KEY or NEWS_API_KEY in Settings."))
        run_bg(out, app.status, f"News: {t}", work)

    ctk.CTkButton(top, text="Get News", command=_run, font=("Segoe UI", 13, "bold"),
                   width=100, fg_color=ACCENT).pack(side="left", padx=10)
    return f


def build_swarm(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    top = ctk.CTkFrame(f, fg_color="transparent")
    top.pack(fill="x", padx=10, pady=8)
    ticker_e = ctk.CTkEntry(top, width=100, placeholder_text="AAPL", font=("Segoe UI", 13))
    ctk.CTkLabel(top, text="Ticker:", font=("Segoe UI", 13)).pack(side="left")
    ticker_e.pack(side="left", padx=5)
    rounds_v = StringVar(value="3")
    ctk.CTkLabel(top, text="Rounds:", font=("Segoe UI", 12)).pack(side="left", padx=(10,3))
    ctk.CTkOptionMenu(top, values=["2","3","4"], variable=rounds_v, width=55).pack(side="left")
    out = OutputPanel(f)
    out.pack(fill="both", expand=True, padx=10, pady=(0,8))

    def _run():
        t = ticker_e.get().strip().upper()
        if not t: return
        def work():
            mod = T()
            df, ind = get_indicators(t)
            if ind is None: _output_q.put(("append", "No data")); return
            swarm = mod.SwarmIntelligence()
            # Redirect swarm console output
            result = swarm.analyze(t, ind, rounds=int(rounds_v.get()))
            a, c = result.get('action','HOLD'), result.get('confidence',0)
            bd = result.get('breakdown',{})
            _output_q.put(("append", f"\n{'='*50}"))
            _output_q.put(("append", f"  CONSENSUS: {a} ({c:.1f}%)"))
            _output_q.put(("append", f"  BUY: {bd.get('buy',0):.0f}%  SELL: {bd.get('sell',0):.0f}%  HOLD: {bd.get('hold',0):.0f}%"))
            _output_q.put(("append", f"{'='*50}"))
            for r in result.get('reasons', [])[:5]:
                _output_q.put(("append", f"  - {r}"))
            _output_q.put(("append", "\n  Leaderboard:"))
            for ag in sorted(swarm.agents, key=lambda x: x.accuracy, reverse=True):
                _output_q.put(("append", f"    {ag.name}: {ag.accuracy*100:.0f}% ({ag.weight:.1f}x)"))
            _output_q.put(("status", f"Swarm: {a} on {t} ({c:.0f}%)"))
        run_bg(out, app.status, f"Swarm: {t} ({rounds_v.get()} rounds)", work)

    ctk.CTkButton(top, text="Run Swarm", command=_run, font=("Segoe UI", 13, "bold"),
                   width=110, fg_color=ACCENT_PURPLE, hover_color="#7c3aed").pack(side="left", padx=10)
    return f


def build_backtest(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    top = ctk.CTkFrame(f, fg_color="transparent")
    top.pack(fill="x", padx=10, pady=8)
    ticker_e = ctk.CTkEntry(top, width=80, placeholder_text="AAPL", font=("Segoe UI", 13))
    start_e = ctk.CTkEntry(top, width=100, font=("Segoe UI", 12))
    start_e.insert(0, (datetime.now()-timedelta(days=90)).strftime('%Y-%m-%d'))
    cutoff_e = ctk.CTkEntry(top, width=100, font=("Segoe UI", 12))
    cutoff_e.insert(0, (datetime.now()-timedelta(days=7)).strftime('%Y-%m-%d'))
    horizon_v = StringVar(value="5")
    for lbl, w in [("Ticker:",ticker_e),("Start:",start_e),("Cutoff:",cutoff_e)]:
        ctk.CTkLabel(top, text=lbl, font=("Segoe UI", 12)).pack(side="left", padx=(8,2))
        w.pack(side="left")
    ctk.CTkLabel(top, text="Days:", font=("Segoe UI", 12)).pack(side="left", padx=(8,2))
    ctk.CTkOptionMenu(top, values=["3","5","10","20"], variable=horizon_v, width=55).pack(side="left")
    out = OutputPanel(f)
    out.pack(fill="both", expand=True, padx=10, pady=(0,8))

    def _run():
        t = ticker_e.get().strip().upper()
        if not t: return
        def work():
            import yfinance as yf
            df = fetch_data(t, period=None, interval="1d") if False else None
            df = yf.download(t, start=start_e.get(), end=cutoff_e.get(), interval='1d', progress=False)
            if hasattr(df.columns, 'levels'):
                df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            if df is None or len(df) < 20:
                _output_q.put(("append", "Not enough data")); return
            p = float(df['Close'].iloc[-1])
            ind = T().TechnicalAnalyzer.calculate_indicators(df)
            if not ind: _output_q.put(("append", "Indicator error")); return
            ind.price = p; ind.close = p
            sig = get_analyzer()._fallback_analysis(t, ind, 100000, 0.01, 2.5)
            if not sig: _output_q.put(("append", "No signal")); return
            _output_q.put(("append", f"Bot sees {len(df)} candles ending ${p:.2f}"))
            _output_q.put(("append", f"\nPREDICTION: {sig.action} ({sig.confidence:.0f}%)"))
            _output_q.put(("append", f"SL: ${sig.stop_loss:.2f} | TP: ${sig.take_profit_1:.2f}\n"))
            # Reveal
            h = int(horizon_v.get())
            end = (datetime.strptime(cutoff_e.get(), '%Y-%m-%d')+timedelta(days=h+5)).strftime('%Y-%m-%d')
            fut = yf.download(t, start=cutoff_e.get(), end=end, interval='1d', progress=False)
            if hasattr(fut.columns, 'levels'):
                fut.columns = [c[0] if isinstance(c, tuple) else c for c in fut.columns]
            fut = fut.head(h)
            if fut.empty: _output_q.put(("append", "No future data")); return
            final = float(fut['Close'].iloc[-1])
            chg = (final-p)/p*100
            ok = (sig.action=='BUY' and chg>0) or (sig.action=='SELL' and chg<0) or (sig.action=='HOLD' and abs(chg)<1.5)
            _output_q.put(("append", f"ACTUAL: ${p:.2f} -> ${final:.2f} ({chg:+.2f}%)"))
            _output_q.put(("append", f"VERDICT: {'CORRECT' if ok else 'WRONG'}\n"))
            for idx, row in fut.iterrows():
                dc = (float(row['Close'])-p)/p*100
                _output_q.put(("append", f"  {str(idx)[:10]}: ${float(row['Close']):.2f} ({dc:+.2f}%)"))
        run_bg(out, app.status, f"Backtest: {t}", work)

    ctk.CTkButton(top, text="Test", command=_run, font=("Segoe UI", 13, "bold"),
                   width=80, fg_color=ACCENT_GREEN, hover_color="#059669").pack(side="left", padx=10)
    return f


def build_monte_carlo(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    top = ctk.CTkFrame(f, fg_color="transparent")
    top.pack(fill="x", padx=10, pady=8)
    ticker_e = ctk.CTkEntry(top, width=80, placeholder_text="AAPL", font=("Segoe UI", 13))
    sims_e = ctk.CTkEntry(top, width=100, font=("Segoe UI", 12))
    sims_e.insert(0, "1000000")
    horizon_e = ctk.CTkEntry(top, width=60, font=("Segoe UI", 12))
    horizon_e.insert(0, "30")
    for lbl, w in [("Ticker:",ticker_e),("Sims:",sims_e),("Days:",horizon_e)]:
        ctk.CTkLabel(top, text=lbl, font=("Segoe UI", 12)).pack(side="left", padx=(8,2))
        w.pack(side="left")
    out = OutputPanel(f)
    out.pack(fill="both", expand=True, padx=10, pady=(0,8))

    def _run():
        t = ticker_e.get().strip().upper()
        if not t: return
        def work():
            import numpy as np, yfinance as yf
            n = int(sims_e.get()); h = int(horizon_e.get())
            _output_q.put(("append", f"Running {n:,} Monte Carlo simulations for {t} ({h} days)...\n"))
            df = yf.download(t, period="1y", interval="1d", progress=False)
            if hasattr(df.columns, 'levels'):
                df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            if df is None or len(df) < 30: _output_q.put(("append", "No data")); return
            closes = df['Close'].values.astype(float)
            returns = np.diff(np.log(closes))
            mu = returns.mean(); sigma = returns.std()
            S0 = closes[-1]
            rng = np.random.default_rng()
            rand = rng.standard_normal((n, h))
            paths = S0 * np.exp(np.cumsum((mu - 0.5*sigma**2) + sigma*rand, axis=1))
            finals = paths[:, -1]
            _output_q.put(("clear", None))
            _output_q.put(("append", f"Monte Carlo: {t} | {n:,} sims | {h} days"))
            _output_q.put(("append", f"Current: ${S0:.2f}\n"))
            for p_name, p_val in [("5th", 5),("25th",25),("50th (median)",50),("75th",75),("95th",95)]:
                v = np.percentile(finals, p_val)
                chg = (v-S0)/S0*100
                _output_q.put(("append", f"  {p_name}: ${v:.2f} ({chg:+.1f}%)"))
            _output_q.put(("append", f"\n  Mean: ${finals.mean():.2f} ({(finals.mean()-S0)/S0*100:+.1f}%)"))
            _output_q.put(("append", f"  Prob up: {(finals>S0).mean()*100:.1f}%"))
            _output_q.put(("append", f"  Prob >5%: {(finals>S0*1.05).mean()*100:.1f}%"))
            _output_q.put(("append", f"  Prob <-5%: {(finals<S0*0.95).mean()*100:.1f}%"))
            _output_q.put(("status", f"MC: {t} median ${np.median(finals):.2f} ({h}d)"))
        run_bg(out, app.status, f"Monte Carlo: {t}", work)

    ctk.CTkButton(top, text="Simulate", command=_run, font=("Segoe UI", 13, "bold"),
                   width=100, fg_color=ACCENT_AMBER, hover_color="#d97706").pack(side="left", padx=10)
    return f


def build_portfolio(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    top = ctk.CTkFrame(f, fg_color="transparent")
    top.pack(fill="x", padx=10, pady=8)
    out = OutputPanel(f)
    out.pack(fill="both", expand=True, padx=10, pady=(0,8))

    def _acct():
        def work():
            mod = T()
            b = mod.IBKRTrader()
            if not b.is_ready():
                _output_q.put(("append", "IBKR not connected. Start TWS first.")); return
            a = b.get_account()
            if a:
                _output_q.put(("append", f"  {b.status_line()}\n"))
                _output_q.put(("append", f"  Cash:         ${a['cash']:,.2f}"))
                _output_q.put(("append", f"  Equity:       ${a['equity']:,.2f}"))
                _output_q.put(("append", f"  Buying Power: ${a['buying_power']:,.2f}"))
            positions = b.list_positions()
            if positions:
                _output_q.put(("append", f"\n  Open Positions ({len(positions)}):"))
                _output_q.put(("append", f"  {'Symbol':<10} {'Qty':>8} {'Side':<6} {'Entry':>10} {'P&L':>12}"))
                _output_q.put(("append", f"  {'-'*48}"))
                total = 0
                for p in positions:
                    pnl = p.get('unrealized_pl',0); total += pnl
                    _output_q.put(("append", f"  {p['symbol']:<10} {p['qty']:>8.0f} {p['side']:<6} ${p['avg_entry_price']:>9.2f} ${pnl:>+11.2f}"))
                _output_q.put(("append", f"  {'-'*48}"))
                _output_q.put(("append", f"  {'Total':>36} ${total:>+11.2f}"))
            else:
                _output_q.put(("append", "\n  No open positions."))
            b.disconnect()
        run_bg(out, app.status, "Fetching IBKR", work)

    ctk.CTkButton(top, text="Refresh", command=_acct, font=("Segoe UI", 13, "bold"), width=100).pack(side="left", padx=5)
    return f


def build_paper(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    out = OutputPanel(f)
    out.pack(fill="both", expand=True, padx=10, pady=8)

    def _load():
        def work():
            try:
                p = Path("results/paper_trades.json")
                if not p.exists(): _output_q.put(("append", "No paper trades yet.")); return
                trades = json.loads(p.read_text())
                if not trades: _output_q.put(("append", "No paper trades.")); return
                _output_q.put(("append", f"Paper Trades ({len(trades)}):\n"))
                for t in trades[-20:]:
                    _output_q.put(("append", f"  {t.get('ticker','?')} {t.get('action','?')} @ ${t.get('entry_price',0):.2f} | "
                                             f"SL ${t.get('stop_loss',0):.2f} TP ${t.get('take_profit',0):.2f} | {t.get('status','open')}"))
            except Exception as e: _output_q.put(("append", f"Error: {e}"))
        run_bg(out, app.status, "Loading paper trades", work)

    ctk.CTkButton(f, text="Load Paper Trades", command=_load, font=("Segoe UI", 13)).pack(padx=10, pady=5, anchor="w")
    return f


def build_smart_money(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    top = ctk.CTkFrame(f, fg_color="transparent")
    top.pack(fill="x", padx=10, pady=8)
    ticker_e = ctk.CTkEntry(top, width=100, placeholder_text="AAPL", font=("Segoe UI", 13))
    ctk.CTkLabel(top, text="Ticker:", font=("Segoe UI", 13)).pack(side="left")
    ticker_e.pack(side="left", padx=5)
    out = OutputPanel(f)
    out.pack(fill="both", expand=True, padx=10, pady=(0,8))

    def _run():
        t = ticker_e.get().strip().upper()
        if not t: return
        def work():
            mod = T()
            df, ind = get_indicators(t, "3mo", "1d")
            if df is None: _output_q.put(("append", "No data")); return
            try:
                sma = mod.SmartMoneyAnalyzer()
                result = sma.analyze(df)
                _output_q.put(("append", f"Smart Money Analysis: {t}\n"))
                _output_q.put(("append", f"  Structure: {result.get('market_structure', '?')}"))
                for ob in result.get('order_blocks', [])[:5]:
                    _output_q.put(("append", f"  Order Block: {ob.get('type','?')} @ ${ob.get('price',0):.2f}"))
                for fvg in result.get('fair_value_gaps', [])[:5]:
                    _output_q.put(("append", f"  FVG: {fvg.get('type','?')} ${fvg.get('low',0):.2f}-${fvg.get('high',0):.2f}"))
                for lz in result.get('liquidity_zones', [])[:5]:
                    _output_q.put(("append", f"  Liquidity: ${lz.get('price',0):.2f} ({lz.get('type','?')})"))
            except Exception as e:
                _output_q.put(("append", f"Error: {e}"))
        run_bg(out, app.status, f"Smart Money: {t}", work)

    ctk.CTkButton(top, text="Detect", command=_run, font=("Segoe UI", 13, "bold"),
                   width=90, fg_color=ACCENT).pack(side="left", padx=10)
    return f


def build_multi_tf(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    top = ctk.CTkFrame(f, fg_color="transparent")
    top.pack(fill="x", padx=10, pady=8)
    ticker_e = ctk.CTkEntry(top, width=100, placeholder_text="AAPL", font=("Segoe UI", 13))
    ctk.CTkLabel(top, text="Ticker:", font=("Segoe UI", 13)).pack(side="left")
    ticker_e.pack(side="left", padx=5)
    out = OutputPanel(f)
    out.pack(fill="both", expand=True, padx=10, pady=(0,8))

    def _run():
        t = ticker_e.get().strip().upper()
        if not t: return
        def work():
            _output_q.put(("append", f"Multi-Timeframe Analysis: {t}\n"))
            for tf, per, itv in [("1m (intraday)","5d","1m"),("15m","5d","15m"),("1h","1mo","1h"),("1D","6mo","1d")]:
                try:
                    df, ind = get_indicators(t, per, itv)
                    if ind is None: continue
                    sig = get_analyzer()._fallback_analysis(t, ind, 100000, 0.01, 2.5, is_day_trading=(itv=="1m"))
                    if sig:
                        _output_q.put(("append", f"  {tf:>15}: {sig.action} ({sig.confidence:.0f}%) — RSI {ind.rsi_14:.0f}"))
                except Exception: continue
        run_bg(out, app.status, f"Multi-TF: {t}", work)

    ctk.CTkButton(top, text="Analyze", command=_run, font=("Segoe UI", 13, "bold"),
                   width=90, fg_color=ACCENT).pack(side="left", padx=10)
    return f


def build_options(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    top = ctk.CTkFrame(f, fg_color="transparent")
    top.pack(fill="x", padx=10, pady=8)
    ticker_e = ctk.CTkEntry(top, width=80, placeholder_text="AAPL", font=("Segoe UI", 13))
    ctk.CTkLabel(top, text="Ticker:", font=("Segoe UI", 13)).pack(side="left")
    ticker_e.pack(side="left", padx=5)
    out = OutputPanel(f)
    out.pack(fill="both", expand=True, padx=10, pady=(0,8))

    def _run():
        t = ticker_e.get().strip().upper()
        if not t: return
        def work():
            import yfinance as yf
            tk = yf.Ticker(t)
            _output_q.put(("append", f"Options Chain: {t}\n"))
            try:
                dates = tk.options[:5]
                _output_q.put(("append", f"  Expiration dates: {', '.join(dates[:5])}"))
                if dates:
                    chain = tk.option_chain(dates[0])
                    _output_q.put(("append", f"\n  Calls (nearest expiry {dates[0]}):"))
                    _output_q.put(("append", f"  {'Strike':>10} {'Last':>8} {'Bid':>8} {'Ask':>8} {'Vol':>8} {'OI':>8} {'IV':>8}"))
                    for _, r in chain.calls.head(10).iterrows():
                        _output_q.put(("append", f"  ${r['strike']:>9.2f} ${r['lastPrice']:>7.2f} ${r['bid']:>7.2f} ${r['ask']:>7.2f} {r.get('volume',''):>8} {r.get('openInterest',''):>8} {r.get('impliedVolatility',0)*100:>7.1f}%"))
                    _output_q.put(("append", f"\n  Puts (nearest expiry {dates[0]}):"))
                    for _, r in chain.puts.head(10).iterrows():
                        _output_q.put(("append", f"  ${r['strike']:>9.2f} ${r['lastPrice']:>7.2f} ${r['bid']:>7.2f} ${r['ask']:>7.2f} {r.get('volume',''):>8} {r.get('openInterest',''):>8} {r.get('impliedVolatility',0)*100:>7.1f}%"))
            except Exception as e:
                _output_q.put(("append", f"Error: {e}"))
        run_bg(out, app.status, f"Options: {t}", work)

    ctk.CTkButton(top, text="Load Chain", command=_run, font=("Segoe UI", 13, "bold"),
                   width=110, fg_color=ACCENT).pack(side="left", padx=10)
    return f


def build_insider(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    top = ctk.CTkFrame(f, fg_color="transparent")
    top.pack(fill="x", padx=10, pady=8)
    ticker_e = ctk.CTkEntry(top, width=100, placeholder_text="AAPL", font=("Segoe UI", 13))
    ctk.CTkLabel(top, text="Ticker:", font=("Segoe UI", 13)).pack(side="left")
    ticker_e.pack(side="left", padx=5)
    out = OutputPanel(f)
    out.pack(fill="both", expand=True, padx=10, pady=(0,8))

    def _run():
        t = ticker_e.get().strip().upper()
        if not t: return
        def work():
            fh = os.getenv('FINNHUB_API_KEY','')
            if not fh: _output_q.put(("append", "Need FINNHUB_API_KEY")); return
            import requests
            r = requests.get(f"https://finnhub.io/api/v1/stock/insider-transactions?symbol={t}&token={fh}", timeout=8)
            if r.status_code != 200: _output_q.put(("append", f"API error {r.status_code}")); return
            data = r.json().get('data', [])
            _output_q.put(("append", f"Insider Transactions: {t} ({len(data)} recent)\n"))
            for tx in data[:15]:
                name = tx.get('name','?')
                shares = tx.get('share', 0)
                price = tx.get('transactionPrice', 0)
                code = tx.get('transactionCode', '?')
                date = tx.get('filingDate', '?')
                action = "BUY" if code in ('P','A') else "SELL" if code == 'S' else code
                _output_q.put(("append", f"  {date} {action:>4} {name[:25]:<25} {shares:>10,} @ ${price:.2f}"))
        run_bg(out, app.status, f"Insider: {t}", work)

    ctk.CTkButton(top, text="Check Insiders", command=_run, font=("Segoe UI", 13, "bold"),
                   width=120, fg_color=ACCENT).pack(side="left", padx=10)
    return f


def build_political(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    out = OutputPanel(f)
    out.pack(fill="both", expand=True, padx=10, pady=8)
    def _run():
        def work():
            _output_q.put(("append", "Political Trades Tracker\n"))
            _output_q.put(("append", "Fetching congressional trading disclosures...\n"))
            try:
                import requests
                r = requests.get("https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json", timeout=15)
                if r.status_code == 200:
                    trades = r.json()[-20:]
                    for tx in trades:
                        _output_q.put(("append", f"  {tx.get('transaction_date','?')} {tx.get('representative','?')[:20]:<20} "
                                                 f"{tx.get('type','?'):>10} {tx.get('ticker','?'):<6} {tx.get('amount','?')}"))
                else:
                    _output_q.put(("append", "Could not fetch data"))
            except Exception as e:
                _output_q.put(("append", f"Error: {e}"))
        run_bg(out, app.status, "Political trades", work)
    ctk.CTkButton(f, text="Fetch Congressional Trades", command=_run,
                   font=("Segoe UI", 13), width=200).pack(padx=10, pady=8, anchor="w")
    return f


def build_quant(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    out = OutputPanel(f)
    out.pack(fill="both", expand=True, padx=10, pady=8)
    def _run():
        def work():
            _output_q.put(("append", "Quantitative Strategies\n"))
            _output_q.put(("append", "Use the terminal (Trading.py) for full quant access:"))
            _output_q.put(("append", "  - Momentum Strategy"))
            _output_q.put(("append", "  - Mean Reversion"))
            _output_q.put(("append", "  - Pairs Trading"))
            _output_q.put(("append", "  - Statistical Arbitrage"))
            _output_q.put(("append", "  - Risk Parity"))
            _output_q.put(("append", "\nRun: python Trading.py -> Option 15"))
        run_bg(out, app.status, "Quant strategies", work)
    ctk.CTkButton(f, text="Show Strategies", command=_run, font=("Segoe UI", 13)).pack(padx=10, pady=8, anchor="w")
    return f


def build_journal(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    out = OutputPanel(f)
    out.pack(fill="both", expand=True, padx=10, pady=8)
    def _run():
        def work():
            p = Path("logs/auto_trades.jsonl")
            if not p.exists(): _output_q.put(("append", "No trade journal entries yet.")); return
            lines = p.read_text().strip().split('\n')
            _output_q.put(("append", f"Trade Journal ({len(lines)} entries):\n"))
            _output_q.put(("append", f"{'Date':<22} {'Ticker':<8} {'Action':<6} {'Entry':>10} {'SL':>10} {'TP':>10} {'Conf':>6} {'Channel':>8}"))
            _output_q.put(("append", "-"*80))
            for line in lines[-25:]:
                try:
                    t = json.loads(line)
                    _output_q.put(("append", f"{t['time'][:19]:<22} {t['ticker']:<8} {t['action']:<6} "
                                             f"${t['entry']:>9.2f} ${t['stop_loss']:>9.2f} ${t['take_profit']:>9.2f} "
                                             f"{t['confidence']:>5.0f}% {t['channel']:>8}"))
                except Exception: pass
        run_bg(out, app.status, "Trade journal", work)
    ctk.CTkButton(f, text="Load Journal", command=_run, font=("Segoe UI", 13)).pack(padx=10, pady=8, anchor="w")
    return f


def build_sizing(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    top = ctk.CTkFrame(f, fg_color="transparent")
    top.pack(fill="x", padx=10, pady=8)
    entries = {}
    for lbl, default, w in [("Account $:","100000",100),("Risk %:","1.0",60),("Entry $:","150",80),("SL $:","145",80)]:
        ctk.CTkLabel(top, text=lbl, font=("Segoe UI", 12)).pack(side="left", padx=(8,2))
        e = ctk.CTkEntry(top, width=w, font=("Segoe UI", 12))
        e.insert(0, default)
        e.pack(side="left")
        entries[lbl] = e
    out = OutputPanel(f)
    out.pack(fill="both", expand=True, padx=10, pady=(0,8))

    def _run():
        def work():
            acct = float(entries["Account $:"].get())
            risk = float(entries["Risk %:"].get()) / 100
            entry = float(entries["Entry $:"].get())
            sl = float(entries["SL $:"].get())
            risk_per_share = abs(entry - sl)
            if risk_per_share <= 0: _output_q.put(("append", "SL must differ from entry")); return
            risk_dollars = acct * risk
            shares = int(risk_dollars / risk_per_share)
            notional = shares * entry
            _output_q.put(("clear", None))
            _output_q.put(("append", f"Position Sizing Calculator\n"))
            _output_q.put(("append", f"  Account:       ${acct:,.2f}"))
            _output_q.put(("append", f"  Risk:          {risk*100:.1f}% = ${risk_dollars:,.2f}"))
            _output_q.put(("append", f"  Entry:         ${entry:.2f}"))
            _output_q.put(("append", f"  Stop Loss:     ${sl:.2f}"))
            _output_q.put(("append", f"  Risk/Share:    ${risk_per_share:.2f}"))
            _output_q.put(("append", f"\n  Position Size: {shares} shares"))
            _output_q.put(("append", f"  Notional:      ${notional:,.2f}"))
            _output_q.put(("append", f"  Max Loss:      ${shares * risk_per_share:,.2f}"))
        run_bg(out, app.status, "Sizing", work)

    ctk.CTkButton(top, text="Calculate", command=_run, font=("Segoe UI", 13, "bold"),
                   width=90, fg_color=ACCENT).pack(side="left", padx=10)
    return f


def build_settings(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    scroll = ctk.CTkScrollableFrame(f, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=10, pady=8)

    ctk.CTkLabel(scroll, text="API Keys", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0,8))
    key_entries = {}
    for env_name, label in [("FINNHUB_API_KEY","Finnhub"),("GROQ_API_KEY","Groq"),
                             ("NEWSDATA_API_KEY","NewsData"),("NEWS_API_KEY","News API"),
                             ("ANTHROPIC_API_KEY","Anthropic")]:
        row = ctk.CTkFrame(scroll, fg_color="transparent")
        row.pack(fill="x", pady=2)
        ctk.CTkLabel(row, text=label, font=("Segoe UI", 12), width=120, anchor="w").pack(side="left")
        e = ctk.CTkEntry(row, show="*", font=("Segoe UI", 12))
        e.pack(side="left", fill="x", expand=True, padx=5)
        val = os.getenv(env_name, "")
        if val: e.insert(0, val)
        key_entries[env_name] = e

    def save_keys():
        env_path = REPO / ".env"
        lines = env_path.read_text().splitlines() if env_path.exists() else []
        for env_name, entry in key_entries.items():
            val = entry.get().strip()
            if val:
                os.environ[env_name] = val
                found = False
                for i, line in enumerate(lines):
                    if line.startswith(f"{env_name}="):
                        lines[i] = f'{env_name}="{val}"'; found = True; break
                if not found: lines.append(f'{env_name}="{val}"')
        env_path.write_text("\n".join(lines) + "\n")
        messagebox.showinfo("Saved", "API keys saved")

    ctk.CTkButton(scroll, text="Save Keys", command=save_keys, width=100).pack(anchor="w", pady=8)

    ctk.CTkLabel(scroll, text="Trading Config", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(15,8))
    try: config = json.loads(Path("config/config.json").read_text())
    except Exception: config = {}
    cfg_entries = {}
    for key, label, default in [("account_size","Account Size ($)",100000),("auto_trade_risk_pct","Risk/Trade (%)",1.0),
                                 ("auto_trade_max_daily","Max Trades/Day",30),("auto_trade_max_open_positions","Max Positions",8),
                                 ("auto_trade_max_daily_loss_pct","Daily Loss Limit (%)",5.0),("auto_trade_min_confidence","Min Confidence (%)",80)]:
        row = ctk.CTkFrame(scroll, fg_color="transparent")
        row.pack(fill="x", pady=2)
        ctk.CTkLabel(row, text=label, font=("Segoe UI", 12), width=180, anchor="w").pack(side="left")
        e = ctk.CTkEntry(row, width=100, font=("Segoe UI", 12))
        e.insert(0, str(config.get(key, default)))
        e.pack(side="left", padx=5)
        cfg_entries[key] = e

    def save_config():
        try: c = json.loads(Path("config/config.json").read_text())
        except Exception: c = {}
        for k, e in cfg_entries.items():
            try: c[k] = float(e.get())
            except Exception: pass
        Path("config/config.json").write_text(json.dumps(c, indent=2))
        messagebox.showinfo("Saved", "Config saved")

    ctk.CTkButton(scroll, text="Save Config", command=save_config, width=100).pack(anchor="w", pady=8)

    ctk.CTkLabel(scroll, text="Broker", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(15,8))
    broker_v = StringVar(value=os.getenv("BROKER","alpaca"))
    ctk.CTkSegmentedButton(scroll, values=["alpaca","ibkr"], variable=broker_v).pack(anchor="w")
    ctk.CTkLabel(scroll, text="IBKR needs TWS running on port 7497", font=("Segoe UI", 11), text_color=TEXT_DIM).pack(anchor="w", pady=3)
    return f


# ═══════════════════════════════════════════════════════════
# MAIN APP WITH SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════

class StatusBar(ctk.CTkFrame):
    def __init__(self, parent, **kw):
        super().__init__(parent, height=28, fg_color=BG_SIDEBAR, **kw)
        self.label = ctk.CTkLabel(self, text="Ready", font=("Segoe UI", 11), text_color=TEXT_DIM, anchor="w")
        self.label.pack(side="left", padx=10, fill="x", expand=True)
    def set(self, text):
        self.label.configure(text=text)


class FinalAIApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FinalAI Quantum")
        self.geometry("1280x800")
        self.minsize(1000, 650)
        self.configure(fg_color=BG_DARK)

        # Header
        header = ctk.CTkFrame(self, height=48, fg_color=BG_SIDEBAR, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header, text="  FinalAI Quantum", font=("Segoe UI", 18, "bold"),
                      text_color="#60a5fa").pack(side="left", padx=8)
        ctk.CTkLabel(header, text="Trading Intelligence Platform",
                      font=("Segoe UI", 11), text_color=TEXT_DIM).pack(side="left", padx=5)

        # Main area
        main = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        main.pack(fill="both", expand=True)

        # Sidebar
        sidebar = ctk.CTkScrollableFrame(main, width=200, fg_color=BG_SIDEBAR, corner_radius=0)
        sidebar.pack(side="left", fill="y")

        # Content
        self.content = ctk.CTkFrame(main, fg_color=BG_DARK, corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)

        # Status
        self.status = StatusBar(self)
        self.status.pack(fill="x")

        # Pages
        self.pages = {}
        self.current_page = None

        MENU = [
            ("ANALYSIS", [
                ("Analyze Ticker", "analyze", ACCENT),
                ("Market Scanner", "scanner", ACCENT),
                ("News Intel", "news", ACCENT),
                ("Smart Money", "smart_money", ACCENT),
                ("Multi-Timeframe", "multi_tf", ACCENT),
            ]),
            ("AI & SWARM", [
                ("Swarm AI (12 agents)", "swarm", ACCENT_PURPLE),
                ("Blind Prediction", "backtest", ACCENT_GREEN),
            ]),
            ("TRADING", [
                ("Portfolio (IBKR)", "portfolio", ACCENT),
                ("Paper Trading", "paper", ACCENT),
                ("Position Sizing", "sizing", ACCENT),
                ("Trade Journal", "journal", ACCENT),
            ]),
            ("QUANT LAB", [
                ("Monte Carlo", "monte_carlo", ACCENT_AMBER),
                ("Options Chain", "options", ACCENT),
                ("Quant Strategies", "quant", ACCENT),
            ]),
            ("RESEARCH", [
                ("Insider Trading", "insider", ACCENT),
                ("Political Trades", "political", ACCENT),
            ]),
            ("SYSTEM", [
                ("Settings", "settings", ACCENT),
            ]),
        ]

        builders = {
            "analyze": build_analyze, "scanner": build_scanner, "news": build_news,
            "swarm": build_swarm, "backtest": build_backtest, "monte_carlo": build_monte_carlo,
            "portfolio": build_portfolio, "paper": build_paper, "smart_money": build_smart_money,
            "multi_tf": build_multi_tf, "options": build_options, "insider": build_insider,
            "political": build_political, "quant": build_quant, "journal": build_journal,
            "sizing": build_sizing, "settings": build_settings,
        }

        self.nav_buttons = {}
        for section, items in MENU:
            ctk.CTkLabel(sidebar, text=section, font=("Segoe UI", 10, "bold"),
                          text_color=TEXT_DIM).pack(anchor="w", padx=12, pady=(12, 4))
            for label, key, color in items:
                btn = ctk.CTkButton(sidebar, text=f"  {label}", font=("Segoe UI", 12),
                                     fg_color="transparent", hover_color="#1e293b",
                                     text_color=TEXT_LIGHT, anchor="w", height=32,
                                     command=lambda k=key: self.show_page(k))
                btn.pack(fill="x", padx=6, pady=1)
                self.nav_buttons[key] = btn

                # Build page
                page = builders[key](self.content, self)
                self.pages[key] = page

        # Show first page
        self.show_page("analyze")

        # Queue processor
        self._process_queue()

        # Status
        broker = os.getenv("BROKER", "alpaca").upper()
        fh = "OK" if os.getenv("FINNHUB_API_KEY") else "?"
        groq = "OK" if os.getenv("GROQ_API_KEY") else "?"
        self.status.set(f"Broker: {broker} | Finnhub: {fh} | Groq: {groq} | Ready")

    def show_page(self, key):
        if self.current_page:
            self.pages[self.current_page].pack_forget()
            self.nav_buttons[self.current_page].configure(fg_color="transparent")
        self.pages[key].pack(fill="both", expand=True)
        self.nav_buttons[key].configure(fg_color="#1e3a5f")
        self.current_page = key

    def _process_queue(self):
        try:
            while True:
                cmd, data = _output_q.get_nowait()
                # Find visible output panel
                page = self.pages.get(self.current_page)
                panel = None
                if page:
                    for child in page.winfo_children():
                        if isinstance(child, OutputPanel):
                            panel = child; break
                        for sub in child.winfo_children():
                            if isinstance(sub, OutputPanel):
                                panel = sub; break
                if cmd == "append" and panel: panel.append(data)
                elif cmd == "clear" and panel: panel.clear()
                elif cmd == "status": self.status.set(data)
        except queue.Empty: pass
        self.after(80, self._process_queue)


if __name__ == "__main__":
    app = FinalAIApp()
    app.mainloop()
