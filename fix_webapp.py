#!/usr/bin/env python3
"""Fix web_app.py - Add candlestick charts to Analyze Stock page"""

with open(r'c:\Users\aravn\web_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the Analyze Stock section
start_marker = '    elif page == "�📊 Analyze Stock":'
end_marker = '    elif page == "📰 News & Intel":'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("❌ Could not find markers")
    exit(1)

new_section = '''    elif page == "�📊 Analyze Stock":
        st.title("📊 Stock Analysis")
        
        ticker = st.text_input("Enter Ticker Symbol:", "AAPL").upper()
        
        if st.button("Analyze"):
            with st.spinner(f"Analyzing {ticker}..."):
                try:
                    import plotly.graph_objects as go
                    from plotly.subplots import make_subplots
                    
                    df = DataManager.fetch_data(ticker, period='3mo', interval='1d')
                    if df is not None and len(df) > 0:
                        st.success(f"✓ Data loaded for {ticker}")
                        
                        analyzer = TechnicalAnalyzer()
                        
                        # RSI
                        delta = df['Close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / loss
                        rsi = 100 - (100 / (1 + rs))
                        
                        # MACD
                        ema12 = df['Close'].ewm(span=12).mean()
                        ema26 = df['Close'].ewm(span=26).mean()
                        macd = ema12 - ema26
                        signal = macd.ewm(span=9).mean()
                        
                        # Moving Averages
                        ma20 = df['Close'].rolling(window=20).mean()
                        ma50 = df['Close'].rolling(window=50).mean()
                        
                        # Create candlestick chart
                        fig = make_subplots(
                            rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                            row_heights=[0.5, 0.25, 0.25],
                            subplot_titles=(f'{ticker} Price', 'RSI (14)', 'MACD')
                        )
                        
                        fig.add_trace(go.Candlestick(
                            x=df.index, open=df['Open'], high=df['High'],
                            low=df['Low'], close=df['Close'], name='Price'
                        ), row=1, col=1)
                        
                        fig.add_trace(go.Scatter(x=df.index, y=ma20, name='MA20',
                            line=dict(color='orange', width=1)), row=1, col=1)
                        fig.add_trace(go.Scatter(x=df.index, y=ma50, name='MA50',
                            line=dict(color='blue', width=1)), row=1, col=1)
                        
                        fig.add_trace(go.Scatter(x=df.index, y=rsi, name='RSI',
                            line=dict(color='purple', width=1)), row=2, col=1)
                        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
                        
                        fig.add_trace(go.Scatter(x=df.index, y=macd, name='MACD',
                            line=dict(color='blue', width=1)), row=3, col=1)
                        fig.add_trace(go.Scatter(x=df.index, y=signal, name='Signal',
                            line=dict(color='orange', width=1)), row=3, col=1)
                        
                        fig.update_layout(height=800, showlegend=True,
                            xaxis_rangeslider_visible=False, hovermode='x unified',
                            template='plotly_dark', dragmode=False)
                        fig.update_xaxes(showgrid=True, gridcolor='#333', fixedrange=True)
                        fig.update_yaxes(showgrid=True, gridcolor='#333', fixedrange=True)
                        
                        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})
                        
                        # Generate signals
                        current_rsi = rsi.iloc[-1]
                        current_macd = macd.iloc[-1]
                        current_signal = signal.iloc[-1]
                        current_price = df['Close'].iloc[-1]
                        current_ma20 = ma20.iloc[-1]
                        current_ma50 = ma50.iloc[-1]
                        
                        signals = []
                        confidence = 0
                        
                        if current_rsi < 30:
                            signals.append("🟢 RSI Oversold (Bullish)")
                            confidence += 30
                        elif current_rsi > 70:
                            signals.append("🔴 RSI Overbought (Bearish)")
                            confidence -= 30
                        
                        if current_macd > current_signal:
                            signals.append("🟢 MACD Bullish Crossover")
                            confidence += 25
                        else:
                            signals.append("🔴 MACD Bearish")
                            confidence -= 25
                        
                        if current_price > current_ma20 > current_ma50:
                            signals.append("🟢 Price Above MA20 & MA50")
                            confidence += 25
                        elif current_price < current_ma20 < current_ma50:
                            signals.append("🔴 Price Below MA20 & MA50")
                            confidence -= 25
                        
                        if confidence >= 50:
                            rec = "🟢 STRONG BUY"
                        elif confidence >= 20:
                            rec = "🟢 BUY"
                        elif confidence >= -20:
                            rec = "🟡 HOLD"
                        elif confidence >= -50:
                            rec = "🔴 SELL"
                        else:
                            rec = "🔴 STRONG SELL"
                        
                        st.subheader("Technical Analysis Summary")
                        col1, col2, col3, col4 = st.columns(4)
                        change = ((df['Close'].iloc[-1] / df['Close'].iloc[-2]) - 1) * 100
                        col1.metric("Price", f"${current_price:.2f}", f"{change:+.2f}%")
                        col2.metric("RSI", f"{current_rsi:.1f}")
                        col3.metric("Recommendation", rec)
                        col4.metric("Confidence", f"{abs(confidence)}%")
                        
                        st.subheader("Trading Signals")
                        for sig in signals:
                            st.write(sig)
                        
                        col1, col2 = st.columns(2)
                        col1.metric("Support", f"${df['Low'].tail(20).min():.2f}")
                        col2.metric("Resistance", f"${df['High'].tail(20).max():.2f}")
                    else:
                        st.error(f"Could not load data for {ticker}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
    
'''

# Replace the section
new_content = content[:start_idx] + new_section + content[end_idx:]

# Write back
with open(r'c:\Users\aravn\web_app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Updated web_app.py with candlestick charts and technical indicators!")
print("📊 Features added:")
print("  - Candlestick chart with MA20/MA50")
print("  - RSI indicator with overbought/oversold zones")
print("  - MACD with signal line")
print("  - Buy/Sell/Hold recommendations")
print("  - Confidence scoring")
print("  - Support/Resistance levels")
print("  - Static plot (no unwanted interactivity)")
