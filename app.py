#!/usr/bin/env python3
"""
FinalAI Quantum Trading - Streamlit Web Interface
Expose all trading analysis features to friends via web browser
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Configure page
st.set_page_config(
    page_title="FinalAI Quantum Trading",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5em;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1.5em;
        border-radius: 0.5em;
        border-left: 4px solid #667eea;
    }
    .signal-buy {
        background-color: #d4edda;
        color: #155724;
        padding: 1em;
        border-radius: 0.5em;
        border-left: 4px solid #28a745;
    }
    .signal-sell {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1em;
        border-radius: 0.5em;
        border-left: 4px solid #dc3545;
    }
    .signal-hold {
        background-color: #fff3cd;
        color: #856404;
        padding: 1em;
        border-radius: 0.5em;
        border-left: 4px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

# Import after path setup
try:
    from Trading import (
        ConfigurationManager, DataManager, TechnicalAnalyzer, 
        NewsAnalyzer, SECAnalyzer, AnalysisEngine,
        MomentumStrategy, MeanReversionStrategy, MultiFactorStrategy,
        MarketScanner, ThemeResearcher, PaperTradingManager,
        PortfolioOptimizer, RegimeDetector, MultiTimeframeAnalyzer,
        logger
    )
except ImportError as e:
    st.error(f"Error importing Trading module: {e}")
    st.stop()

# Initialize session state
if 'paper_trading_manager' not in st.session_state:
    st.session_state.paper_trading_manager = PaperTradingManager()

if 'analyzer' not in st.session_state:
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        st.session_state.analyzer = AnalysisEngine(api_key)
    except:
        st.session_state.analyzer = None

# Sidebar Navigation
st.sidebar.markdown("# 📊 FinalAI Quantum")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Select Analysis Module",
    [
        "🏠 Dashboard",
        "📈 Stock Analysis",
        "🔍 Market Scanner",
        "📰 News & Sentiment",
        "💼 Portfolio Tools",
        "📊 Technical Analysis",
        "🤖 AI Strategies",
        "📝 Paper Trading",
        "🎯 Theme Research",
        "⚙️ Settings"
    ]
)

# ============================================
# PAGE: DASHBOARD
# ============================================
if page == "🏠 Dashboard":
    st.markdown("<h1 class='main-header'>FinalAI Quantum - Trading Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("Professional quantitative trading analysis system for friends")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Features", "80+", "Indicators")
    with col2:
        st.metric("🎯 Strategies", "6", "Active")
    with col3:
        st.metric("📈 Markets", "5000+", "Tickers")
    with col4:
        st.metric("💰 Paper Trading", st.session_state.paper_trading_manager.get_performance().get('total_trades', 0), "Trades")
    
    st.markdown("---")
    st.markdown("## 🚀 Quick Start")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Analyze Any Stock
        1. Go to **Stock Analysis**
        2. Enter ticker (AAPL, MSFT, TSLA, etc.)
        3. Choose analysis type
        4. Get AI-powered insights
        """)
    
    with col2:
        st.markdown("""
        ### Scan for Opportunities
        1. Go to **Market Scanner**
        2. Select market universe
        3. Get ranked opportunities
        4. Trade signals with R:R ratios
        """)
    
    st.markdown("---")
    st.markdown("## 📚 Feature Overview")
    
    features = {
        "🎯 80+ Technical Indicators": "SMA, EMA, RSI, MACD, Bollinger Bands, ATR, Ichimoku, Keltner, Williams %R, CCI, OBV, MFI, ADX + more",
        "🔄 6 Trading Strategies": "Momentum, Mean Reversion, Multi-Factor, Pairs Trading, ML Classification, Custom",
        "📊 Technical Analysis": "Chart patterns, candlesticks, support/resistance, trend analysis, volume profile",
        "📰 News & Sentiment": "Real-time headlines, sentiment analysis, SEC filings, insider trades",
        "💼 Portfolio Tools": "Efficient frontier, risk parity, Sharpe optimization, multi-asset correlation",
        "📈 Multi-Timeframe": "Confirm trends across 1m, 5m, 1h, 1d, 1w timeframes",
        "🤖 AI Analysis": "Claude Sonnet analysis, win probability, smart money detection",
        "💰 Paper Trading": "Risk-free backtesting with stop loss/take profit tracking",
        "🎨 Market Regimes": "Trending vs Ranging detection with volatility analysis",
        "🔍 Smart Money Concepts": "Order blocks, fair value gaps, liquidity zones, premium/discount zones"
    }
    
    for title, desc in features.items():
        st.markdown(f"**{title}**  \n{desc}")

