"""FinalAI Quantum — Professional Desktop Trading Application"""

import os, sys, threading, json, queue
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

# ── Design System ──
C = {
    "bg":       "#090d1a",
    "surface":  "#0f1629",
    "card":     "#141b2d",
    "sidebar":  "#0c1222",
    "border":   "#1e293b",
    "accent":   "#3b82f6",
    "green":    "#10b981",
    "red":      "#ef4444",
    "purple":   "#8b5cf6",
    "amber":    "#f59e0b",
    "cyan":     "#06b6d4",
    "text":     "#f1f5f9",
    "text2":    "#94a3b8",
    "text3":    "#475569",
    "hover":    "#1a2744",
    "active":   "#172554",
    "input":    "#1e293b",
}
FONT = "Segoe UI"
MONO = "Cascadia Code"

_trading_mod = None
def T():
    global _trading_mod
    if _trading_mod is None:
        import importlib
        _trading_mod = importlib.import_module("Trading")
    return _trading_mod

_q = queue.Queue()

# ── Reusable Components ──

class Card(ctk.CTkFrame):
    def __init__(self, parent, title=None, **kw):
        super().__init__(parent, fg_color=C["card"], corner_radius=12, border_width=1, border_color=C["border"], **kw)
        if title:
            ctk.CTkLabel(self, text=title, font=(FONT, 14, "bold"), text_color=C["text"],
                          anchor="w").pack(anchor="w", padx=16, pady=(14, 6))


class Output(ctk.CTkFrame):
    def __init__(self, parent, **kw):
        super().__init__(parent, fg_color=C["surface"], corner_radius=10, **kw)
        self.tb = ctk.CTkTextbox(self, font=(MONO, 12), wrap="word", state="disabled",
                                  fg_color=C["surface"], text_color=C["text2"],
                                  corner_radius=10, border_width=0)
        self.tb.pack(fill="both", expand=True, padx=8, pady=8)

    def put(self, text):
        self.tb.configure(state="normal")
        self.tb.insert("end", text + "\n")
        self.tb.see("end")
        self.tb.configure(state="disabled")

    def clear(self):
        self.tb.configure(state="normal")
        self.tb.delete("1.0", "end")
        self.tb.configure(state="disabled")


class Btn(ctk.CTkButton):
    def __init__(self, parent, text, color=None, **kw):
        color = color or C["accent"]
        super().__init__(parent, text=text, font=(FONT, 12, "bold"), height=36,
                          corner_radius=8, fg_color=color,
                          hover_color=self._lighten(color), **kw)

    @staticmethod
    def _lighten(hex_color):
        r, g, b = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
        return f"#{min(r+30,255):02x}{min(g+30,255):02x}{min(b+30,255):02x}"


class Entry(ctk.CTkEntry):
    def __init__(self, parent, **kw):
        kw.setdefault("font", (FONT, 13))
        kw.setdefault("height", 36)
        kw.setdefault("corner_radius", 8)
        kw.setdefault("fg_color", C["input"])
        kw.setdefault("border_color", C["border"])
        kw.setdefault("border_width", 1)
        super().__init__(parent, **kw)


class MetricCard(ctk.CTkFrame):
    def __init__(self, parent, label, value, color=None, **kw):
        super().__init__(parent, fg_color=C["card"], corner_radius=10,
                          border_width=1, border_color=C["border"], **kw)
        ctk.CTkLabel(self, text=label, font=(FONT, 11), text_color=C["text3"]).pack(padx=14, pady=(10, 0), anchor="w")
        ctk.CTkLabel(self, text=value, font=(FONT, 20, "bold"),
                      text_color=color or C["text"]).pack(padx=14, pady=(2, 12), anchor="w")


def bg_run(output, status, label, fn):
    output.clear()
    output.put(f"{label}...\n")
    if status: status.set(label)
    def _w():
        try: fn()
        except Exception as e:
            import traceback
            _q.put(("put", f"\nError: {e}\n{traceback.format_exc()}"))
    threading.Thread(target=_w, daemon=True).start()


def get_data(ticker, period="5d", interval="1m"):
    import yfinance as yf
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    if hasattr(df.columns, 'levels'):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    return df

def get_ind(ticker, period="5d", interval="1m"):
    df = get_data(ticker, period, interval)
    if df is None or df.empty: return None, None
    ind = T().TechnicalAnalyzer.calculate_indicators(df)
    if ind: ind.price = float(df['Close'].iloc[-1]); ind.close = ind.price
    return df, ind

def analyzer():
    a = T().AIAnalyzer.__new__(T().AIAnalyzer); a.api_key = None; return a


# ═══════════════════════════════════════════════════
# PAGES
# ═══════════════════════════════════════════════════

def page_dashboard(parent, app):
    f = ctk.CTkScrollableFrame(parent, fg_color="transparent")

    # Hero
    hero = ctk.CTkFrame(f, fg_color=C["card"], corner_radius=14, border_width=1, border_color=C["border"])
    hero.pack(fill="x", padx=6, pady=(6, 12))
    ctk.CTkLabel(hero, text="Welcome to FinalAI Quantum", font=(FONT, 24, "bold"),
                  text_color=C["accent"]).pack(padx=20, pady=(20, 4), anchor="w")
    ctk.CTkLabel(hero, text="Ultra-advanced quantitative trading intelligence with 12 adaptive AI agents, "
                 "76+ technical signals, IBKR integration, and real-time analysis.",
                  font=(FONT, 13), text_color=C["text2"], wraplength=700).pack(padx=20, pady=(0, 16), anchor="w")

    # Metrics row
    row = ctk.CTkFrame(f, fg_color="transparent")
    row.pack(fill="x", padx=6, pady=(0, 12))
    broker = os.getenv("BROKER", "alpaca").upper()
    fh = "Active" if os.getenv("FINNHUB_API_KEY") else "Missing"
    groq = "Active" if os.getenv("GROQ_API_KEY") else "Missing"
    for label, val, color in [("Broker", broker, C["accent"]), ("Finnhub", fh, C["green"] if fh=="Active" else C["red"]),
                               ("Groq AI", groq, C["green"] if groq=="Active" else C["red"]),
                               ("Signals", "76+", C["purple"])]:
        m = MetricCard(row, label, val, color)
        m.pack(side="left", fill="x", expand=True, padx=4)

    # Quick actions
    qa = Card(f, title="Quick Actions")
    qa.pack(fill="x", padx=6, pady=(0, 12))
    btns = ctk.CTkFrame(qa, fg_color="transparent")
    btns.pack(fill="x", padx=16, pady=(0, 14))
    for label, page, color in [("Analyze Ticker", "analyze", C["accent"]),
                                ("Swarm AI", "swarm", C["purple"]),
                                ("Blind Test", "backtest", C["green"]),
                                ("Monte Carlo", "monte_carlo", C["amber"])]:
        Btn(btns, text=label, color=color, width=140,
            command=lambda p=page: app.show_page(p)).pack(side="left", padx=4, pady=4)

    # Features
    feat = Card(f, title="All Features")
    feat.pack(fill="x", padx=6, pady=(0, 12))
    features = [
        "Analyze Ticker — 76+ balanced technical signals with SL/TP",
        "Market Scanner — scan entire universes for high-confidence setups",
        "Swarm Intelligence — 12 adaptive AI agents with performance weighting",
        "Blind Prediction Test — bot predicts, you reveal the future",
        "Monte Carlo — 1M simulation price projections",
        "Multi-Timeframe — 1m / 15m / 1h / 1D signal alignment",
        "Smart Money — order blocks, FVGs, liquidity zones",
        "Options Chain — calls/puts with greeks and OI",
        "Insider Trading — corporate insider buy/sell signals",
        "Political Trades — congressional disclosure tracker",
        "Portfolio — live IBKR positions and P&L",
        "Position Sizing — risk-based calculator",
    ]
    for feat_text in features:
        ctk.CTkLabel(feat, text=f"  {feat_text}", font=(FONT, 12),
                      text_color=C["text2"], anchor="w").pack(anchor="w", padx=16, pady=1)
    ctk.CTkLabel(feat, text="").pack(pady=4)  # spacer
    return f


