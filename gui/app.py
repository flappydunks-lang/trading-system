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


def bg_run(output, status, label, fn, btn=None):
    output.clear()
    output.put(f"  Loading {label}...\n")
    if status: status.set(f"Loading: {label}")
    if btn: btn.configure(state="disabled", text="Loading...")
    def _w():
        try:
            fn()
        except Exception as e:
            import traceback
            _q.put(("put", f"\nError: {e}\n{traceback.format_exc()}"))
        finally:
            if btn: _q.put(("btn_reset", btn))
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
    card = Card(f, title="Technical Analysis — 76+ Signals")
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

    btn = Btn(row, text="Analyze", color=C["accent"], width=100)
    btn._orig_text = "Analyze"

    def _run():
        t = ticker_e.get().strip().upper()
        if not t: return
        is_day = style_v.get() == "day"
        per = "5d" if is_day else ("3mo" if style_v.get()=="swing" else "1y")
        itv = "1m" if is_day else "1d"
        def work():
            df, ind = get_ind(t, per, itv)
            if ind is None: _q.put(("put", f"  No data for {t}")); return

            # Try Finnhub for live price
            try:
                import requests
                fh = os.getenv('FINNHUB_API_KEY','')
                if fh:
                    r = requests.get(f"https://finnhub.io/api/v1/quote?symbol={t}&token={fh}", timeout=3)
                    if r.status_code == 200:
                        c = r.json().get('c',0)
                        if c > 0: ind.price = float(c); ind.close = float(c)
            except Exception: pass

            sig = analyzer()._fallback_analysis(t, ind, 100000, 0.01, 2.5, is_day_trading=is_day)
            if not sig: _q.put(("put", "  No signal generated (market may be too choppy)")); return
            p = ind.price

            _q.put(("clear", None))
            _q.put(("put", f"  {'='*58}"))
            _q.put(("put", f"  ANALYSIS: {t} @ ${p:.2f}  ({style_v.get().upper()} TRADING)"))
            _q.put(("put", f"  {'='*58}\n"))

            # Signal
            _q.put(("put", f"  SIGNAL: {sig.action}  —  {sig.confidence:.0f}% confidence\n"))

            # Trade plan
            _q.put(("put", f"  TRADE PLAN"))
            _q.put(("put", f"  {'─'*54}"))
            _q.put(("put", f"  {'Entry Price':<24} ${p:.2f}"))
            _q.put(("put", f"  {'Stop Loss':<24} ${sig.stop_loss:.2f}  ({(sig.stop_loss-p)/p*100:+.2f}%)"))
            _q.put(("put", f"  {'Take Profit 1':<24} ${sig.take_profit_1:.2f}  ({(sig.take_profit_1-p)/p*100:+.2f}%)"))
            _q.put(("put", f"  {'Take Profit 2':<24} ${sig.take_profit_2:.2f}  ({(sig.take_profit_2-p)/p*100:+.2f}%)"))
            _q.put(("put", f"  {'Take Profit 3':<24} ${sig.take_profit_3:.2f}  ({(sig.take_profit_3-p)/p*100:+.2f}%)"))
            risk = abs(p - sig.stop_loss); reward = abs(sig.take_profit_1 - p)
            _q.put(("put", f"  {'Risk/Share':<24} ${risk:.2f}"))
            _q.put(("put", f"  {'Reward/Share':<24} ${reward:.2f}"))
            _q.put(("put", f"  {'R:R Ratio':<24} 1:{reward/max(0.01,risk):.1f}"))

            # Position sizing
            acct = 100000
            shares = int(acct * 0.01 / max(0.01, risk))
            _q.put(("put", f"\n  POSITION SIZING (1% risk on $100K)"))
            _q.put(("put", f"  {'─'*54}"))
            _q.put(("put", f"  {'Shares':<24} {shares}"))
            _q.put(("put", f"  {'Notional':<24} ${shares * p:,.2f}"))
            _q.put(("put", f"  {'Max Loss':<24} ${shares * risk:,.2f}"))
            _q.put(("put", f"  {'Max Gain (TP1)':<24} ${shares * reward:,.2f}"))

            # Indicators
            _q.put(("put", f"\n  KEY INDICATORS"))
            _q.put(("put", f"  {'─'*54}"))
            _q.put(("put", f"  {'RSI(14)':<24} {ind.rsi_14:.1f}"))
            if ind.rsi_7: _q.put(("put", f"  {'RSI(7)':<24} {ind.rsi_7:.1f}"))
            _q.put(("put", f"  {'MACD':<24} {ind.macd:.4f}  (Signal: {ind.macd_signal:.4f})"))
            if ind.macd_histogram is not None: _q.put(("put", f"  {'MACD Histogram':<24} {ind.macd_histogram:.4f}"))
            if ind.adx: _q.put(("put", f"  {'ADX':<24} {ind.adx:.1f}"))
            if ind.plus_di: _q.put(("put", f"  {'+DI / -DI':<24} {ind.plus_di:.1f} / {ind.minus_di:.1f}"))
            _q.put(("put", f"  {'ATR':<24} {ind.atr:.4f} ({ind.atr_percent:.2f}%)" if ind.atr_percent else ""))
            if ind.stochastic_k: _q.put(("put", f"  {'Stochastic K/D':<24} {ind.stochastic_k:.1f} / {ind.stochastic_d:.1f}"))
            if ind.williams_r: _q.put(("put", f"  {'Williams %R':<24} {ind.williams_r:.1f}"))
            if ind.cci: _q.put(("put", f"  {'CCI':<24} {ind.cci:.1f}"))
            if ind.mfi: _q.put(("put", f"  {'MFI':<24} {ind.mfi:.1f}"))
            if ind.volume_ratio: _q.put(("put", f"  {'Volume Ratio':<24} {ind.volume_ratio:.2f}x"))
            if ind.market_regime: _q.put(("put", f"  {'Market Regime':<24} {ind.market_regime} ({ind.regime_confidence:.0f}%)"))

            # Moving averages
            _q.put(("put", f"\n  MOVING AVERAGES"))
            _q.put(("put", f"  {'─'*54}"))
            _q.put(("put", f"  {'SMA 20 / 50':<24} ${ind.sma_20:.2f} / ${ind.sma_50:.2f}"))
            if ind.sma_200: _q.put(("put", f"  {'SMA 200':<24} ${ind.sma_200:.2f}"))
            _q.put(("put", f"  {'EMA 8 / 21 / 34':<24} ${ind.ema_8:.2f} / ${ind.ema_21:.2f} / ${ind.ema_34:.2f}"))
            if ind.bb_upper: _q.put(("put", f"  {'Bollinger':<24} ${ind.bb_lower:.2f} — ${ind.bb_middle:.2f} — ${ind.bb_upper:.2f}"))
            if ind.vwap: _q.put(("put", f"  {'VWAP':<24} ${ind.vwap:.2f}"))

            # Ichimoku
            if ind.tenkan_sen and ind.kijun_sen:
                _q.put(("put", f"\n  ICHIMOKU"))
                _q.put(("put", f"  {'─'*54}"))
                _q.put(("put", f"  {'Tenkan / Kijun':<24} ${ind.tenkan_sen:.2f} / ${ind.kijun_sen:.2f}"))
                if ind.senkou_a: _q.put(("put", f"  {'Cloud (A/B)':<24} ${ind.senkou_a:.2f} / ${ind.senkou_b:.2f}"))

            # Supporting signals
            if hasattr(sig, 'supporting_signals') and sig.supporting_signals:
                _q.put(("put", f"\n  SIGNALS FIRED ({len(sig.supporting_signals)})"))
                _q.put(("put", f"  {'─'*54}"))
                for s in sig.supporting_signals[:15]: _q.put(("put", f"    {s}"))

            # Risk factors
            risk_flags = []
            if ind.atr_percent and ind.atr_percent > 2.0: risk_flags.append(f"High ATR ({ind.atr_percent:.1f}%)")
            if ind.volume_ratio and ind.volume_ratio < 0.5: risk_flags.append("Very low volume")
            if ind.rsi_14 > 85 or ind.rsi_14 < 15: risk_flags.append(f"Extreme RSI ({ind.rsi_14:.0f})")
            if risk_flags:
                _q.put(("put", f"\n  RISK FLAGS"))
                _q.put(("put", f"  {'─'*54}"))
                for rf in risk_flags: _q.put(("put", f"    {rf}"))

            _q.put(("status", f"{t}: {sig.action} ({sig.confidence:.0f}%) @ ${p:.2f}"))
        bg_run(out, app.status, f"Analyzing {t}", work, btn)

    btn.configure(command=_run)
    btn.pack(side="left")
    ticker_e.bind("<Return>", lambda e: _run())
    return f