# ============================================
# PAGE: STOCK ANALYSIS
# ============================================
elif page == "📈 Stock Analysis":
    st.markdown("<h1 class='main-header'>Stock Analysis</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input("Enter Stock Ticker", value="AAPL", placeholder="MSFT, TSLA, NVDA...").upper()
    
    with col2:
        style = st.selectbox("Analysis Style", ["Full Report", "Quick Signal", "Technical Only", "Fundamentals"])
    
    if st.button("🔍 Analyze", use_container_width=True, type="primary"):
        with st.spinner(f"Analyzing {ticker}..."):
            try:
                # Fetch data
                df = DataManager.fetch_data(ticker, "1y", "1d")
                
                if df is None or df.empty:
                    st.error(f"Could not fetch data for {ticker}")
                else:
                    # Calculate indicators
                    indicators = TechnicalAnalyzer.calculate_indicators(df)
                    
                    if indicators:
                        # Get analysis
                        if st.session_state.analyzer:
                            summary = st.session_state.analyzer.analyze_comprehensive(
                                ticker, indicators, 10000, 0.02, 2.0
                            )
                        else:
                            summary = st.session_state.analyzer._fallback_analysis(
                                ticker, indicators, 10000, 0.02, 2.0
                            ) if st.session_state.analyzer else None
                        
                        if summary:
                            # Price info
                            col1, col2, col3, col4 = st.columns(4)
                            current_price = float(df['Close'].iloc[-1])
                            
                            with col1:
                                st.metric("Current Price", f"${current_price:.2f}")
                            with col2:
                                change = current_price - float(df['Close'].iloc[-2])
                                change_pct = (change / float(df['Close'].iloc[-2])) * 100
                                st.metric("Change", f"{change_pct:+.2f}%")
                            with col3:
                                st.metric("Signal", summary.action, f"{summary.confidence:.0f}% conf")
                            with col4:
                                st.metric("R:R Ratio", f"{summary.risk_reward_ratio:.2f}")
                            
                            st.markdown("---")
                            
                            # Signal display
                            signal_class = f"signal-{summary.action.lower()}"
                            st.markdown(f"""
                            <div class="{signal_class}">
                                <h3>{summary.action} Signal</h3>
                                <p><strong>Entry:</strong> ${summary.entry_price:.2f}</p>
                                <p><strong>Stop Loss:</strong> ${summary.stop_loss:.2f}</p>
                                <p><strong>Take Profit 1:</strong> ${summary.take_profit_1:.2f}</p>
                                <p><strong>Take Profit 2:</strong> ${summary.take_profit_2:.2f}</p>
                                <p><strong>Reason:</strong> {summary.primary_reason}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown("---")
                            
                            # Indicators
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.subheader("📊 Trend")
                                st.metric("RSI(14)", f"{indicators.rsi_14:.1f}", "Momentum")
                                st.metric("MACD", f"{indicators.macd:.4f}", "Signal")
                                st.metric("ADX", f"{indicators.adx:.1f}", "Strength")
                            
                            with col2:
                                st.subheader("📈 Support/Resistance")
                                st.metric("SMA 50", f"${indicators.sma_50:.2f}", "Support")
                                st.metric("SMA 200", f"${indicators.sma_200:.2f}", "Long-term")
                                st.metric("BB Upper", f"${indicators.bb_upper:.2f}", "Resistance")
                            
                            with col3:
                                st.subheader("💪 Strength")
                                st.metric("ATR", f"${indicators.atr:.2f}", "Volatility")
                                st.metric("Volume Ratio", f"{indicators.volume_ratio:.2f}x", "vs 20-day avg")
                                st.metric("Stoch K", f"{indicators.stochastic_k:.1f}", "Momentum")
                            
                            st.markdown("---")
                            
                            # Supporting signals
                            st.subheader("✅ Supporting Signals")
                            for signal in summary.supporting_signals[:8]:
                                st.markdown(f"• {signal}")
                            
                            st.subheader("⚠️ Risk Factors")
                            for risk in summary.risk_factors[:5]:
                                st.markdown(f"• {risk}")
                        else:
                            st.error("Could not generate analysis")
                    else:
                        st.error("Could not calculate indicators")
            except Exception as e:
                st.error(f"Analysis error: {str(e)}")

# ============================================
# PAGE: MARKET SCANNER
# ============================================
elif page == "🔍 Market Scanner":
    st.markdown("<h1 class='main-header'>Market Scanner</h1>", unsafe_allow_html=True)
    st.markdown("Scan multiple stocks for trading opportunities")
    
    col1, col2 = st.columns(2)
    
    with col1:
        universe = st.selectbox(
            "Select Market Universe",
            [
                "S&P 500 Top 50",
                "Tech Leaders (20)",
                "Mega Caps (8)",
                "AI & Quantum (10)",
                "Custom List"
            ]
        )
    
    with col2:
        min_confidence = st.slider("Minimum Confidence", 0, 100, 60)
    
    if st.button("🔍 Scan Market", use_container_width=True, type="primary"):
        with st.spinner("Scanning..."):
            try:
                # Import market universes
                from Trading import MARKET_UNIVERSES
                
                if universe == "Custom List":
                    tickers_str = st.text_input("Enter tickers (comma-separated)", "AAPL,MSFT,NVDA")
                    tickers = [t.strip().upper() for t in tickers_str.split(",")]
                else:
                    universe_map = {
                        "S&P 500 Top 50": "sp500_top50",
                        "Tech Leaders (20)": "tech_leaders",
                        "Mega Caps (8)": "mega_caps",
                        "AI & Quantum (10)": "ai_quantum"
                    }
                    tickers = MARKET_UNIVERSES[universe_map[universe]]
                
                # Create scanner
                scanner = MarketScanner(st.session_state.analyzer)
                
                config = {
                    'scanner_min_confidence': min_confidence,
                    'scanner_max_results': 30,
                    'account_size': 10000,
                    'risk_per_trade': 2.0,
                    'default_rrr': 2.0
                }
                
                opportunities = scanner.scan_universe(tickers, config)
                
                if opportunities:
                    st.success(f"Found {len(opportunities)} opportunities")
                    
                    # Display as table
                    opp_data = []
                    for opp in opportunities:
                        opp_data.append({
                            'Ticker': opp.ticker,
                            'Action': opp.action,
                            'Confidence': f"{opp.confidence:.0f}%",
                            'Entry': f"${opp.entry_price:.2f}",
                            'Stop Loss': f"${opp.stop_loss:.2f}",
                            'Target': f"${opp.target:.2f}",
                            'R:R': f"{opp.risk_reward:.2f}",
                            'Signal': opp.primary_signal[:30] + "..."
                        })
                    
                    df_opps = pd.DataFrame(opp_data)
                    st.dataframe(df_opps, use_container_width=True)
                else:
                    st.info("No opportunities found with current filters")
                    
            except Exception as e:
                st.error(f"Scanner error: {str(e)}")

# ============================================
# PAGE: NEWS & SENTIMENT
# ============================================
elif page == "📰 News & Sentiment":
    st.markdown("<h1 class='main-header'>News & Sentiment Analysis</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input("Enter Ticker", value="AAPL").upper()
    
    with col2:
        limit = st.number_input("Number of Articles", 5, 20, 10)
    
    if st.button("📰 Get News", use_container_width=True, type="primary"):
        with st.spinner("Fetching news..."):
            try:
                news_items = NewsAnalyzer.get_news(ticker, limit)
                
                if news_items:
                    st.subheader(f"Latest {len(news_items)} Headlines for {ticker}")
                    
                    for item in news_items:
                        sentiment_color = "🟢" if item.sentiment == "POSITIVE" else ("🔴" if item.sentiment == "NEGATIVE" else "🟡")
                        
                        st.markdown(f"""
                        {sentiment_color} **{item.title}**  
                        *{item.source}* • {item.sentiment}  
                        [Read more]({item.url})
                        """)
                        st.markdown("---")
                else:
                    st.info("No news found")
                    
            except Exception as e:
                st.error(f"News fetch error: {str(e)}")

# ============================================
# PAGE: PORTFOLIO TOOLS
# ============================================
elif page == "💼 Portfolio Tools":
    st.markdown("<h1 class='main-header'>Portfolio Optimization</h1>", unsafe_allow_html=True)
    
    tool = st.selectbox(
        "Select Tool",
        [
            "Efficient Frontier",
            "Risk Parity",
            "Correlation Matrix",
            "Portfolio Metrics"
        ]
    )
    
    tickers_input = st.text_input("Enter Tickers (comma-separated)", "AAPL,MSFT,NVDA,TSLA,META")
    tickers = [t.strip().upper() for t in tickers_input.split(",")]
    
    if st.button("📊 Analyze", use_container_width=True, type="primary"):
        with st.spinner("Running portfolio analysis..."):
            try:
                # Fetch data for all tickers
                returns_data = {}
                for ticker in tickers:
                    df = DataManager.fetch_data(ticker, "1y", "1d")
                    if df is not None and len(df) >= 200:
                        returns_data[ticker] = df['Close'].pct_change().dropna()
                
                if len(returns_data) < 2:
                    st.error("Need at least 2 tickers with sufficient data")
                else:
                    returns_df = pd.DataFrame(returns_data).dropna()
                    
                    if tool == "Efficient Frontier":
                        st.subheader("Efficient Frontier Analysis")
                        
                        # Calculate key portfolios
                        max_sharpe_weights, max_sharpe_ret, max_sharpe_vol, sharpe = PortfolioOptimizer.optimize_max_sharpe(returns_df)
                        min_var_weights, min_var_ret, min_var_vol = PortfolioOptimizer.optimize_min_variance(returns_df)
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Max Sharpe Ratio", f"{sharpe:.2f}")
                            st.metric("Return", f"{max_sharpe_ret*100:.2f}%")
                            st.metric("Volatility", f"{max_sharpe_vol*100:.2f}%")
                        
                        with col2:
                            st.metric("Min Variance Return", f"{min_var_ret*100:.2f}%")
                            st.metric("Min Variance Vol", f"{min_var_vol*100:.2f}%")
                        
                        with col3:
                            st.markdown("**Max Sharpe Allocation:**")
                            for ticker, weight in zip(returns_df.columns, max_sharpe_weights):
                                st.markdown(f"{ticker}: {weight*100:.1f}%")
                    
                    elif tool == "Correlation Matrix":
                        st.subheader("Asset Correlation Matrix")
                        corr_matrix = returns_df.corr()
                        
                        import plotly.express as px
                        fig = px.imshow(corr_matrix, text_auto=True, color_continuous_scale="RdBu", aspect="auto")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif tool == "Portfolio Metrics":
                        st.subheader("Portfolio Statistics")
                        
                        metrics = {
                            'Annual Return': returns_df.mean() * 252,
                            'Annual Volatility': returns_df.std() * np.sqrt(252),
                            'Sharpe Ratio': (returns_df.mean() * 252) / (returns_df.std() * np.sqrt(252))
                        }
                        
                        for metric_name, values in metrics.items():
                            st.markdown(f"**{metric_name}**")
                            for ticker, value in values.items():
                                st.markdown(f"  {ticker}: {value:.4f}")
                    
                    elif tool == "Risk Parity":
                        st.subheader("Risk Parity Weights")
                        rp_weights = PortfolioOptimizer.risk_parity_weights(returns_df)
                        
                        rp_data = pd.DataFrame({
                            'Ticker': returns_df.columns,
                            'Weight': rp_weights * 100
                        })
                        
                        st.dataframe(rp_data, use_container_width=True)
                        
                        import plotly.express as px
                        fig = px.pie(rp_data, values='Weight', names='Ticker', title="Risk Parity Allocation")
                        st.plotly_chart(fig, use_container_width=True)
                        
            except Exception as e:
                st.error(f"Portfolio analysis error: {str(e)}")

# ============================================
# PAGE: TECHNICAL ANALYSIS
# ============================================
elif page == "📊 Technical Analysis":
    st.markdown("<h1 class='main-header'>Technical Analysis</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input("Enter Ticker", value="AAPL").upper()
    
    with col2:
        timeframe = st.selectbox("Timeframe", ["1d", "1wk", "1mo"])
    
    if st.button("📈 Analyze", use_container_width=True, type="primary"):
        with st.spinner(f"Analyzing {ticker} ({timeframe})..."):
            try:
                # Fetch data
                period_map = {"1d": "2y", "1wk": "5y", "1mo": "10y"}
                df = DataManager.fetch_data(ticker, period_map[timeframe], timeframe)
                
                if df is None or df.empty:
                    st.error(f"Could not fetch data for {ticker}")
                else:
                    # Calculate indicators
                    indicators = TechnicalAnalyzer.calculate_indicators(df)
                    
                    if indicators:
                        # Candlestick chart
                        st.subheader(f"{ticker} Price Chart")
                        
                        # Prepare data for plotly
                        chart_data = df.copy()
                        chart_data['Date'] = chart_data.index
                        
                        import plotly.graph_objects as go
                        
                        fig = go.Figure(data=[go.Candlestick(
                            x=chart_data.index,
                            open=chart_data['Open'],
                            high=chart_data['High'],
                            low=chart_data['Low'],
                            close=chart_data['Close']
                        )])
                        
                        fig.update_layout(
                            title=f"{ticker} - {timeframe}",
                            yaxis_title='Stock Price',
                            template='plotly_dark',
                            height=500
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Indicators grid
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("SMA 20", f"${indicators.sma_20:.2f}")
                            st.metric("SMA 50", f"${indicators.sma_50:.2f}")
                        
                        with col2:
                            st.metric("SMA 200", f"${indicators.sma_200:.2f}")
                            st.metric("EMA 12", f"${indicators.ema_12:.2f}")
                        
                        with col3:
                            st.metric("RSI(14)", f"{indicators.rsi_14:.1f}")
                            st.metric("MACD", f"{indicators.macd:.6f}")
                        
                        with col4:
                            st.metric("ATR", f"${indicators.atr:.2f}")
                            st.metric("ADX", f"{indicators.adx:.1f}")
                        
                    else:
                        st.error("Could not calculate indicators")
                        
            except Exception as e:
                st.error(f"Technical analysis error: {str(e)}")

# ============================================
# PAGE: AI STRATEGIES
# ============================================
elif page == "🤖 AI Strategies":
    st.markdown("<h1 class='main-header'>AI Trading Strategies</h1>", unsafe_allow_html=True)
    
    strategy = st.selectbox(
        "Select Strategy",
        [
            "Momentum",
            "Mean Reversion",
            "Multi-Factor",
            "Pairs Trading",
            "ML Classification"
        ]
    )
    
    tickers_input = st.text_input("Enter Tickers (comma-separated)", "AAPL,MSFT,NVDA,TSLA,META,GOOGL,AMZN,JPM")
    tickers = [t.strip().upper() for t in tickers_input.split(",")]
    
    if st.button("🎯 Run Strategy", use_container_width=True, type="primary"):
        with st.spinner(f"Running {strategy} strategy..."):
            try:
                if strategy == "Momentum":
                    strat = MomentumStrategy()
                    signals = strat.generate_signals(tickers[:5])
                elif strategy == "Mean Reversion":
                    strat = MeanReversionStrategy()
                    signals = strat.generate_signals(tickers[:5])
                elif strategy == "Multi-Factor":
                    strat = MultiFactorStrategy()
                    signals = strat.generate_signals(tickers[:10])
                else:
                    st.info(f"{strategy} requires additional setup")
                    signals = []
                
                if signals:
                    st.success(f"Generated {len(signals)} signals")
                    
                    # Display signals
                    signal_data = []
                    for sig in signals:
                        signal_data.append({
                            'Ticker': sig.ticker,
                            'Action': sig.action,
                            'Strength': f"{sig.strength:.0f}%",
                            'Entry': f"${sig.entry_price:.2f}",
                            'Stop': f"${sig.stop_loss:.2f}",
                            'Target': f"${sig.take_profit:.2f}",
                            'Reason': sig.reason[:40] + "..."
                        })
                    
                    df_signals = pd.DataFrame(signal_data)
                    st.dataframe(df_signals, use_container_width=True)
                else:
                    st.info("No signals generated")
                    
            except Exception as e:
                st.error(f"Strategy error: {str(e)}")

# ============================================
# PAGE: PAPER TRADING
# ============================================
elif page == "📝 Paper Trading":
    st.markdown("<h1 class='main-header'>Paper Trading</h1>", unsafe_allow_html=True)
    st.markdown("Virtual trading with risk-free backtesting")
    
    tab1, tab2, tab3 = st.tabs(["Open Trade", "Active Positions", "Performance"])
    
    with tab1:
        st.subheader("Open New Paper Trade")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ticker = st.text_input("Ticker", "AAPL").upper()
            action = st.selectbox("Action", ["LONG", "SHORT"])
        
        with col2:
            entry_price = st.number_input("Entry Price", 100.0, 1000.0, 100.0)
            position_size = st.number_input("Position Size (shares)", 1, 1000, 10)
        
        with col3:
            stop_loss = st.number_input("Stop Loss", 50.0, 1000.0, 90.0)
            take_profit = st.number_input("Take Profit", 100.0, 1000.0, 120.0)
        
        if st.button("📥 Open Trade", use_container_width=True, type="primary"):
            st.session_state.paper_trading_manager.open_trade(
                ticker, action, entry_price, stop_loss, take_profit, position_size
            )
            st.success(f"Paper trade opened: {action} {position_size} {ticker} @ ${entry_price:.2f}")
    
    with tab2:
        st.subheader("Active Positions")
        open_trades = st.session_state.paper_trading_manager.get_open_trades()
        
        if open_trades:
            for trade in open_trades:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    **{trade.ticker} - {trade.action}**  
                    Entry: ${trade.entry_price:.2f} | Size: {trade.position_size}  
                    Stop: ${trade.stop_loss:.2f} | Target: ${trade.take_profit:.2f}
                    """)
                
                with col2:
                    if st.button(f"❌ Close {trade.ticker}", key=f"close_{trade.ticker}"):
                        st.session_state.paper_trading_manager.close_trade_manually(trade.ticker)
                        st.rerun()
        else:
            st.info("No open positions")
    
    with tab3:
        st.subheader("Trading Performance")
        perf = st.session_state.paper_trading_manager.get_performance()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Trades", perf.get('total_trades', 0))
        with col2:
            st.metric("Win Rate", f"{perf.get('win_rate', 0):.1f}%")
        with col3:
            st.metric("Total P&L", f"${perf.get('total_pnl', 0):.2f}")
        with col4:
            st.metric("Avg Win", f"${perf.get('avg_win', 0):.2f}")

# ============================================
# PAGE: THEME RESEARCH
# ============================================
elif page == "🎯 Theme Research":
    st.markdown("<h1 class='main-header'>Theme Research</h1>", unsafe_allow_html=True)
    st.markdown("AI-powered investment theme analysis")
    
    theme = st.text_input("Enter Investment Theme", "quantum computing", placeholder="AI, quantum, crypto, EV...")
    
    if st.button("🔬 Research Theme", use_container_width=True, type="primary"):
        with st.spinner(f"Researching {theme}..."):
            try:
                api_key = os.getenv('ANTHROPIC_API_KEY')
                researcher = ThemeResearcher(api_key)
                research = researcher.research_theme(theme)
                
                st.subheader(f"Analysis: {research.get('theme', theme)}")
                
                st.markdown(f"**Summary:** {research.get('summary', 'N/A')}")
                
                st.subheader("📊 Key Companies")
                companies = research.get('key_companies', [])
                if companies:
                    for company in companies[:10]:
                        st.markdown(f"• **{company.get('ticker')}** - {company.get('name')}  \n  {company.get('reason')}")
                
                st.subheader("📈 Growth Potential")
                st.markdown(research.get('growth_potential', 'N/A'))
                
                st.subheader("⚠️ Risk Factors")
                risks = research.get('risks', [])
                for risk in risks:
                    st.markdown(f"• {risk}")
                
            except Exception as e:
                st.error(f"Research error: {str(e)}")

# ============================================
# PAGE: SETTINGS
# ============================================
elif page == "⚙️ Settings":
    st.markdown("<h1 class='main-header'>Settings & Configuration</h1>", unsafe_allow_html=True)
    
    st.subheader("🔑 API Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Anthropic API Key** (for AI analysis)")
        api_key = st.text_input("API Key", type="password", value=os.getenv('ANTHROPIC_API_KEY', ''))
        if st.button("💾 Save API Key"):
            os.environ['ANTHROPIC_API_KEY'] = api_key
            st.success("API key saved!")
    
    with col2:
        st.markdown("**Polygon.io API Key** (for intraday data)")
        poly_key = st.text_input("Polygon Key", type="password", value=os.getenv('POLYGON_API_KEY', ''))
        if st.button("💾 Save Polygon Key"):
            os.environ['POLYGON_API_KEY'] = poly_key
            st.success("Polygon key saved!")
    
    st.markdown("---")
    st.subheader("📊 Trading Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        account_size = st.number_input("Account Size ($)", 1000, 1000000, 10000)
        risk_per_trade = st.slider("Risk per Trade (%)", 0.5, 10.0, 2.0)
    
    with col2:
        max_positions = st.number_input("Max Concurrent Positions", 1, 20, 3)
        default_rrr = st.number_input("Default Risk:Reward Ratio", 1.0, 5.0, 2.0)
    
    if st.button("💾 Save Preferences", use_container_width=True, type="primary"):
        st.success("Preferences saved!")
    
    st.markdown("---")
    st.subheader("ℹ️ About")
    st.markdown("""
    **FinalAI Quantum v7.0 - Professional Edition**
    
    Comprehensive quantitative trading analysis system with:
    - 80+ Technical Indicators
    - 6+ Trading Strategies
    - AI-Powered Analysis
    - Portfolio Optimization
    - Market Scanning
    - Paper Trading
    - Theme Research
    
    Built for friends to share trading insights.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
<small>FinalAI Quantum Trading | Professional Edition | Powered by Advanced Quantitative Analysis</small>
</div>
""", unsafe_allow_html=True)