def page_analyze(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    card = Card(f, title="Technical Analysis")
    card.pack(fill="x", padx=6, pady=6)
    row = ctk.CTkFrame(card, fg_color="transparent")
    row.pack(fill="x", padx=16, pady=(0, 14))
    ticker_e = Entry(row, width=110, placeholder_text="AAPL")
    ticker_e.pack(side="left", padx=(0, 8))
    style_v = StringVar(value="day")
    ctk.CTkSegmentedButton(row, values=["day", "swing", "long"], variable=style_v,
                            font=(FONT, 11), height=36, corner_radius=8).pack(side="left", padx=(0, 8))
    out = Output(f)
    out.pack(fill="both", expand=True, padx=6, pady=(0, 6))

    def _run():
        t = ticker_e.get().strip().upper()
        if not t: return
        is_day = style_v.get() == "day"
        per = "5d" if is_day else ("3mo" if style_v.get()=="swing" else "1y")
        itv = "1m" if is_day else "1d"
        def work():
            df, ind = get_ind(t, per, itv)
            if ind is None: _q.put(("put", f"No data for {t}")); return
            sig = analyzer()._fallback_analysis(t, ind, 100000, 0.01, 2.5, is_day_trading=is_day)
            if not sig: _q.put(("put", "No signal")); return
            p = ind.price
            _q.put(("clear", None))
            lines = [
                f"  {t} @ ${p:.2f}",
                f"  {'BUY' if sig.action=='BUY' else 'SELL' if sig.action=='SELL' else 'HOLD'} — {sig.confidence:.0f}% confidence\n",
                f"  Stop Loss     ${sig.stop_loss:.2f}",
                f"  Take Profit 1 ${sig.take_profit_1:.2f}",
                f"  Take Profit 2 ${sig.take_profit_2:.2f}",
                f"  R:R Ratio     1:{abs(sig.take_profit_1-p)/max(0.01,abs(p-sig.stop_loss)):.1f}\n",
                f"  RSI {ind.rsi_14:.1f}  |  MACD {ind.macd:.4f}  |  ADX {ind.adx:.1f}" if ind.adx else "",
                f"  SMA20 {ind.sma_20:.2f}  |  SMA50 {ind.sma_50:.2f}",
                f"  EMA8 {ind.ema_8:.2f}  |  EMA21 {ind.ema_21:.2f}",
                f"  ATR {ind.atr:.4f} ({ind.atr_percent:.2f}%)" if ind.atr_percent else "",
                f"  Volume {ind.volume_ratio:.2f}x  |  Regime: {ind.market_regime}" if ind.market_regime else "",
            ]
            for l in lines:
                if l: _q.put(("put", l))
            if hasattr(sig, 'supporting_signals') and sig.supporting_signals:
                _q.put(("put", "\n  Supporting signals:"))
                for s in sig.supporting_signals[:12]: _q.put(("put", f"    {s}"))
            _q.put(("status", f"{t}: {sig.action} ({sig.confidence:.0f}%)"))
        bg_run(out, app.status, f"Analyzing {t}", work)

    Btn(row, text="Analyze", color=C["accent"], width=100, command=_run).pack(side="left")
    ticker_e.bind("<Return>", lambda e: _run())
    return f


def page_scanner(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    card = Card(f, title="Market Scanner")
    card.pack(fill="x", padx=6, pady=6)
    row = ctk.CTkFrame(card, fg_color="transparent")
    row.pack(fill="x", padx=16, pady=(0, 14))
    uni_v = StringVar(value="tech_leaders")
    ctk.CTkOptionMenu(row, values=["tech_leaders","sp500_top50","crypto","all"],
                       variable=uni_v, font=(FONT, 12), width=160, height=36).pack(side="left", padx=(0,8))
    conf_e = Entry(row, width=60); conf_e.insert(0, "70")
    ctk.CTkLabel(row, text="Min%", font=(FONT, 12), text_color=C["text2"]).pack(side="left", padx=(8,3))
    conf_e.pack(side="left")
    out = Output(f)
    out.pack(fill="both", expand=True, padx=6, pady=(0,6))

    def _run():
        def work():
            mod = T()
            tickers = list(getattr(mod, 'MARKET_UNIVERSES', {}).get(uni_v.get(), ['AAPL','MSFT','GOOGL','NVDA','AMZN']))
            thresh = float(conf_e.get() or 70)
            _q.put(("put", f"Scanning {len(tickers)} tickers...\n"))
            hits = 0
            for t in tickers:
                try:
                    _, ind = get_ind(t, "5d", "1m")
                    if ind is None: continue
                    sig = analyzer()._fallback_analysis(t, ind, 100000, 0.01, 2.5, is_day_trading=True)
                    if sig and sig.action != 'HOLD' and sig.confidence >= thresh:
                        hits += 1
                        _q.put(("put", f"  {sig.action:>4} {t:<8} ${ind.price:>10.2f}  {sig.confidence:.0f}%"))
                except Exception: continue
            _q.put(("put", f"\n{hits} signal(s) from {len(tickers)} scanned"))
            _q.put(("status", f"Scanner: {hits} hits"))
        bg_run(out, app.status, "Scanning", work)

    Btn(row, text="Scan", color=C["accent"], width=80, command=_run).pack(side="left", padx=8)
    return f


def page_news(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    card = Card(f, title="News & Market Intel")
    card.pack(fill="x", padx=6, pady=6)
    row = ctk.CTkFrame(card, fg_color="transparent")
    row.pack(fill="x", padx=16, pady=(0,14))
    ticker_e = Entry(row, width=110, placeholder_text="AAPL")
    ticker_e.pack(side="left", padx=(0,8))
    out = Output(f)
    out.pack(fill="both", expand=True, padx=6, pady=(0,6))

    def _run():
        t = ticker_e.get().strip().upper() or "AAPL"
        def work():
            import requests
            for name, env, url_fn in [
                ("NewsData", "NEWSDATA_API_KEY", lambda k: f"https://newsdata.io/api/1/news?apikey={k}&q={t}&language=en&size=8"),
                ("News API", "NEWS_API_KEY", lambda k: f"https://newsapi.org/v2/everything?q={t}&apiKey={k}&pageSize=8&sortBy=publishedAt"),
            ]:
                key = os.getenv(env, '')
                if not key: continue
                try:
                    r = requests.get(url_fn(key), timeout=8)
                    if r.status_code != 200: continue
                    data = r.json()
                    articles = data.get('results') or data.get('articles') or []
                    if articles:
                        _q.put(("put", f"  {name}:"))
                        for a in articles[:8]:
                            title = a.get('title', '?')
                            date = (a.get('pubDate') or a.get('publishedAt') or '')[:10]
                            _q.put(("put", f"    [{date}] {title}"))
                        _q.put(("put", ""))
                except Exception: continue
        bg_run(out, app.status, f"News: {t}", work)

    Btn(row, text="Fetch News", color=C["accent"], width=110, command=_run).pack(side="left")
    return f


def page_swarm(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    card = Card(f, title="Swarm Intelligence — 12 Adaptive AI Agents")
    card.pack(fill="x", padx=6, pady=6)
    row = ctk.CTkFrame(card, fg_color="transparent")
    row.pack(fill="x", padx=16, pady=(0,14))
    ticker_e = Entry(row, width=110, placeholder_text="AAPL")
    ticker_e.pack(side="left", padx=(0,8))
    rounds_v = StringVar(value="3")
    ctk.CTkLabel(row, text="Rounds", font=(FONT, 12), text_color=C["text2"]).pack(side="left", padx=(8,3))
    ctk.CTkOptionMenu(row, values=["2","3","4"], variable=rounds_v, width=55, height=36).pack(side="left")
    out = Output(f)
    out.pack(fill="both", expand=True, padx=6, pady=(0,6))

    def _run():
        t = ticker_e.get().strip().upper()
        if not t: return
        def work():
            _, ind = get_ind(t)
            if ind is None: _q.put(("put", "No data")); return
            swarm = T().SwarmIntelligence()
            result = swarm.analyze(t, ind, rounds=int(rounds_v.get()))
            a, c = result.get('action','HOLD'), result.get('confidence',0)
            bd = result.get('breakdown',{})
            _q.put(("put", f"\n  CONSENSUS: {a} — {c:.1f}% confidence"))
            _q.put(("put", f"  BUY {bd.get('buy',0):.0f}%  |  SELL {bd.get('sell',0):.0f}%  |  HOLD {bd.get('hold',0):.0f}%\n"))
            for r in result.get('reasons', [])[:5]: _q.put(("put", f"    {r}"))
            _q.put(("put", "\n  Agent Rankings:"))
            for ag in sorted(swarm.agents, key=lambda x: x.accuracy, reverse=True):
                bar = "*" * int(ag.accuracy * 20)
                _q.put(("put", f"    {ag.name:<22} {ag.accuracy*100:>5.0f}%  {ag.weight:.1f}x  {bar}"))
            _q.put(("status", f"Swarm: {a} on {t} ({c:.0f}%)"))
        bg_run(out, app.status, f"Swarm: {t}", work)

    Btn(row, text="Run Swarm", color=C["purple"], width=110, command=_run).pack(side="left", padx=8)
    return f


def page_backtest(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    card = Card(f, title="Blind Prediction Test")
    card.pack(fill="x", padx=6, pady=6)
    row = ctk.CTkFrame(card, fg_color="transparent")
    row.pack(fill="x", padx=16, pady=(0,14))
    ticker_e = Entry(row, width=80, placeholder_text="AAPL"); ticker_e.pack(side="left", padx=(0,6))
    start_e = Entry(row, width=100); start_e.insert(0, (datetime.now()-timedelta(days=90)).strftime('%Y-%m-%d')); start_e.pack(side="left", padx=3)
    cutoff_e = Entry(row, width=100); cutoff_e.insert(0, (datetime.now()-timedelta(days=7)).strftime('%Y-%m-%d')); cutoff_e.pack(side="left", padx=3)
    horizon_v = StringVar(value="5")
    ctk.CTkOptionMenu(row, values=["3","5","10","20"], variable=horizon_v, width=55, height=36).pack(side="left", padx=3)
    out = Output(f)
    out.pack(fill="both", expand=True, padx=6, pady=(0,6))

    def _run():
        t = ticker_e.get().strip().upper()
        if not t: return
        def work():
            import yfinance as yf
            df = yf.download(t, start=start_e.get(), end=cutoff_e.get(), interval='1d', progress=False)
            if hasattr(df.columns, 'levels'): df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            if df is None or len(df) < 20: _q.put(("put", "Not enough data")); return
            p = float(df['Close'].iloc[-1])
            ind = T().TechnicalAnalyzer.calculate_indicators(df)
            if not ind: _q.put(("put", "Indicator error")); return
            ind.price = p; ind.close = p
            sig = analyzer()._fallback_analysis(t, ind, 100000, 0.01, 2.5)
            if not sig: _q.put(("put", "No signal")); return
            _q.put(("put", f"  Bot sees {len(df)} candles ending ${p:.2f}\n"))
            _q.put(("put", f"  PREDICTION: {sig.action} ({sig.confidence:.0f}%)"))
            _q.put(("put", f"  SL ${sig.stop_loss:.2f}  |  TP ${sig.take_profit_1:.2f}\n"))
            h = int(horizon_v.get())
            end = (datetime.strptime(cutoff_e.get(), '%Y-%m-%d')+timedelta(days=h+5)).strftime('%Y-%m-%d')
            fut = yf.download(t, start=cutoff_e.get(), end=end, interval='1d', progress=False)
            if hasattr(fut.columns, 'levels'): fut.columns = [c[0] if isinstance(c, tuple) else c for c in fut.columns]
            fut = fut.head(h)
            if fut.empty: _q.put(("put", "No future data")); return
            final = float(fut['Close'].iloc[-1]); chg = (final-p)/p*100
            ok = (sig.action=='BUY' and chg>0) or (sig.action=='SELL' and chg<0) or (sig.action=='HOLD' and abs(chg)<1.5)
            _q.put(("put", f"  RESULT: ${p:.2f} -> ${final:.2f} ({chg:+.2f}%)"))
            _q.put(("put", f"  VERDICT: {'CORRECT' if ok else 'WRONG'}\n"))
            for idx, r in fut.iterrows():
                dc = (float(r['Close'])-p)/p*100
                _q.put(("put", f"    {str(idx)[:10]}  ${float(r['Close']):>8.2f}  {dc:+.2f}%"))
        bg_run(out, app.status, f"Predicting {t}", work)

    Btn(row, text="Test", color=C["green"], width=80, command=_run).pack(side="left", padx=6)
    ctk.CTkLabel(card, text="  Start → Cutoff = what bot sees.  Days = how far to reveal.",
                  font=(FONT, 11), text_color=C["text3"]).pack(anchor="w", padx=16, pady=(0,10))
    return f


def page_monte_carlo(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    card = Card(f, title="Monte Carlo Price Simulation (GBM)")
    card.pack(fill="x", padx=6, pady=6)
    row = ctk.CTkFrame(card, fg_color="transparent")
    row.pack(fill="x", padx=16, pady=(0,14))
    ticker_e = Entry(row, width=80, placeholder_text="AAPL"); ticker_e.pack(side="left", padx=(0,6))
    sims_e = Entry(row, width=100); sims_e.insert(0, "1000000"); sims_e.pack(side="left", padx=3)
    days_e = Entry(row, width=60); days_e.insert(0, "30"); days_e.pack(side="left", padx=3)
    out = Output(f)
    out.pack(fill="both", expand=True, padx=6, pady=(0,6))

    def _run():
        t = ticker_e.get().strip().upper()
        if not t: return
        def work():
            import numpy as np, yfinance as yf
            n, h = int(sims_e.get()), int(days_e.get())

            # Fetch multi-horizon data
            _q.put(("put", f"  Fetching market data for {t}..."))
            df_2y = yf.download(t, period="2y", interval="1d", progress=False)
            df_3mo = yf.download(t, period="3mo", interval="1d", progress=False)
            for _df in [df_2y, df_3mo]:
                if _df is not None and hasattr(_df.columns, 'levels'):
                    _df.columns = [c[0] if isinstance(c, tuple) else c for c in _df.columns]
            if df_2y is None or len(df_2y) < 30: _q.put(("put", "Not enough data")); return

            closes_2y = df_2y['Close'].dropna().values.astype(float)
            lr_2y = np.diff(np.log(closes_2y))
            vol_2y = float(lr_2y.std() * np.sqrt(252) * 100)
            mu_2y = float(lr_2y.mean())
            S0 = closes_2y[-1]

            # 30-day realized vol
            if df_3mo is not None and not df_3mo.empty:
                c3 = df_3mo['Close'].dropna().values.astype(float)
                lr_3mo = np.diff(np.log(c3))
                lr_30d = lr_3mo[-21:] if len(lr_3mo) >= 21 else lr_3mo
                vol_30d = float(lr_30d.std() * np.sqrt(252) * 100)
                mu_30d = float(lr_30d.mean())
            else:
                vol_30d, mu_30d = vol_2y, mu_2y

            # Use 2-year drift (safer) + 30-day vol (more current)
            mu_daily = mu_2y
            sigma = (vol_30d / 100.0) / np.sqrt(252)
            mu_ann = (np.exp(mu_daily * 252) - 1) * 100
            mu_30d_ann = (np.exp(mu_30d * 252) - 1) * 100

            _q.put(("clear", None))
            _q.put(("put", f"  {'='*60}"))
            _q.put(("put", f"  MONTE CARLO SIMULATION: {t}"))
            _q.put(("put", f"  {n:,} paths  |  {h}-day horizon  |  GBM model"))
            _q.put(("put", f"  {'='*60}\n"))

            # Market inputs
            _q.put(("put", f"  MARKET INPUTS"))
            _q.put(("put", f"  {'─'*56}"))
            _q.put(("put", f"  {'Spot Price':<28} ${S0:.2f}"))
            _q.put(("put", f"  {'2-Year Ann. Volatility':<28} {vol_2y:.1f}%"))
            _q.put(("put", f"  {'30-Day Realized Vol':<28} {vol_30d:.1f}%  (using this)"))
            _q.put(("put", f"  {'2-Year Drift (ann.)':<28} {mu_ann:+.1f}%/yr  (using this)"))
            _q.put(("put", f"  {'30-Day Drift (ann.)':<28} {mu_30d_ann:+.1f}%/yr{'  ** EXTREME' if abs(mu_30d_ann)>40 else ''}"))
            _q.put(("put", ""))

            # Drift warning
            if abs(mu_30d_ann) > 40:
                _q.put(("put", f"  ** 30-day drift is extreme ({mu_30d_ann:+.1f}%/yr)."))
                _q.put(("put", f"     Using 2-year drift instead (recommended).\n"))

            # Run simulation
            _q.put(("put", f"  Simulating {n:,} paths..."))
            rng = np.random.default_rng()
            drift = mu_daily - 0.5 * sigma**2
            paths = S0 * np.exp(np.cumsum(drift + sigma * rng.standard_normal((n, h)), axis=1))
            finals = paths[:, -1]
            returns_pct = (finals - S0) / S0 * 100

            # Price projections
            _q.put(("put", f"\n  PRICE PROJECTIONS"))
            _q.put(("put", f"  {'─'*56}"))
            for lbl, pct in [("5th  (Deep Bear)",5),("10th (Bear)",10),("25th (Cautious)",25),
                              ("50th (MEDIAN)",50),("75th (Optimistic)",75),("90th (Bull)",90),("95th (Deep Bull)",95)]:
                v = np.percentile(finals, pct); c = (v-S0)/S0*100
                marker = "  <<" if pct == 50 else ""
                _q.put(("put", f"  {lbl:<24} ${v:>10.2f}   ({c:+.1f}%){marker}"))
            _q.put(("put", f"\n  {'Mean':.<24} ${finals.mean():>10.2f}   ({(finals.mean()-S0)/S0*100:+.1f}%)"))

            # Risk metrics
            var_95 = float(np.percentile(returns_pct, 5))
            cvar_95 = float(returns_pct[returns_pct <= var_95].mean()) if (returns_pct <= var_95).any() else var_95
            running_max = np.maximum.accumulate(paths, axis=1)
            dd = (paths - running_max) / running_max * 100
            max_dd_per = dd.min(axis=1)
            median_dd = float(np.median(max_dd_per))
            worst_dd = float(np.percentile(max_dd_per, 5))

            _q.put(("put", f"\n  RISK METRICS"))
            _q.put(("put", f"  {'─'*56}"))
            _q.put(("put", f"  {'VaR (95%) — worst loss':<28} {var_95:.2f}%"))
            _q.put(("put", f"  {'CVaR (95%) — tail avg':<28} {cvar_95:.2f}%"))
            _q.put(("put", f"  {'Median Max Drawdown':<28} {median_dd:.1f}%"))
            _q.put(("put", f"  {'5th %ile Max Drawdown':<28} {worst_dd:.1f}%  (worst-case)"))

            # Strategy metrics
            years = h / 252.0
            cagr = float((np.median(finals) / S0) ** (1.0 / max(years, 0.01)) - 1) * 100
            full_paths = np.hstack([np.full((n, 1), S0), paths])
            dpr = np.diff(np.log(full_paths), axis=1)
            pm = dpr.mean(axis=1) * 252; ps = dpr.std(axis=1) * np.sqrt(252)
            sharpe = np.where(ps > 0, (pm - 0.045) / ps, 0)
            med_sharpe = float(np.median(sharpe))

            _q.put(("put", f"\n  STRATEGY METRICS"))
            _q.put(("put", f"  {'─'*56}"))
            _q.put(("put", f"  {'Median CAGR':<28} {cagr:+.1f}%"))
            _q.put(("put", f"  {'Median Sharpe Ratio':<28} {med_sharpe:.2f}"))
            _q.put(("put", f"  {'Prob Sharpe > 0':<28} {(sharpe>0).mean()*100:.1f}%"))

            # Probabilities
            _q.put(("put", f"\n  PROBABILITIES"))
            _q.put(("put", f"  {'─'*56}"))
            _q.put(("put", f"  {'Prob price goes UP':<28} {(finals>S0).mean()*100:.1f}%"))
            _q.put(("put", f"  {'Prob gain > 5%':<28} {(finals>S0*1.05).mean()*100:.1f}%"))
            _q.put(("put", f"  {'Prob gain > 10%':<28} {(finals>S0*1.10).mean()*100:.1f}%"))
            _q.put(("put", f"  {'Prob gain > 20%':<28} {(finals>S0*1.20).mean()*100:.1f}%"))
            _q.put(("put", f"  {'Prob loss > 5%':<28} {(finals<S0*0.95).mean()*100:.1f}%"))
            _q.put(("put", f"  {'Prob loss > 10%':<28} {(finals<S0*0.90).mean()*100:.1f}%"))
            _q.put(("put", f"  {'Prob loss > 20%':<28} {(finals<S0*0.80).mean()*100:.1f}%"))

            # Recommendation
            _q.put(("put", f"\n  {'='*60}"))
            _q.put(("put", f"  RECOMMENDATION"))
            _q.put(("put", f"  {'='*60}"))
            prob_up = (finals > S0).mean() * 100
            if prob_up > 60 and med_sharpe > 0.3 and median_dd > -15:
                _q.put(("put", f"  BULLISH — {prob_up:.0f}% upside probability, positive Sharpe"))
                _q.put(("put", f"  Median target: ${np.median(finals):.2f} ({(np.median(finals)-S0)/S0*100:+.1f}%)"))
            elif prob_up < 40 or median_dd < -20:
                _q.put(("put", f"  BEARISH — only {prob_up:.0f}% upside, drawdown risk {median_dd:.0f}%"))
                _q.put(("put", f"  Consider hedging or reducing exposure"))
            else:
                _q.put(("put", f"  NEUTRAL — {prob_up:.0f}% upside, moderate risk"))
                _q.put(("put", f"  Median target: ${np.median(finals):.2f} ({(np.median(finals)-S0)/S0*100:+.1f}%)"))

            _q.put(("status", f"MC: {t} median ${np.median(finals):.2f} ({h}d, {n:,} sims)"))
        bg_run(out, app.status, f"Monte Carlo: {t} ({int(sims_e.get()):,} sims)", work)

    Btn(row, text="Simulate", color=C["amber"], width=100, command=_run).pack(side="left", padx=6)
    ctk.CTkLabel(card, text="  Ticker | Simulations | Horizon (days)  •  Uses 2yr drift + 30d vol (recommended)",
                  font=(FONT, 11), text_color=C["text3"]).pack(anchor="w", padx=16, pady=(0,10))
    return f


def page_portfolio(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    card = Card(f, title="IBKR Portfolio")
    card.pack(fill="x", padx=6, pady=6)
    out = Output(f)
    out.pack(fill="both", expand=True, padx=6, pady=(0,6))
    def _run():
        def work():
            b = T().IBKRTrader()
            if not b.is_ready(): _q.put(("put", "IBKR not connected. Start TWS.")); return
            a = b.get_account()
            if a:
                _q.put(("put", f"  {b.status_line()}\n"))
                _q.put(("put", f"  Cash:          ${a['cash']:>12,.2f}"))
                _q.put(("put", f"  Equity:        ${a['equity']:>12,.2f}"))
                _q.put(("put", f"  Buying Power:  ${a['buying_power']:>12,.2f}\n"))
            for p in b.list_positions():
                pnl = p.get('unrealized_pl',0)
                _q.put(("put", f"  {p['symbol']:<10} {p['qty']:>6.0f} {p['side']:<5} ${p['avg_entry_price']:>9.2f}  P&L ${pnl:>+10.2f}"))
            b.disconnect()
        bg_run(out, app.status, "IBKR", work)
    Btn(card, text="Refresh", color=C["accent"], width=100, command=_run).pack(padx=16, pady=(0,14), anchor="w")
    return f


def page_smart_money(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    card = Card(f, title="Smart Money Detector")
    card.pack(fill="x", padx=6, pady=6)
    row = ctk.CTkFrame(card, fg_color="transparent")
    row.pack(fill="x", padx=16, pady=(0,14))
    ticker_e = Entry(row, width=110, placeholder_text="AAPL"); ticker_e.pack(side="left", padx=(0,8))
    out = Output(f)
    out.pack(fill="both", expand=True, padx=6, pady=(0,6))
    def _run():
        t = ticker_e.get().strip().upper()
        if not t: return
        def work():
            df, ind = get_ind(t, "3mo", "1d")
            if df is None: _q.put(("put", "No data")); return
            try:
                sma = T().SmartMoneyAnalyzer(); r = sma.analyze(df)
                _q.put(("put", f"  Structure: {r.get('market_structure','?')}\n"))
                for ob in r.get('order_blocks',[])[:8]: _q.put(("put", f"  OB {ob.get('type','?'):>8} @ ${ob.get('price',0):.2f}"))
                for fvg in r.get('fair_value_gaps',[])[:8]: _q.put(("put", f"  FVG {fvg.get('type','?'):>7} ${fvg.get('low',0):.2f}-${fvg.get('high',0):.2f}"))
            except Exception as e: _q.put(("put", f"Error: {e}"))
        bg_run(out, app.status, f"SMC: {t}", work)
    Btn(row, text="Detect", color=C["accent"], width=90, command=_run).pack(side="left")
    return f


def page_multi_tf(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    card = Card(f, title="Multi-Timeframe Analysis")
    card.pack(fill="x", padx=6, pady=6)
    row = ctk.CTkFrame(card, fg_color="transparent")
    row.pack(fill="x", padx=16, pady=(0,14))
    ticker_e = Entry(row, width=110, placeholder_text="AAPL"); ticker_e.pack(side="left", padx=(0,8))
    out = Output(f)
    out.pack(fill="both", expand=True, padx=6, pady=(0,6))
    def _run():
        t = ticker_e.get().strip().upper()
        if not t: return
        def work():
            _q.put(("put", f"  Multi-Timeframe: {t}\n"))
            for tf, per, itv in [("1m","5d","1m"),("15m","5d","15m"),("1h","1mo","1h"),("1D","6mo","1d")]:
                try:
                    _, ind = get_ind(t, per, itv)
                    if ind is None: continue
                    sig = analyzer()._fallback_analysis(t, ind, 100000, 0.01, 2.5, is_day_trading=(itv=="1m"))
                    if sig: _q.put(("put", f"  {tf:>6}  {sig.action:<5} {sig.confidence:>5.0f}%  RSI {ind.rsi_14:.0f}"))
                except Exception: continue
        bg_run(out, app.status, f"MTF: {t}", work)
    Btn(row, text="Analyze", color=C["accent"], width=90, command=_run).pack(side="left")
    return f


def page_options(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    card = Card(f, title="Options Chain")
    card.pack(fill="x", padx=6, pady=6)
    row = ctk.CTkFrame(card, fg_color="transparent")
    row.pack(fill="x", padx=16, pady=(0,14))
    ticker_e = Entry(row, width=110, placeholder_text="AAPL"); ticker_e.pack(side="left", padx=(0,8))
    out = Output(f)
    out.pack(fill="both", expand=True, padx=6, pady=(0,6))
    def _run():
        t = ticker_e.get().strip().upper()
        if not t: return
        def work():
            import yfinance as yf
            tk = yf.Ticker(t)
            dates = tk.options[:5]
            _q.put(("put", f"  Expirations: {', '.join(dates[:5])}\n"))
            if dates:
                chain = tk.option_chain(dates[0])
                _q.put(("put", f"  CALLS ({dates[0]}):"))
                _q.put(("put", f"  {'Strike':>8} {'Last':>8} {'Bid':>8} {'Ask':>8} {'Vol':>8} {'OI':>8} {'IV':>7}"))
                for _, r in chain.calls.head(12).iterrows():
                    _q.put(("put", f"  ${r['strike']:>7.2f} ${r['lastPrice']:>7.2f} ${r['bid']:>7.2f} ${r['ask']:>7.2f} {str(r.get('volume','')):>8} {str(r.get('openInterest','')):>8} {r.get('impliedVolatility',0)*100:>6.1f}%"))
                _q.put(("put", f"\n  PUTS ({dates[0]}):"))
                for _, r in chain.puts.head(12).iterrows():
                    _q.put(("put", f"  ${r['strike']:>7.2f} ${r['lastPrice']:>7.2f} ${r['bid']:>7.2f} ${r['ask']:>7.2f} {str(r.get('volume','')):>8} {str(r.get('openInterest','')):>8} {r.get('impliedVolatility',0)*100:>6.1f}%"))
        bg_run(out, app.status, f"Options: {t}", work)
    Btn(row, text="Load", color=C["accent"], width=80, command=_run).pack(side="left")
    return f


def page_insider(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    card = Card(f, title="Insider Trading")
    card.pack(fill="x", padx=6, pady=6)
    row = ctk.CTkFrame(card, fg_color="transparent")
    row.pack(fill="x", padx=16, pady=(0,14))
    ticker_e = Entry(row, width=110, placeholder_text="AAPL"); ticker_e.pack(side="left", padx=(0,8))
    out = Output(f)
    out.pack(fill="both", expand=True, padx=6, pady=(0,6))
    def _run():
        t = ticker_e.get().strip().upper()
        if not t: return
        def work():
            fh = os.getenv('FINNHUB_API_KEY','')
            if not fh: _q.put(("put", "Need FINNHUB_API_KEY")); return
            import requests
            r = requests.get(f"https://finnhub.io/api/v1/stock/insider-transactions?symbol={t}&token={fh}", timeout=8)
            data = r.json().get('data',[])
            _q.put(("put", f"  {len(data)} insider transactions\n"))
            for tx in data[:20]:
                act = "BUY" if tx.get('transactionCode','') in ('P','A') else "SELL" if tx.get('transactionCode')=='S' else tx.get('transactionCode','?')
                _q.put(("put", f"  {tx.get('filingDate','?'):>10}  {act:>4}  {tx.get('name','?')[:25]:<25}  {tx.get('share',0):>10,} sh  ${tx.get('transactionPrice',0):.2f}"))
        bg_run(out, app.status, f"Insider: {t}", work)
    Btn(row, text="Check", color=C["accent"], width=80, command=_run).pack(side="left")
    return f


def page_political(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    card = Card(f, title="Congressional Trades")
    card.pack(fill="x", padx=6, pady=6)
    out = Output(f)
    out.pack(fill="both", expand=True, padx=6, pady=(0,6))
    def _run():
        def work():
            import requests
            r = requests.get("https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json", timeout=15)
            if r.status_code == 200:
                for tx in r.json()[-25:]:
                    _q.put(("put", f"  {tx.get('transaction_date','?'):>10}  {tx.get('representative','?')[:22]:<22}  {tx.get('type','?'):>12}  {tx.get('ticker','?'):<6}  {tx.get('amount','?')}"))
        bg_run(out, app.status, "Political", work)
    Btn(card, text="Fetch Trades", color=C["accent"], width=120, command=_run).pack(padx=16, pady=(0,14), anchor="w")
    return f


def page_paper(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    card = Card(f, title="Paper Trading")
    card.pack(fill="x", padx=6, pady=6)
    out = Output(f)
    out.pack(fill="both", expand=True, padx=6, pady=(0,6))
    def _run():
        def work():
            p = Path("results/paper_trades.json")
            if not p.exists(): _q.put(("put", "No paper trades yet.")); return
            trades = json.loads(p.read_text())
            for t in trades[-20:]:
                _q.put(("put", f"  {t.get('ticker','?'):<8} {t.get('action','?'):<5} ${t.get('entry_price',0):.2f}  SL ${t.get('stop_loss',0):.2f}  TP ${t.get('take_profit',0):.2f}  {t.get('status','open')}"))
        bg_run(out, app.status, "Paper trades", work)
    Btn(card, text="Load Trades", color=C["accent"], width=120, command=_run).pack(padx=16, pady=(0,14), anchor="w")
    return f


def page_sizing(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    card = Card(f, title="Position Sizing Calculator")
    card.pack(fill="x", padx=6, pady=6)
    row = ctk.CTkFrame(card, fg_color="transparent")
    row.pack(fill="x", padx=16, pady=(0,14))
    entries = {}
    for lbl, default in [("Account $","100000"),("Risk %","1.0"),("Entry $","150"),("Stop $","145")]:
        ctk.CTkLabel(row, text=lbl, font=(FONT, 11), text_color=C["text2"]).pack(side="left", padx=(8,2))
        e = Entry(row, width=80); e.insert(0, default); e.pack(side="left", padx=2)
        entries[lbl] = e
    out = Output(f)
    out.pack(fill="both", expand=True, padx=6, pady=(0,6))
    def _run():
        def work():
            acct=float(entries["Account $"].get()); risk=float(entries["Risk %"].get())/100
            entry=float(entries["Entry $"].get()); sl=float(entries["Stop $"].get())
            rps=abs(entry-sl)
            if rps<=0: _q.put(("put", "SL must differ from entry")); return
            rd=acct*risk; shares=int(rd/rps)
            _q.put(("clear",None))
            _q.put(("put", f"  Account:    ${acct:>12,.2f}"))
            _q.put(("put", f"  Risk:       {risk*100:.1f}% = ${rd:,.2f}"))
            _q.put(("put", f"  Entry:      ${entry:.2f}  |  SL: ${sl:.2f}"))
            _q.put(("put", f"  Risk/Share: ${rps:.2f}\n"))
            _q.put(("put", f"  Shares:     {shares}"))
            _q.put(("put", f"  Notional:   ${shares*entry:,.2f}"))
            _q.put(("put", f"  Max Loss:   ${shares*rps:,.2f}"))
        bg_run(out, app.status, "Sizing", work)
    Btn(row, text="Calculate", color=C["accent"], width=100, command=_run).pack(side="left", padx=8)
    return f


def page_journal(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    card = Card(f, title="Trade Journal")
    card.pack(fill="x", padx=6, pady=6)
    out = Output(f)
    out.pack(fill="both", expand=True, padx=6, pady=(0,6))
    def _run():
        def work():
            p = Path("logs/auto_trades.jsonl")
            if not p.exists(): _q.put(("put", "No trades logged yet.")); return
            lines = p.read_text().strip().split('\n')
            _q.put(("put", f"  {len(lines)} trades logged\n"))
            _q.put(("put", f"  {'Date':<20} {'Ticker':<8} {'Action':<6} {'Entry':>9} {'SL':>9} {'TP':>9} {'Conf':>5} {'Ch':>6}"))
            _q.put(("put", f"  {'-'*75}"))
            for line in lines[-30:]:
                try:
                    t = json.loads(line)
                    _q.put(("put", f"  {t['time'][:19]:<20} {t['ticker']:<8} {t['action']:<6} ${t['entry']:>8.2f} ${t['stop_loss']:>8.2f} ${t['take_profit']:>8.2f} {t['confidence']:>4.0f}% {t['channel']:>6}"))
                except Exception: pass
        bg_run(out, app.status, "Journal", work)
    Btn(card, text="Load Journal", color=C["accent"], width=120, command=_run).pack(padx=16, pady=(0,14), anchor="w")
    return f


def page_settings(parent, app):
    f = ctk.CTkScrollableFrame(parent, fg_color="transparent")
    # API Keys
    card1 = Card(f, title="API Keys")
    card1.pack(fill="x", padx=6, pady=6)
    key_entries = {}
    for env, label in [("FINNHUB_API_KEY","Finnhub"),("GROQ_API_KEY","Groq"),("NEWSDATA_API_KEY","NewsData"),
                        ("NEWS_API_KEY","News API"),("ANTHROPIC_API_KEY","Anthropic")]:
        row = ctk.CTkFrame(card1, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=2)
        ctk.CTkLabel(row, text=label, font=(FONT, 12), width=100, anchor="w").pack(side="left")
        e = Entry(row, show="*"); e.pack(side="left", fill="x", expand=True, padx=4)
        val = os.getenv(env,"")
        if val: e.insert(0, val)
        key_entries[env] = e
    def save_keys():
        env_path = REPO / ".env"
        lines = env_path.read_text().splitlines() if env_path.exists() else []
        for env, entry in key_entries.items():
            val = entry.get().strip()
            if val:
                os.environ[env] = val
                found = False
                for i, l in enumerate(lines):
                    if l.startswith(f"{env}="): lines[i] = f'{env}="{val}"'; found = True; break
                if not found: lines.append(f'{env}="{val}"')
        env_path.write_text("\n".join(lines)+"\n")
        messagebox.showinfo("Saved", "Keys saved to .env")
    Btn(card1, text="Save Keys", width=100, command=save_keys).pack(padx=16, pady=(4,14), anchor="w")

    # Config
    card2 = Card(f, title="Trading Configuration")
    card2.pack(fill="x", padx=6, pady=6)
    try: config = json.loads(Path("config/config.json").read_text())
    except Exception: config = {}
    cfg_entries = {}
    for key, label, default in [("account_size","Account Size ($)",100000),("auto_trade_risk_pct","Risk/Trade (%)",1.0),
                                 ("auto_trade_max_daily","Max Trades/Day",30),("auto_trade_max_open_positions","Max Positions",8),
                                 ("auto_trade_max_daily_loss_pct","Loss Limit (%)",5.0),("auto_trade_min_confidence","Min Conf (%)",80)]:
        row = ctk.CTkFrame(card2, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=2)
        ctk.CTkLabel(row, text=label, font=(FONT, 12), width=160, anchor="w").pack(side="left")
        e = Entry(row, width=100); e.insert(0, str(config.get(key, default))); e.pack(side="left", padx=4)
        cfg_entries[key] = e
    def save_cfg():
        try: c = json.loads(Path("config/config.json").read_text())
        except Exception: c = {}
        for k, e in cfg_entries.items():
            try: c[k] = float(e.get())
            except: pass
        Path("config/config.json").write_text(json.dumps(c, indent=2))
        messagebox.showinfo("Saved", "Config saved")
    Btn(card2, text="Save Config", width=110, command=save_cfg).pack(padx=16, pady=(4,14), anchor="w")

    # Broker
    card3 = Card(f, title="Broker")
    card3.pack(fill="x", padx=6, pady=6)
    broker_v = StringVar(value=os.getenv("BROKER","alpaca"))
    ctk.CTkSegmentedButton(card3, values=["alpaca","ibkr"], variable=broker_v,
                            font=(FONT, 12), height=36).pack(padx=16, pady=(4,6), anchor="w")
    ctk.CTkLabel(card3, text="IBKR: start TWS on port 7497 before connecting",
                  font=(FONT, 11), text_color=C["text3"]).pack(padx=16, pady=(0,14), anchor="w")
    return f


# ═══════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════

class StatusBar(ctk.CTkFrame):
    def __init__(self, parent, **kw):
        super().__init__(parent, height=28, fg_color=C["sidebar"], corner_radius=0, **kw)
        self.l = ctk.CTkLabel(self, text="Ready", font=(FONT, 10), text_color=C["text3"], anchor="w")
        self.l.pack(side="left", padx=12, fill="x", expand=True)
    def set(self, t): self.l.configure(text=t)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FinalAI Quantum")
        self.geometry("1300x820")
        self.minsize(1050, 680)
        self.configure(fg_color=C["bg"])

        # Header
        hdr = ctk.CTkFrame(self, height=52, fg_color=C["sidebar"], corner_radius=0)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="    FinalAI Quantum", font=(FONT, 20, "bold"), text_color=C["accent"]).pack(side="left")
        ctk.CTkLabel(hdr, text="v7.0", font=(FONT, 11), text_color=C["text3"]).pack(side="left", padx=6)

        # Body
        body = ctk.CTkFrame(self, fg_color=C["bg"], corner_radius=0)
        body.pack(fill="both", expand=True)

        # Sidebar
        sb = ctk.CTkScrollableFrame(body, width=195, fg_color=C["sidebar"], corner_radius=0,
                                     scrollbar_button_color=C["sidebar"])
        sb.pack(side="left", fill="y")

        # Content
        self.content = ctk.CTkFrame(body, fg_color=C["bg"], corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)

        # Status
        self.status = StatusBar(self)
        self.status.pack(fill="x")

        # Pages
        MENU = [
            ("HOME", [("Dashboard", "home", "")]),
            ("ANALYSIS", [
                ("Analyze Ticker", "analyze", ""),
                ("Market Scanner", "scanner", ""),
                ("News Intel", "news", ""),
                ("Smart Money", "smart_money", ""),
                ("Multi-Timeframe", "multi_tf", ""),
            ]),
            ("AI & SWARM", [
                ("Swarm AI", "swarm", ""),
                ("Blind Prediction", "backtest", ""),
            ]),
            ("TRADING", [
                ("Portfolio (IBKR)", "portfolio", ""),
                ("Paper Trading", "paper", ""),
                ("Position Sizing", "sizing", ""),
                ("Trade Journal", "journal", ""),
            ]),
            ("QUANT LAB", [
                ("Monte Carlo", "monte_carlo", ""),
                ("Options Chain", "options", ""),
            ]),
            ("RESEARCH", [
                ("Insider Trading", "insider", ""),
                ("Political Trades", "political", ""),
            ]),
            ("SYSTEM", [("Settings", "settings", "")]),
        ]

        builders = {
            "home": page_dashboard, "analyze": page_analyze, "scanner": page_scanner,
            "news": page_news, "swarm": page_swarm, "backtest": page_backtest,
            "monte_carlo": page_monte_carlo, "portfolio": page_portfolio,
            "smart_money": page_smart_money, "multi_tf": page_multi_tf,
            "options": page_options, "insider": page_insider, "political": page_political,
            "paper": page_paper, "sizing": page_sizing, "journal": page_journal,
            "settings": page_settings,
        }

        self.pages = {}
        self.btns = {}
        self.current = None

        for section, items in MENU:
            ctk.CTkLabel(sb, text=f"  {section}", font=(FONT, 9, "bold"),
                          text_color=C["text3"]).pack(anchor="w", padx=8, pady=(14, 4))
            for label, key, _ in items:
                btn = ctk.CTkButton(sb, text=f"   {label}", font=(FONT, 12),
                                     fg_color="transparent", hover_color=C["hover"],
                                     text_color=C["text"], anchor="w", height=34,
                                     corner_radius=8,
                                     command=lambda k=key: self.show_page(k))
                btn.pack(fill="x", padx=6, pady=1)
                self.btns[key] = btn
                self.pages[key] = builders[key](self.content, self)

        self.show_page("home")
        self._poll()
        broker = os.getenv("BROKER","alpaca").upper()
        self.status.set(f"Broker: {broker}  |  Finnhub: {'OK' if os.getenv('FINNHUB_API_KEY') else '?'}  |  Groq: {'OK' if os.getenv('GROQ_API_KEY') else '?'}")

    def show_page(self, key):
        if self.current:
            self.pages[self.current].pack_forget()
            self.btns[self.current].configure(fg_color="transparent")
        self.pages[key].pack(fill="both", expand=True)
        self.btns[key].configure(fg_color=C["active"])
        self.current = key

    def _poll(self):
        try:
            while True:
                cmd, data = _q.get_nowait()
                page = self.pages.get(self.current)
                panel = self._find_output(page)
                if cmd == "put" and panel: panel.put(data)
                elif cmd == "clear" and panel: panel.clear()
                elif cmd == "status": self.status.set(data)
        except queue.Empty: pass
        self.after(80, self._poll)

    def _find_output(self, widget):
        if widget is None: return None
        if isinstance(widget, Output): return widget
        for child in widget.winfo_children():
            r = self._find_output(child)
            if r: return r
        return None


if __name__ == "__main__":
    App().mainloop()