def page_scanner(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    card = Card(f, title="Market Scanner — Multi-Universe")
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
    btn = Btn(row, text="Scan", color=C["accent"], width=80)
    btn._orig_text = "Scan"

    def _run():
        def work():
            mod = T()
            tickers = list(getattr(mod, 'MARKET_UNIVERSES', {}).get(uni_v.get(), ['AAPL','MSFT','GOOGL','NVDA','AMZN']))
            thresh = float(conf_e.get() or 70)
            _q.put(("clear", None))
            _q.put(("put", f"  {'='*62}"))
            _q.put(("put", f"  SCANNING: {uni_v.get().upper()}  ({len(tickers)} tickers, min {thresh:.0f}%)"))
            _q.put(("put", f"  {'='*62}\n"))
            _q.put(("put", f"  {'Signal':>6} {'Ticker':<8} {'Price':>10} {'Conf':>6} {'RSI':>6} {'Regime':<10}"))
            _q.put(("put", f"  {'─'*56}"))
            hits = []
            for i, t in enumerate(tickers):
                try:
                    _, ind = get_ind(t, "5d", "1m")
                    if ind is None: continue
                    sig = analyzer()._fallback_analysis(t, ind, 100000, 0.01, 2.5, is_day_trading=True)
                    if sig and sig.action != 'HOLD' and sig.confidence >= thresh:
                        hits.append((t, sig, ind))
                        reg = (ind.market_regime or "?")[:8]
                        _q.put(("put", f"  {sig.action:>6} {t:<8} ${ind.price:>9.2f} {sig.confidence:>5.0f}% {ind.rsi_14:>5.0f} {reg}"))
                    if (i+1) % 5 == 0: _q.put(("status", f"Scanning {i+1}/{len(tickers)}..."))
                except Exception: continue
            _q.put(("put", f"\n  {'='*56}"))
            _q.put(("put", f"  {len(hits)} signal(s) from {len(tickers)} scanned"))
            if hits:
                buys = sum(1 for _,s,_ in hits if s.action=='BUY')
                sells = len(hits) - buys
                _q.put(("put", f"  BUY: {buys}  |  SELL: {sells}"))
                best = max(hits, key=lambda x: x[1].confidence)
                _q.put(("put", f"\n  Best signal: {best[0]} {best[1].action} ({best[1].confidence:.0f}%) @ ${best[2].price:.2f}"))
            _q.put(("status", f"Scanner: {len(hits)} hits"))
        bg_run(out, app.status, f"Scanning {uni_v.get()}", work, btn)

    btn.configure(command=_run)
    btn.pack(side="left", padx=8)
    return f


def page_news(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    card = Card(f, title="News & Market Intelligence")
    card.pack(fill="x", padx=6, pady=6)
    row = ctk.CTkFrame(card, fg_color="transparent")
    row.pack(fill="x", padx=16, pady=(0,14))
    ticker_e = Entry(row, width=110, placeholder_text="AAPL")
    ticker_e.pack(side="left", padx=(0,8))
    out = Output(f)
    out.pack(fill="both", expand=True, padx=6, pady=(0,6))
    btn = Btn(row, text="Fetch News", color=C["accent"], width=110)
    btn._orig_text = "Fetch News"

    def _run():
        t = ticker_e.get().strip().upper() or "AAPL"
        def work():
            import requests
            _q.put(("clear", None))
            _q.put(("put", f"  {'='*58}"))
            _q.put(("put", f"  NEWS & MARKET INTEL: {t}"))
            _q.put(("put", f"  {'='*58}\n"))

            # Finnhub company news
            fh = os.getenv('FINNHUB_API_KEY','')
            if fh:
                try:
                    from_d = (datetime.now()-timedelta(days=7)).strftime('%Y-%m-%d')
                    to_d = datetime.now().strftime('%Y-%m-%d')
                    r = requests.get(f"https://finnhub.io/api/v1/company-news?symbol={t}&from={from_d}&to={to_d}&token={fh}", timeout=8)
                    if r.status_code == 200:
                        news = r.json()[:8]
                        if news:
                            _q.put(("put", f"  FINNHUB COMPANY NEWS ({len(news)} articles)"))
                            _q.put(("put", f"  {'─'*54}"))
                            for n in news:
                                _q.put(("put", f"    [{n.get('datetime','')[:10] if isinstance(n.get('datetime'),str) else datetime.fromtimestamp(n.get('datetime',0)).strftime('%Y-%m-%d')}] {n.get('headline','?')[:75]}"))
                                if n.get('summary'): _q.put(("put", f"      {n['summary'][:100]}..."))
                            _q.put(("put", ""))
                except Exception: pass

            for name, env, url_fn, key_r, key_a in [
                ("NEWSDATA", "NEWSDATA_API_KEY",
                 lambda k: f"https://newsdata.io/api/1/news?apikey={k}&q={t}&language=en&size=8",
                 "results", None),
                ("NEWS API", "NEWS_API_KEY",
                 lambda k: f"https://newsapi.org/v2/everything?q={t}&apiKey={k}&pageSize=8&sortBy=publishedAt",
                 None, "articles"),
            ]:
                key = os.getenv(env, '')
                if not key: continue
                try:
                    r = requests.get(url_fn(key), timeout=8)
                    if r.status_code != 200: continue
                    data = r.json()
                    articles = data.get(key_r) or data.get(key_a) or data.get('results') or data.get('articles') or []
                    if articles:
                        _q.put(("put", f"  {name} HEADLINES"))
                        _q.put(("put", f"  {'─'*54}"))
                        for a in articles[:8]:
                            title = a.get('title', '?')
                            date = (a.get('pubDate') or a.get('publishedAt') or '')[:10]
                            source = a.get('source_id') or (a.get('source',{}).get('name','') if isinstance(a.get('source'),dict) else '')
                            _q.put(("put", f"    [{date}] {title}"))
                            if source: _q.put(("put", f"      Source: {source}"))
                        _q.put(("put", ""))
                except Exception: continue
            _q.put(("status", f"News loaded for {t}"))
        bg_run(out, app.status, f"News: {t}", work, btn)

    btn.configure(command=_run)
    btn.pack(side="left")
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
    btn = Btn(row, text="Run Swarm", color=C["purple"], width=110)
    btn._orig_text = "Run Swarm"

    def _run():
        t = ticker_e.get().strip().upper()
        if not t: return
        def work():
            _, ind = get_ind(t)
            if ind is None: _q.put(("put", "  No data")); return
            _q.put(("clear", None))
            _q.put(("put", f"  {'='*58}"))
            _q.put(("put", f"  SWARM INTELLIGENCE: {t} @ ${ind.price:.2f}"))
            _q.put(("put", f"  12 agents x {rounds_v.get()} debate rounds via Groq LLM"))
            _q.put(("put", f"  {'='*58}\n"))
            _q.put(("put", f"  Agents are deliberating... (this takes 1-3 minutes)\n"))

            swarm = T().SwarmIntelligence()
            result = swarm.analyze(t, ind, rounds=int(rounds_v.get()))
            a, c = result.get('action','HOLD'), result.get('confidence',0)
            bd = result.get('breakdown',{})

            _q.put(("put", f"\n  {'='*58}"))
            _q.put(("put", f"  CONSENSUS: {a} — {c:.1f}% confidence"))
            _q.put(("put", f"  {'='*58}\n"))
            _q.put(("put", f"  {'BUY':>8}: {bd.get('buy',0):>5.1f}%"))
            _q.put(("put", f"  {'SELL':>8}: {bd.get('sell',0):>5.1f}%"))
            _q.put(("put", f"  {'HOLD':>8}: {bd.get('hold',0):>5.1f}%"))

            reasons = result.get('reasons', [])
            if reasons:
                _q.put(("put", f"\n  TOP REASONS"))
                _q.put(("put", f"  {'─'*54}"))
                for r in reasons[:6]: _q.put(("put", f"    {r}"))

            _q.put(("put", f"\n  AGENT LEADERBOARD"))
            _q.put(("put", f"  {'─'*54}"))
            _q.put(("put", f"  {'Agent':<22} {'Accuracy':>8} {'Weight':>7} {'Calls':>6}  Performance"))
            for ag in sorted(swarm.agents, key=lambda x: x.accuracy, reverse=True):
                bar = "|" * int(ag.accuracy * 20)
                _q.put(("put", f"  {ag.name:<22} {ag.accuracy*100:>7.0f}% {ag.weight:>6.1f}x {ag.total_calls:>5}  {bar}"))

            _q.put(("status", f"Swarm: {a} on {t} ({c:.0f}%)"))
        bg_run(out, app.status, f"Swarm: {t} ({rounds_v.get()} rounds)", work, btn)

    btn.configure(command=_run)
    btn.pack(side="left", padx=8)
    ctk.CTkLabel(card, text="  Agents learn from mistakes — accuracy improves over time. Weight 0.3x-3.0x.",
                  font=(FONT, 11), text_color=C["text3"]).pack(anchor="w", padx=16, pady=(0,10))
    return f


def page_backtest(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    card = Card(f, title="Blind Prediction Test — Accuracy Validator")
    card.pack(fill="x", padx=6, pady=6)
    row = ctk.CTkFrame(card, fg_color="transparent")
    row.pack(fill="x", padx=16, pady=(0,6))
    for lbl in ["Ticker","Start","Cutoff","Days"]:
        ctk.CTkLabel(row, text=lbl, font=(FONT, 10), text_color=C["text3"]).pack(side="left", padx=(6,2))
        if lbl == "Ticker":
            ticker_e = Entry(row, width=75, placeholder_text="AAPL"); ticker_e.pack(side="left", padx=(0,4))
        elif lbl == "Start":
            start_e = Entry(row, width=95); start_e.insert(0, (datetime.now()-timedelta(days=90)).strftime('%Y-%m-%d')); start_e.pack(side="left", padx=(0,4))
        elif lbl == "Cutoff":
            cutoff_e = Entry(row, width=95); cutoff_e.insert(0, (datetime.now()-timedelta(days=7)).strftime('%Y-%m-%d')); cutoff_e.pack(side="left", padx=(0,4))
        else:
            horizon_v = StringVar(value="5")
            ctk.CTkOptionMenu(row, values=["3","5","10","20"], variable=horizon_v, width=55, height=36).pack(side="left", padx=(0,4))
    out = Output(f)
    out.pack(fill="both", expand=True, padx=6, pady=(0,6))
    btn = Btn(row, text="Predict", color=C["green"], width=85)
    btn._orig_text = "Predict"

    def _run():
        t = ticker_e.get().strip().upper()
        if not t: return
        def work():
            import yfinance as yf, numpy as np
            df = yf.download(t, start=start_e.get(), end=cutoff_e.get(), interval='1d', progress=False)
            if hasattr(df.columns, 'levels'): df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            if df is None or len(df) < 20: _q.put(("put", "  Not enough data (need 20+ bars)")); return
            p = float(df['Close'].iloc[-1])
            ind = T().TechnicalAnalyzer.calculate_indicators(df)
            if not ind: _q.put(("put", "  Indicator error")); return
            ind.price = p; ind.close = p
            sig = analyzer()._fallback_analysis(t, ind, 100000, 0.01, 2.5)
            if not sig: _q.put(("put", "  No signal generated")); return

            _q.put(("clear", None))
            _q.put(("put", f"  {'='*58}"))
            _q.put(("put", f"  BLIND PREDICTION TEST: {t}"))
            _q.put(("put", f"  Bot sees: {start_e.get()} to {cutoff_e.get()} ({len(df)} candles)"))
            _q.put(("put", f"  {'='*58}\n"))

            _q.put(("put", f"  PREDICTION"))
            _q.put(("put", f"  {'─'*54}"))
            _q.put(("put", f"  {'Signal':<20} {sig.action} ({sig.confidence:.0f}%)"))
            _q.put(("put", f"  {'Last Price':<20} ${p:.2f}"))
            _q.put(("put", f"  {'Stop Loss':<20} ${sig.stop_loss:.2f}  ({(sig.stop_loss-p)/p*100:+.2f}%)"))
            _q.put(("put", f"  {'Take Profit':<20} ${sig.take_profit_1:.2f}  ({(sig.take_profit_1-p)/p*100:+.2f}%)"))

            # Reveal
            h = int(horizon_v.get())
            end = (datetime.strptime(cutoff_e.get(), '%Y-%m-%d')+timedelta(days=h+5)).strftime('%Y-%m-%d')
            fut = yf.download(t, start=cutoff_e.get(), end=end, interval='1d', progress=False)
            if hasattr(fut.columns, 'levels'): fut.columns = [c[0] if isinstance(c, tuple) else c for c in fut.columns]
            fut = fut.head(h)
            if fut.empty: _q.put(("put", "\n  No future data available")); return

            final = float(fut['Close'].iloc[-1])
            high_f = float(fut['High'].max())
            low_f = float(fut['Low'].min())
            chg = (final-p)/p*100
            max_up = (high_f-p)/p*100
            max_down = (low_f-p)/p*100

            ok = (sig.action=='BUY' and chg>0) or (sig.action=='SELL' and chg<0) or (sig.action=='HOLD' and abs(chg)<1.5)
            sl_hit = (sig.action=='BUY' and low_f<=sig.stop_loss) or (sig.action=='SELL' and high_f>=sig.stop_loss)
            tp_hit = (sig.action=='BUY' and high_f>=sig.take_profit_1) or (sig.action=='SELL' and low_f<=sig.take_profit_1)

            _q.put(("put", f"\n  WHAT ACTUALLY HAPPENED ({h} trading days)"))
            _q.put(("put", f"  {'─'*54}"))
            _q.put(("put", f"  {'Final Price':<20} ${final:.2f}  ({chg:+.2f}%)"))
            _q.put(("put", f"  {'Max Upside':<20} ${high_f:.2f}  ({max_up:+.2f}%)"))
            _q.put(("put", f"  {'Max Downside':<20} ${low_f:.2f}  ({max_down:+.2f}%)"))
            _q.put(("put", f"  {'SL Hit':<20} {'YES' if sl_hit else 'NO'}"))
            _q.put(("put", f"  {'TP Hit':<20} {'YES' if tp_hit else 'NO'}"))

            if tp_hit and not sl_hit:
                _q.put(("put", f"\n  TRADE RESULT: PROFITABLE (TP hit, SL safe)"))
            elif sl_hit and not tp_hit:
                _q.put(("put", f"\n  TRADE RESULT: LOSS (SL hit before TP)"))
            elif tp_hit and sl_hit:
                _q.put(("put", f"\n  TRADE RESULT: UNCLEAR (both SL and TP were touched)"))

            _q.put(("put", f"\n  {'='*58}"))
            _q.put(("put", f"  VERDICT: {'CORRECT' if ok else 'WRONG'} — bot said {sig.action}, market went {chg:+.2f}%"))
            _q.put(("put", f"  {'='*58}"))

            _q.put(("put", f"\n  FUTURE CANDLES (hidden from bot)"))
            _q.put(("put", f"  {'─'*54}"))
            _q.put(("put", f"  {'Date':<12} {'Open':>9} {'High':>9} {'Low':>9} {'Close':>9} {'Chg':>8}"))
            for idx, r in fut.iterrows():
                dc = (float(r['Close'])-p)/p*100
                _q.put(("put", f"  {str(idx)[:10]:<12} ${float(r['Open']):>8.2f} ${float(r['High']):>8.2f} ${float(r['Low']):>8.2f} ${float(r['Close']):>8.2f} {dc:>+7.2f}%"))

            _q.put(("status", f"Backtest: {sig.action} -> {chg:+.1f}% {'CORRECT' if ok else 'WRONG'}"))
        bg_run(out, app.status, f"Predicting {t}", work, btn)

    btn.configure(command=_run)
    btn.pack(side="left", padx=6)
    ctk.CTkLabel(card, text="  Bot sees ONLY candles from Start to Cutoff. Then we reveal what happened after.",
                  font=(FONT, 11), text_color=C["text3"]).pack(anchor="w", padx=16, pady=(4,10))
    return f


def page_monte_carlo(parent, app):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    card = Card(f, title="Monte Carlo — GBM + Jump Diffusion + Multi-Scenario")
    card.pack(fill="x", padx=6, pady=6)
    row = ctk.CTkFrame(card, fg_color="transparent")
    row.pack(fill="x", padx=16, pady=(0,6))
    ticker_e = Entry(row, width=80, placeholder_text="AAPL"); ticker_e.pack(side="left", padx=(0,6))
    sims_e = Entry(row, width=90); sims_e.insert(0, "1000000"); sims_e.pack(side="left", padx=3)
    days_e = Entry(row, width=55); days_e.insert(0, "30"); days_e.pack(side="left", padx=3)
    drift_v = StringVar(value="risk-free")
    ctk.CTkLabel(row, text="Drift:", font=(FONT, 11), text_color=C["text2"]).pack(side="left", padx=(8,2))
    ctk.CTkOptionMenu(row, values=["risk-free","neutral","2yr-hist","shrinkage"],
                       variable=drift_v, width=110, height=36, font=(FONT, 11)).pack(side="left")
    out = Output(f)
    out.pack(fill="both", expand=True, padx=6, pady=(0,6))
    btn = Btn(row, text="Simulate", color=C["amber"], width=100)
    btn._orig_text = "Simulate"

    def _run():
        t = ticker_e.get().strip().upper()
        if not t: return
        def work():
            import numpy as np, yfinance as yf
            n, h = int(sims_e.get()), int(days_e.get())
            RF_RATE = 0.045  # 4.5% risk-free rate

            _q.put(("put", f"  Fetching data for {t}..."))
            df_2y = yf.download(t, period="2y", interval="1d", progress=False)
            df_3mo = yf.download(t, period="3mo", interval="1d", progress=False)
            for _df in [df_2y, df_3mo]:
                if _df is not None and hasattr(_df.columns, 'levels'):
                    _df.columns = [c[0] if isinstance(c, tuple) else c for c in _df.columns]
            if df_2y is None or len(df_2y) < 60: _q.put(("put", "  Need 60+ days of data")); return

            closes_2y = df_2y['Close'].dropna().values.astype(float)
            lr_2y = np.diff(np.log(closes_2y))
            vol_2y_ann = float(lr_2y.std() * np.sqrt(252) * 100)
            mu_2y_daily = float(lr_2y.mean())
            mu_2y_ann = (np.exp(mu_2y_daily * 252) - 1) * 100
            S0 = closes_2y[-1]

            # 30-day realized vol (multiple regimes)
            c3 = df_3mo['Close'].dropna().values.astype(float) if df_3mo is not None and not df_3mo.empty else closes_2y
            lr_3mo = np.diff(np.log(c3))
            lr_30d = lr_3mo[-21:] if len(lr_3mo) >= 21 else lr_3mo
            vol_30d = float(lr_30d.std() * np.sqrt(252) * 100)

            # Volatility regimes from 2-year data
            vol_windows = []
            for i in range(0, len(lr_2y) - 21, 21):
                w = lr_2y[i:i+21]
                vol_windows.append(float(w.std() * np.sqrt(252) * 100))
            vol_low = np.percentile(vol_windows, 20) if vol_windows else vol_2y_ann * 0.7
            vol_med = np.percentile(vol_windows, 50) if vol_windows else vol_2y_ann
            vol_high = np.percentile(vol_windows, 80) if vol_windows else vol_2y_ann * 1.4

            # Drift selection
            drift_choice = drift_v.get()
            if drift_choice == "risk-free":
                mu_daily = np.log(1 + RF_RATE) / 252
                drift_label = f"Risk-free rate ({RF_RATE*100:.1f}%/yr)"
            elif drift_choice == "neutral":
                mu_daily = 0.0
                drift_label = "Neutral (0%/yr)"
            elif drift_choice == "shrinkage":
                mu_daily = 0.70 * (np.log(1 + RF_RATE) / 252) + 0.30 * mu_2y_daily
                drift_label = f"Shrinkage (70% RF + 30% 2yr)"
            else:
                # Cap 2yr drift to ±25%/yr
                cap = np.log(1.25) / 252
                mu_daily = max(-cap, min(cap, mu_2y_daily))
                drift_label = f"2yr historical (capped ±25%/yr)"

            mu_ann_used = (np.exp(mu_daily * 252) - 1) * 100
            sigma = vol_30d / 100.0 / np.sqrt(252)

            # Jump diffusion parameters (Merton model)
            jump_lambda = 0.05  # ~12 jumps/year
            jump_mu = -0.02     # avg jump = -2% (slightly negative, crashes > rallies)
            jump_sigma = 0.04   # jump volatility = 4%

            _q.put(("clear", None))
            _q.put(("put", f"  {'='*64}"))
            _q.put(("put", f"  MONTE CARLO: {t} @ ${S0:.2f}"))
            _q.put(("put", f"  {n:,} paths  |  {h}-day horizon  |  GBM + Jump Diffusion"))
            _q.put(("put", f"  {'='*64}\n"))

            _q.put(("put", f"  MODEL INPUTS"))
            _q.put(("put", f"  {'─'*60}"))
            _q.put(("put", f"  {'Spot Price':<30} ${S0:.2f}"))
            _q.put(("put", f"  {'Drift (mu)':<30} {drift_label}"))
            _q.put(("put", f"  {'  Annual equiv.':<30} {mu_ann_used:+.2f}%/yr"))
            _q.put(("put", f"  {'Volatility (30d realized)':<30} {vol_30d:.1f}%"))
            _q.put(("put", f"  {'Volatility (2yr avg)':<30} {vol_2y_ann:.1f}%"))
            _q.put(("put", f"  {'Vol regimes (20/50/80)':<30} {vol_low:.1f}% / {vol_med:.1f}% / {vol_high:.1f}%"))
            _q.put(("put", f"  {'Jump intensity (lambda)':<30} {jump_lambda:.2f} ({jump_lambda*252:.0f} jumps/yr)"))
            _q.put(("put", f"  {'Jump size (mu/sigma)':<30} {jump_mu*100:+.1f}% / {jump_sigma*100:.1f}%"))

            if mu_2y_ann > 40 or mu_2y_ann < -20:
                _q.put(("put", f"\n  NOTE: Raw 2yr drift was {mu_2y_ann:+.1f}%/yr (extreme)."))
                _q.put(("put", f"  Using '{drift_choice}' drift to avoid unrealistic projections."))

            # === SIMULATE WITH JUMP DIFFUSION ===
            _q.put(("put", f"\n  Simulating {n:,} paths with jump diffusion...\n"))
            rng = np.random.default_rng()

            # Compensated drift (remove jump component from drift to keep martingale)
            jump_compensation = jump_lambda * (np.exp(jump_mu + 0.5 * jump_sigma**2) - 1)
            drift_comp = mu_daily - 0.5 * sigma**2 - jump_compensation

            # GBM diffusion
            Z = rng.standard_normal((n, h))
            diffusion = drift_comp + sigma * Z

            # Poisson jumps
            jumps = rng.poisson(jump_lambda, (n, h))
            jump_sizes = jumps * (jump_mu + jump_sigma * rng.standard_normal((n, h)))

            # Combined
            log_returns = diffusion + jump_sizes
            paths = S0 * np.exp(np.cumsum(log_returns, axis=1))
            finals = paths[:, -1]
            returns_pct = (finals - S0) / S0 * 100

            # === PRICE PROJECTIONS ===
            _q.put(("put", f"  PRICE PROJECTIONS"))
            _q.put(("put", f"  {'─'*60}"))
            for lbl, pct in [("1st  (Tail risk)",1),("5th  (Deep Bear)",5),("10th (Bear)",10),
                              ("25th (Cautious)",25),("50th (MEDIAN)",50),("75th (Optimistic)",75),
                              ("90th (Bull)",90),("95th (Deep Bull)",95),("99th (Tail upside)",99)]:
                v = np.percentile(finals, pct); c = (v-S0)/S0*100
                marker = "  <<" if pct == 50 else ""
                _q.put(("put", f"  {lbl:<24} ${v:>10.2f}   ({c:+.1f}%){marker}"))
            _q.put(("put", f"\n  {'Mean':.<24} ${finals.mean():>10.2f}   ({(finals.mean()-S0)/S0*100:+.1f}%)"))

            # === RISK METRICS ===
            var_95 = float(np.percentile(returns_pct, 5))
            var_99 = float(np.percentile(returns_pct, 1))
            cvar_95 = float(returns_pct[returns_pct <= var_95].mean()) if (returns_pct <= var_95).any() else var_95
            running_max = np.maximum.accumulate(paths, axis=1)
            dd = (paths - running_max) / running_max * 100
            max_dd_per = dd.min(axis=1)
            median_dd = float(np.median(max_dd_per))
            worst_dd = float(np.percentile(max_dd_per, 5))

            _q.put(("put", f"\n  RISK METRICS"))
            _q.put(("put", f"  {'─'*60}"))
            _q.put(("put", f"  {'VaR (95%)':<30} {var_95:.2f}%"))
            _q.put(("put", f"  {'VaR (99%)':<30} {var_99:.2f}%"))
            _q.put(("put", f"  {'CVaR (95%) — expected tail':<30} {cvar_95:.2f}%"))
            _q.put(("put", f"  {'Median Max Drawdown':<30} {median_dd:.1f}%"))
            _q.put(("put", f"  {'Worst-case Drawdown (5th)':<30} {worst_dd:.1f}%"))

            # === STRATEGY METRICS ===
            years = h / 252.0
            cagr = float((np.median(finals) / S0) ** (1.0 / max(years, 0.01)) - 1) * 100
            full_paths = np.hstack([np.full((n, 1), S0), paths])
            dpr = np.diff(np.log(full_paths), axis=1)
            pm = dpr.mean(axis=1) * 252; ps = dpr.std(axis=1) * np.sqrt(252)
            sharpe = np.where(ps > 0, (pm - RF_RATE) / ps, 0)
            med_sharpe = float(np.median(sharpe))

            _q.put(("put", f"\n  STRATEGY METRICS"))
            _q.put(("put", f"  {'─'*60}"))
            _q.put(("put", f"  {'Median CAGR':<30} {cagr:+.1f}%"))
            _q.put(("put", f"  {'Median Sharpe (vs RF)':<30} {med_sharpe:.2f}"))
            _q.put(("put", f"  {'Prob Sharpe > 0':<30} {(sharpe>0).mean()*100:.1f}%"))

            # === PROBABILITIES ===
            _q.put(("put", f"\n  PROBABILITIES"))
            _q.put(("put", f"  {'─'*60}"))
            _q.put(("put", f"  {'Price goes UP':<30} {(finals>S0).mean()*100:.1f}%"))
            for pct in [5, 10, 20, 30]:
                _q.put(("put", f"  {'Gain > ' + str(pct) + '%':<30} {(finals>S0*(1+pct/100)).mean()*100:.1f}%"))
            for pct in [5, 10, 20, 30]:
                _q.put(("put", f"  {'Loss > ' + str(pct) + '%':<30} {(finals<S0*(1-pct/100)).mean()*100:.1f}%"))

            # === MULTI-SCENARIO COMPARISON ===
            _q.put(("put", f"\n  SCENARIO ANALYSIS (3 vol regimes)"))
            _q.put(("put", f"  {'─'*60}"))
            _q.put(("put", f"  {'Scenario':<16} {'Vol':>6} {'Median':>10} {'Change':>8} {'P(up)':>7} {'VaR95':>8}"))
            _q.put(("put", f"  {'─'*60}"))
            n_sc = min(n, 250000)  # fewer sims for scenarios to stay fast
            for sc_name, sc_vol in [("Low Vol", vol_low), ("Current", vol_30d), ("High Vol", vol_high)]:
                sc_sig = sc_vol / 100.0 / np.sqrt(252)
                sc_jc = jump_lambda * (np.exp(jump_mu + 0.5 * jump_sigma**2) - 1)
                sc_drift = mu_daily - 0.5 * sc_sig**2 - sc_jc
                sc_Z = rng.standard_normal((n_sc, h))
                sc_j = rng.poisson(jump_lambda, (n_sc, h)) * (jump_mu + jump_sigma * rng.standard_normal((n_sc, h)))
                sc_paths = S0 * np.exp(np.cumsum(sc_drift + sc_sig * sc_Z + sc_j, axis=1))
                sc_finals = sc_paths[:, -1]
                sc_med = float(np.median(sc_finals))
                sc_chg = (sc_med - S0) / S0 * 100
                sc_pup = (sc_finals > S0).mean() * 100
                sc_var = float(np.percentile((sc_finals - S0) / S0 * 100, 5))
                _q.put(("put", f"  {sc_name:<16} {sc_vol:>5.1f}% ${sc_med:>9.2f} {sc_chg:>+7.1f}% {sc_pup:>6.1f}% {sc_var:>+7.1f}%"))

            # === RECOMMENDATION ===
            prob_up = (finals > S0).mean() * 100
            _q.put(("put", f"\n  {'='*64}"))
            _q.put(("put", f"  RECOMMENDATION (drift={drift_choice})"))
            _q.put(("put", f"  {'='*64}"))
            if prob_up > 58 and med_sharpe > 0.2 and median_dd > -15:
                _q.put(("put", f"  BULLISH — {prob_up:.0f}% upside, Sharpe {med_sharpe:.2f}"))
            elif prob_up < 42 or median_dd < -20:
                _q.put(("put", f"  BEARISH — only {prob_up:.0f}% upside, drawdown risk {median_dd:.0f}%"))
            else:
                _q.put(("put", f"  NEUTRAL — {prob_up:.0f}% upside, balanced risk"))
            _q.put(("put", f"  Median target: ${np.median(finals):.2f} ({(np.median(finals)-S0)/S0*100:+.1f}%)"))
            _q.put(("put", f"\n  NOTE: This is a RANGE GENERATOR, not a forecast."))
            _q.put(("put", f"  Drift choice matters most — 'risk-free' or 'neutral' gives honest projections."))
            _q.put(("put", f"  Jump diffusion models crash/rally shocks that basic GBM misses."))

            _q.put(("status", f"MC: {t} median ${np.median(finals):.2f} ({h}d, {n:,} sims, {drift_choice})"))
        bg_run(out, app.status, f"Monte Carlo: {t}", work, btn)

    btn.configure(command=_run)
    btn.pack(side="left", padx=6)
    ctk.CTkLabel(card, text="  Ticker | Sims | Days | Drift mode  •  Jump diffusion + volatility regime scenarios",
                  font=(FONT, 11), text_color=C["text3"]).pack(anchor="w", padx=16, pady=(4,10))
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
                elif cmd == "btn_reset" and data:
                    try: data.configure(state="normal", text=data._orig_text)
                    except Exception: pass
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
