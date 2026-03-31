#!/usr/bin/env python3
"""
Quick demo of all 8 new features
Run: python demo_features.py
"""

import sys
sys.path.insert(0, 'c:\\Users\\aravn')

from Trading import (
    BacktestEngine, WatchlistMonitor, SmartMoneyDetector, 
    MultiTimeframeAnalyzer, PositionManager, EquityDashboard, 
    MLSignalWeighter, OptionsStrategist, AIAnalyzer, TechnicalAnalyzer
)
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

def demo():
    console.print("[bold cyan]🚀 FinalAI Quantum v7.0 - Feature Demo[/bold cyan]\n")
    
    # Initialize
    analyzer = AIAnalyzer(api_key=None)
    technical = TechnicalAnalyzer()
    
    console.print("[bold]✓ Feature 1: BacktestEngine[/bold]")
    backtest = BacktestEngine(analyzer, technical)
    console.print("   └─ Ready to backtest historical trades\n")
    
    console.print("[bold]✓ Feature 2: WatchlistMonitor[/bold]")
    watchlist = WatchlistMonitor(analyzer, technical)
    console.print("   └─ Ready to monitor 5+ tickers\n")
    
    console.print("[bold]✓ Feature 3: SmartMoneyDetector[/bold]")
    console.print("   └─ Detects institutional accumulation/distribution\n")
    
    console.print("[bold]✓ Feature 4: MultiTimeframeAnalyzer[/bold]")
    mta = MultiTimeframeAnalyzer(analyzer, technical)
    console.print("   └─ Analyzes 1H/4H/1D alignment\n")
    
    console.print("[bold]✓ Feature 5: PositionManager[/bold]")
    positions = PositionManager()
    console.print("   └─ Tracks open positions with dynamic stops\n")
    
    console.print("[bold]✓ Feature 6: EquityDashboard[/bold]")
    equity = EquityDashboard()
    console.print("   └─ Real-time P&L and Sharpe ratio tracking\n")
    
    console.print("[bold]✓ Feature 7: MLSignalWeighter[/bold]")
    ml = MLSignalWeighter()
    console.print("   └─ Learns optimal indicator weights\n")
    
    console.print("[bold]✓ Feature 8: OptionsStrategist[/bold]")
    console.print("   └─ Suggests protective puts and spreads\n")
    
    console.print("[bold green]All 8 features loaded successfully! ✓[/bold green]\n")
    
    # Show menu preview
    console.print("[bold cyan]Main Menu Structure:[/bold cyan]\n")
    
    menu_items = [
        ("1", "📊 Analyze Stock/Crypto", "[dim](original)[/dim]"),
        ("2", "🔍 Market Scanner", "[dim](original)[/dim]"),
        ("3", "📰 News & Market Intel", "[dim](original)[/dim]"),
        ("4", "🎯 Backtesting Engine", "[green](NEW)[/green]"),
        ("5", "👁️  Watchlist Monitor", "[green](NEW)[/green]"),
        ("6", "💰 Position Manager", "[green](NEW)[/green]"),
        ("7", "📈 Equity Dashboard", "[green](NEW)[/green]"),
        ("8", "🏢 Smart Money Detector", "[green](NEW)[/green]"),
        ("9", "⏱️  Multi-Timeframe", "[green](NEW)[/green]"),
        ("10", "🤖 ML Signal Weighting", "[green](NEW)[/green]"),
        ("11", "📞 Options Strategies", "[green](NEW)[/green]"),
        ("12", "🔬 Theme Research", "[dim](original)[/dim]"),
        ("13", "👔 Insider Trading", "[dim](original)[/dim]"),
        ("14", "🏛️  Political Tracker", "[dim](original)[/dim]"),
        ("15", "⚙️  Settings", "[dim](original)[/dim]"),
        ("16", "🚪 Exit", "[dim](original)[/dim]"),
    ]
    
    table = Table(box=box.ROUNDED)
    table.add_column("Menu #", style="cyan")
    table.add_column("Feature", style="bold")
    table.add_column("Status", style="green")
    
    for num, feature, status in menu_items:
        table.add_row(num, feature, status)
    
    console.print(table)
    
    console.print("\n[bold green]✨ Demo Complete![/bold green]")
    console.print("Run: [bold]python Trading.py[/bold] to start the interactive bot\n")

if __name__ == "__main__":
    demo()
