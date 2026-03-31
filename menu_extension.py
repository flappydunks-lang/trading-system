# ADD THESE METHODS TO THE FinalAIQuantum CLASS IN Trading.py
# Copy everything below and add to the class before the main() function

def _run_backtest(self, engine: 'BacktestEngine'):
    """Run backtesting on historical data."""
    from rich.console import Console
    from rich.prompt import Prompt, IntPrompt, FloatPrompt
    from rich.table import Table
    from rich import box
    
    console = Console()
    console.clear()
    console.print("[bold cyan]🎯 Backtesting Engine[/bold cyan]\n")
    
    ticker = Prompt.ask("Enter ticker to backtest")
    start = Prompt.ask("Start date (YYYY-MM-DD)", default="2023-01-01")
    end = Prompt.ask("End date (YYYY-MM-DD)")
    
    console.print(f"\n[yellow]Running backtest for {ticker} ({start} to {end})...[/yellow]")
    
    metrics = engine.backtest_ticker(ticker, start, end, self.config.get('account_size', 10000))
    
    if metrics:
        table = Table(title=f"📊 Backtest Results: {ticker}", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Trades", str(metrics.total_trades))
        table.add_row("Winning Trades", f"{metrics.winning_trades} ({metrics.win_rate*100:.1f}%)")
        table.add_row("Losing Trades", str(metrics.losing_trades))
        table.add_row("Avg Win / Avg Loss", f"${metrics.avg_win:,.0f} / ${metrics.avg_loss:,.0f}")
        table.add_row("Profit Factor", f"{metrics.profit_factor:.2f}")
        table.add_row("Total P&L", f"${metrics.total_pnl:,.0f}")
        table.add_row("Max Drawdown", f"{metrics.max_drawdown*100:.2f}%")
        table.add_row("Sharpe Ratio", f"{metrics.sharpe_ratio:.2f}")
        table.add_row("Sortino Ratio", f"{metrics.sortino_ratio:.2f}")
        table.add_row("Calmar Ratio", f"{metrics.calmar_ratio:.2f}")
        table.add_row("Expectancy", f"${metrics.expectancy:,.0f}")
        
        console.print(table)
        
        if engine.trades:
            console.print(f"\n[cyan]Sample Trades (first 5):[/cyan]")
            for trade in engine.trades[:5]:
                pnl_color = "[green]" if trade.pnl > 0 else "[red]"
                console.print(f"{trade.ticker} {trade.direction} {pnl_color}{trade.pnl_percent:+.2f}%[/] - {trade.reason}")
    
    Prompt.ask("\nPress Enter to continue")

def _run_watchlist(self, watchlist: 'WatchlistMonitor'):
    """Monitor watchlist of tickers."""
    from rich.console import Console
    from rich.prompt import Prompt, IntPrompt
    
    console = Console()
    console.clear()
    console.print("[bold cyan]👁️  Watchlist Monitor[/bold cyan]\n")
    
    console.print("1. Add ticker to watchlist")
    console.print("2. Scan watchlist for signals")
    console.print("3. View active trades\n")
    
    choice = Prompt.ask("Select", choices=["1", "2", "3"], default="2")
    
    if choice == "1":
        ticker = Prompt.ask("Enter ticker to add")
        min_conf = IntPrompt.ask("Minimum confidence (%)", default=70)
        watchlist.add_to_watchlist(ticker, min_conf)
        console.print(f"[green]✓ Added {ticker}[/green]")
    
    elif choice == "2":
        alerts = watchlist.scan_watchlist()
        if alerts:
            console.print(f"\n[bold cyan]🚨 Found {len(alerts)} high-confidence signals![/bold cyan]\n")
            for ticker, signal in alerts.items():
                console.print(f"{ticker}: {signal.action} @ {signal.confidence}% confidence")
        else:
            console.print("[yellow]No high-confidence signals found[/yellow]")
    
    elif choice == "3":
        if watchlist.active_trades:
            console.print("\n[cyan]Active Trades:[/cyan]")
            for ticker, trade in watchlist.active_trades.items():
                console.print(f"{ticker}: {trade.direction} @ ${trade.entry_price}")
        else:
            console.print("No active trades")
    
    Prompt.ask("\nPress Enter to continue")

def _manage_positions(self, mgr: 'PositionManager'):
    """Manage open positions."""
    from rich.console import Console
    from rich.prompt import Prompt, IntPrompt, FloatPrompt
    
    console = Console()
    console.clear()
    console.print("[bold cyan]💰 Position Manager[/bold cyan]\n")
    
    console.print("1. Add position")
    console.print("2. Update positions (fetch current prices)")
    console.print("3. View all positions\n")
    
    choice = Prompt.ask("Select", choices=["1", "2", "3"], default="3")
    
    if choice == "1":
        ticker = Prompt.ask("Ticker")
        entry = FloatPrompt.ask("Entry price")
        shares = IntPrompt.ask("Shares")
        direction = Prompt.ask("Direction (BUY/SELL)", choices=["BUY", "SELL"])
        stop = FloatPrompt.ask("Stop loss")
        tp = FloatPrompt.ask("Take profit")
        
        mgr.add_position(ticker, entry, shares, direction, stop, tp)
        console.print("[green]✓ Position added[/green]")
    
    elif choice == "2":
        mgr.update_positions()
        console.print("[green]✓ Positions updated[/green]")
    
    elif choice == "3":
        console.print(mgr.get_position_summary())
    
    Prompt.ask("\nPress Enter to continue")

def _detect_smart_money(self):
    """Detect smart money accumulation/distribution."""
    from rich.console import Console
    from rich.prompt import Prompt
    import yfinance as yf
    
    console = Console()
    console.clear()
    console.print("[bold cyan]🏢 Smart Money Detector[/bold cyan]\n")
    
    ticker = Prompt.ask("Enter ticker")
    
    try:
        df = yf.download(ticker, period="60d", progress=False)
        indicators = TechnicalAnalyzer.calculate_indicators(df)
        
        signals = SmartMoneyDetector.get_all_signals(df, indicators)
        
        if signals:
            console.print(f"\n[bold cyan]Found {len(signals)} Smart Money signals:[/bold cyan]\n")
            for sig in signals[:10]:
                console.print(f"[{sig.type}] ${sig.price_level:.2f} - Strength: {sig.strength:.0f}% - {sig.description}")
        else:
            console.print("[yellow]No smart money signals detected[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
    
    Prompt.ask("\nPress Enter to continue")

def _multi_timeframe_analysis(self, mta: 'MultiTimeframeAnalyzer'):
    """Analyze across multiple timeframes."""
    from rich.console import Console
    from rich.prompt import Prompt
    from rich.table import Table
    from rich import box
    
    console = Console()
    console.clear()
    console.print("[bold cyan]⏱️  Multi-Timeframe Analysis[/bold cyan]\n")
    
    ticker = Prompt.ask("Enter ticker")
    
    console.print(f"\n[yellow]Analyzing {ticker} across 1H, 4H, and Daily...[/yellow]")
    
    result = mta.analyze_multi_timeframe(ticker)
    
    table = Table(title=f"Multi-Timeframe Signals: {ticker}", box=box.ROUNDED)
    table.add_column("Timeframe", style="cyan")
    table.add_column("Action", style="green")
    table.add_column("Confidence", style="yellow")
    
    for tf in ['1h', '4h', '1d']:
        if result[tf]:
            table.add_row(tf.upper(), result[tf]['action'], f"{result[tf]['confidence']}%")
    
    console.print(table)
    console.print(f"\n[bold]Alignment: {result['alignment']}[/bold]")
    console.print(f"Overall Confidence: {result['overall_confidence']:.0f}%")
    
    Prompt.ask("\nPress Enter to continue")

def _ml_signal_training(self, weighter: 'MLSignalWeighter', backtest: 'BacktestEngine'):
    """Train ML signal weighting."""
    from rich.console import Console
    from rich.prompt import Prompt
    from rich.table import Table
    from rich import box
    
    console = Console()
    console.clear()
    console.print("[bold cyan]🤖 ML Signal Weighting[/bold cyan]\n")
    
    console.print("1. View current weights")
    console.print("2. Retrain from backtest history")
    console.print("3. Show trades used for training\n")
    
    choice = Prompt.ask("Select", choices=["1", "2", "3"], default="1")
    
    if choice == "1":
        table = Table(title="Current Indicator Weights", box=box.ROUNDED)
        table.add_column("Indicator", style="cyan")
        table.add_column("Weight", style="green")
        for key, weight in weighter.weights.items():
            table.add_row(key, f"{weight:.3f}")
        console.print(table)
    
    elif choice == "2":
        weighter.trade_history = backtest.trades
        weighter.retrain_weights()
        console.print("[green]✓ Weights retrained[/green]")
    
    elif choice == "3":
        console.print(f"Trades in history: {len(weighter.trade_history)}")
        for trade in weighter.trade_history[:5]:
            console.print(f"{trade.ticker} {trade.direction} - P&L: ${trade.pnl:,.0f}")
    
    Prompt.ask("\nPress Enter to continue")

def _options_strategies(self):
    """Suggest options strategies."""
    from rich.console import Console
    from rich.prompt import Prompt
    from rich.table import Table
    from rich import box
    import yfinance as yf
    
    console = Console()
    console.clear()
    console.print("[bold cyan]📞 Options Strategy Overlay[/bold cyan]\n")
    
    ticker = Prompt.ask("Enter ticker")
    
    try:
        df = yf.download(ticker, period="1d", progress=False)
        current_price = df['Close'].iloc[-1]
        
        indicators = TechnicalAnalyzer.calculate_indicators(df)
        signal = self.analyzer._fallback_analysis(ticker, indicators, 10000, 0.02, 2.0)
        
        strategy = OptionsStrategist.suggest_strategy(signal, current_price, volatility=0.25)
        
        if strategy:
            table = Table(title=f"Options Strategy: {ticker}", box=box.ROUNDED)
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Strategy Type", strategy.strategy_type)
            table.add_row("Underlying Price", f"${strategy.underlying_price:.2f}")
            table.add_row("Strike", f"${strategy.strike:.2f}")
            table.add_row("Premium", f"${strategy.premium:.2f}")
            table.add_row("Probability of Profit", f"{strategy.probability_of_profit*100:.0f}%")
            table.add_row("Max Risk", f"${strategy.max_risk:.2f}")
            table.add_row("Max Reward", f"${strategy.max_reward:.2f}")
            table.add_row("Recommendation", strategy.recommendation)
            
            console.print(table)
        else:
            console.print("[yellow]No suitable options strategy for current signal[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
    
    Prompt.ask("\nPress Enter to continue")
