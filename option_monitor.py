#!/usr/bin/env python3
"""
Options Position Monitor - Real-Time Alerts for Buy/Sell Decisions
Monitors your option positions and sends Telegram alerts when you should:
- Buy more contracts (favorable price/Greeks movement)
- Sell/close contracts (take profit, stop loss, Greeks deterioration)
- Roll positions (approaching expiration with favorable conditions)
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import yfinance as yf
import numpy as np
from scipy.stats import norm
import requests

# Black-Scholes Greeks calculator
def black_scholes_greeks(S, K, T, r, sigma, option_type='call'):
    """Calculate option Greeks using Black-Scholes model."""
    if T <= 0 or sigma <= 0:
        return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'price': 0}
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type.lower() == 'call':
        delta = norm.cdf(d1)
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:  # put
        delta = norm.cdf(d1) - 1
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    
    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100  # per 1% change in IV
    theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) - 
             r * K * np.exp(-r * T) * (norm.cdf(d2) if option_type.lower() == 'call' else norm.cdf(-d2))) / 365
    
    return {
        'delta': delta,
        'gamma': gamma,
        'theta': theta,
        'vega': vega,
        'price': price
    }


class OptionsPositionMonitor:
    """Monitor option positions and send actionable Telegram alerts."""
    
    def __init__(self, positions_file: str = "results/options_positions.json"):
        self.positions_file = Path(positions_file)
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_ids = [c.strip() for c in os.getenv('TELEGRAM_CHAT_IDS', '').split(',') if c.strip()]
        self.risk_free_rate = 0.05  # 5% annual
        self.positions_cache = {}
        
    def load_positions(self) -> List[Dict[str, Any]]:
        """Load open option positions from JSON file."""
        if not self.positions_file.exists():
            return []
        try:
            with open(self.positions_file, 'r') as f:
                all_positions = json.load(f)
                return [p for p in all_positions if p.get('status') == 'OPEN']
        except Exception as e:
            print(f"Error loading positions: {e}")
            return []
    
    def get_current_price_and_iv(self, ticker: str) -> tuple:
        """Fetch current stock price and implied volatility."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            
            # Get historical volatility as IV proxy (30-day)
            hist = stock.history(period='1mo', interval='1d')
            if len(hist) > 5:
                returns = np.log(hist['Close'] / hist['Close'].shift(1)).dropna()
                iv = returns.std() * np.sqrt(252)  # Annualized
            else:
                iv = 0.30  # Default 30%
            
            return current_price, iv
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return 0, 0.30
    
    def parse_expiry(self, expiry_str: str) -> datetime:
        """Parse expiration date from various formats."""
        try:
            # Try YYYY-M-D first
            if '-' in expiry_str and len(expiry_str.split('-')) == 3:
                return datetime.strptime(expiry_str, '%Y-%m-%d')
            # Try M/D/YY format
            return datetime.strptime(expiry_str, '%m/%d/%y')
        except:
            # Default to 30 days out if parsing fails
            return datetime.now() + timedelta(days=30)
    
    def analyze_position(self, position: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single option position and determine action."""
        ticker = position['underlying']
        strike = float(position['strike'])
        option_type = position['type'].lower()
        contracts = int(position.get('contracts', 0))
        entry_premium = float(position['entry_premium'])
        stop_premium = float(position.get('stop_premium', entry_premium * 0.5))
        target_premium = float(position.get('target_premium', entry_premium * 2))
        
        if contracts == 0:
            return {'action': 'NONE', 'reason': 'No contracts held'}
        
        # Get current market data
        current_price, iv = self.get_current_price_and_iv(ticker)
        if current_price == 0:
            return {'action': 'ERROR', 'reason': f'Could not fetch price for {ticker}'}
        
        # Calculate time to expiration
        expiry = self.parse_expiry(position['expiration'])
        dte = (expiry - datetime.now()).days
        T = max(dte / 365.0, 0.01)  # Years, minimum 1 day
        
        # Calculate current Greeks
        greeks = black_scholes_greeks(current_price, strike, T, self.risk_free_rate, iv, option_type)
        current_premium = greeks['price']
        
        # Check cache for previous values
        cache_key = f"{ticker}_{strike}_{option_type}_{position['expiration']}"
        prev_data = self.positions_cache.get(cache_key, {})
        prev_premium = prev_data.get('premium', entry_premium)
        prev_delta = prev_data.get('delta', greeks['delta'])
        
        # Update cache
        self.positions_cache[cache_key] = {
            'premium': current_premium,
            'delta': greeks['delta'],
            'price': current_price,
            'iv': iv,
            'timestamp': datetime.now().isoformat()
        }
        
        # Calculate P&L
        pnl = (current_premium - entry_premium) * 100 * contracts
        pnl_pct = ((current_premium - entry_premium) / entry_premium * 100) if entry_premium > 0 else 0
        
        # Decision logic
        action = 'HOLD'
        confidence = 50
        reasons = []
        
        # Stop loss check
        if current_premium <= stop_premium:
            action = 'SELL'
            confidence = 95
            reasons.append(f"Stop loss hit (${current_premium:.2f} ≤ ${stop_premium:.2f})")
        
        # Take profit check
        elif current_premium >= target_premium:
            action = 'SELL'
            confidence = 90
            reasons.append(f"Target reached (${current_premium:.2f} ≥ ${target_premium:.2f})")
        
        # Approaching expiration
        elif dte <= 7:
            if pnl > 0:
                action = 'SELL'
                confidence = 85
                reasons.append(f"Approaching expiry ({dte}d) with profit")
            elif current_premium < entry_premium * 0.3:
                action = 'SELL'
                confidence = 80
                reasons.append(f"Near expiry ({dte}d), cut losses")
            else:
                action = 'ROLL' if dte <= 3 else 'HOLD'
                confidence = 70
                reasons.append(f"Consider rolling ({dte}d left)")
        
        # Delta deterioration (for directional trades)
        elif abs(greeks['delta']) < abs(prev_delta) * 0.5:
            action = 'SELL'
            confidence = 75
            reasons.append(f"Delta deteriorated ({greeks['delta']:.2f} vs {prev_delta:.2f})")
        
        # Gamma risk (high gamma near ATM can be volatile)
        elif abs(greeks['gamma']) > 0.05 and dte < 14:
            if pnl_pct > 20:
                action = 'SELL'
                confidence = 70
                reasons.append(f"High gamma risk, lock profit (Γ={greeks['gamma']:.3f})")
        
        # Theta decay acceleration (last 30 days)
        elif dte < 30 and pnl_pct < -15:
            action = 'SELL'
            confidence = 75
            reasons.append(f"Theta decay accelerating, cut loss (θ={greeks['theta']:.2f})")
        
        # Favorable move - add more
        elif pnl_pct > 50 and abs(greeks['delta']) > 0.6 and dte > 30:
            action = 'BUY'
            confidence = 70
            reasons.append(f"Strong profit (+{pnl_pct:.1f}%), high delta (Δ={greeks['delta']:.2f}), add contracts")
        
        # IV spike (sell premium)
        elif iv > 0.60 and option_type == 'call':
            action = 'SELL'
            confidence = 65
            reasons.append(f"High IV ({iv*100:.1f}%), sell premium")
        
        # Default hold with monitoring
        else:
            if pnl_pct > 10:
                reasons.append(f"Profit +{pnl_pct:.1f}%, monitor closely")
            elif pnl_pct < -10:
                reasons.append(f"Loss {pnl_pct:.1f}%, watch for exit")
        
        return {
            'action': action,
            'confidence': confidence,
            'reasons': reasons,
            'current_price': current_price,
            'current_premium': current_premium,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'greeks': greeks,
            'iv': iv,
            'dte': dte
        }
    
    def send_telegram_alert(self, message: str):
        """Send Telegram alert to configured chat IDs."""
        if not self.bot_token or not self.chat_ids:
            print(f"[Telegram disabled] {message}")
            return
        
        for chat_id in self.chat_ids:
            try:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True
                }
                resp = requests.post(url, json=payload, timeout=6)
                if resp.status_code == 200:
                    print(f"✓ Alert sent to {chat_id}")
                else:
                    print(f"✗ Failed to send to {chat_id}: HTTP {resp.status_code}")
            except Exception as e:
                print(f"✗ Telegram error for {chat_id}: {e}")
    
    def format_alert(self, position: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Format a position alert message."""
        action = analysis['action']
        if action == 'NONE' or action == 'ERROR':
            return None
        
        ticker = position['underlying']
        option_type = position['type'].upper()
        strike = position['strike']
        contracts = position['contracts']
        expiry = position['expiration']
        
        # Emoji indicators
        emoji_map = {'BUY': '🟢 BUY', 'SELL': '🔴 SELL', 'ROLL': '🔄 ROLL', 'HOLD': '🟡 HOLD'}
        action_emoji = emoji_map.get(action, action)
        
        pnl_emoji = '📈' if analysis['pnl'] > 0 else '📉'
        
        msg = f"<b>{action_emoji} SIGNAL</b> ({analysis['confidence']}% confidence)\n\n"
        msg += f"<b>{ticker} ${strike} {option_type}</b>\n"
        msg += f"Contracts: {contracts} | Exp: {expiry}\n"
        msg += f"DTE: {analysis['dte']} days\n\n"
        
        msg += f"<b>Current Status:</b>\n"
        msg += f"Stock: ${analysis['current_price']:.2f}\n"
        msg += f"Premium: ${analysis['current_premium']:.2f}\n"
        msg += f"P&L: ${analysis['pnl']:.2f} ({analysis['pnl_pct']:+.1f}%) {pnl_emoji}\n\n"
        
        msg += f"<b>Greeks:</b>\n"
        msg += f"Δ {analysis['greeks']['delta']:.3f} | "
        msg += f"Γ {analysis['greeks']['gamma']:.4f}\n"
        msg += f"Θ {analysis['greeks']['theta']:.2f} | "
        msg += f"ν {analysis['greeks']['vega']:.2f}\n"
        msg += f"IV: {analysis['iv']*100:.1f}%\n\n"
        
        msg += f"<b>Reasons:</b>\n"
        for r in analysis['reasons']:
            msg += f"• {r}\n"
        
        msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
        
        return msg
    
    def monitor_positions(self, alert_threshold: int = 70):
        """Monitor all positions and send alerts for actionable signals."""
        positions = self.load_positions()
        if not positions:
            print("No open positions to monitor.")
            return
        
        print(f"\n🔍 Monitoring {len(positions)} open option position(s)...\n")
        
        for pos in positions:
            try:
                analysis = self.analyze_position(pos)
                
                # Print summary
                ticker = pos['underlying']
                action = analysis.get('action', 'HOLD')
                confidence = analysis.get('confidence', 0)
                
                print(f"{ticker} ${pos['strike']} {pos['type']}: {action} ({confidence}%)")
                
                # Send alert if confidence meets threshold and action is not HOLD
                if confidence >= alert_threshold and action in ['BUY', 'SELL', 'ROLL']:
                    alert_msg = self.format_alert(pos, analysis)
                    if alert_msg:
                        self.send_telegram_alert(alert_msg)
                        print(f"  → Alert sent!")
                
            except Exception as e:
                print(f"Error analyzing {pos.get('underlying', 'unknown')}: {e}")
        
        print(f"\n✓ Scan complete at {datetime.now().strftime('%H:%M:%S')}\n")
    
    def run_continuous(self, scan_interval: int = 60, alert_threshold: int = 70):
        """Run continuous monitoring loop."""
        print(f"🚀 Starting continuous options monitor (scan every {scan_interval}s, alert threshold {alert_threshold}%)\n")
        print("Press Ctrl+C to stop.\n")
        
        try:
            while True:
                self.monitor_positions(alert_threshold=alert_threshold)
                time.sleep(scan_interval)
        except KeyboardInterrupt:
            print("\n\n⏹ Monitor stopped by user.")


if __name__ == "__main__":
    import sys
    
    monitor = OptionsPositionMonitor()
    
    # Check for command-line args
    if len(sys.argv) > 1 and sys.argv[1] == 'continuous':
        # Continuous mode: python option_monitor.py continuous [interval] [threshold]
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        threshold = int(sys.argv[3]) if len(sys.argv) > 3 else 70
        monitor.run_continuous(scan_interval=interval, alert_threshold=threshold)
    else:
        # One-time scan
        monitor.monitor_positions(alert_threshold=70)
