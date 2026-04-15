"""Daily P&L report for the auto-trader.

Reads logs/trade_closes.jsonl (one close per line, written by Trading.py's
AutoTrader) and prints a per-day breakdown with wins/losses, win rate, net P&L,
best and worst trade, and a running cumulative total.

Usage:
    py daily_pnl.py              # all days
    py daily_pnl.py --days 30    # last 30 days only
    py daily_pnl.py --ticker NVDA   # filter to one symbol
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

LOG = Path('logs/trade_closes.jsonl')


def load_closes(path: Path = LOG) -> list[dict]:
    if not path.exists():
        return []
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out


def group_by_day(closes: list[dict]) -> dict[str, list[dict]]:
    by_day: dict[str, list[dict]] = defaultdict(list)
    for c in closes:
        d = c.get('date') or (c.get('time', '')[:10])
        if not d:
            continue
        by_day[d].append(c)
    return dict(sorted(by_day.items()))


def fmt_money(x: float) -> str:
    sign = "+" if x >= 0 else "-"
    return f"{sign}${abs(x):,.2f}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--days', type=int, default=None, help='only the last N days')
    ap.add_argument('--ticker', type=str, default=None, help='filter to this symbol')
    args = ap.parse_args()

    closes = load_closes()
    if args.ticker:
        t = args.ticker.upper()
        closes = [c for c in closes if c.get('ticker', '').upper() == t]
    if args.days:
        cutoff = (date.today() - timedelta(days=args.days)).isoformat()
        closes = [c for c in closes if (c.get('date') or '') >= cutoff]

    if not closes:
        print("No trade closes logged yet." if not LOG.exists()
              else "No closes match the filter.")
        return

    by_day = group_by_day(closes)

    # Header
    print()
    print(f"  {'Date':<12} {'Trades':>6} {'W':>4} {'L':>4} {'Win%':>7} "
          f"{'Net P&L':>12} {'Best':>11} {'Worst':>11} {'Cumulative':>14}")
    print("  " + "─" * 94)

    cumulative = 0.0
    total_trades = total_wins = total_losses = 0
    grand_pnl = 0.0

    for day, entries in by_day.items():
        wins = sum(1 for e in entries if float(e.get('pnl', 0)) > 0)
        losses = sum(1 for e in entries if float(e.get('pnl', 0)) < 0)
        decided = wins + losses
        win_pct = (wins / decided * 100) if decided else 0.0
        day_pnl = sum(float(e.get('pnl', 0)) for e in entries)
        pnls = [float(e.get('pnl', 0)) for e in entries]
        best = max(pnls) if pnls else 0.0
        worst = min(pnls) if pnls else 0.0
        cumulative += day_pnl

        color_pnl = "\x1b[32m" if day_pnl >= 0 else "\x1b[31m"
        color_cum = "\x1b[32m" if cumulative >= 0 else "\x1b[31m"
        reset = "\x1b[0m"

        print(f"  {day:<12} {len(entries):>6} {wins:>4} {losses:>4} "
              f"{win_pct:>6.1f}% {color_pnl}{fmt_money(day_pnl):>12}{reset} "
              f"{fmt_money(best):>11} {fmt_money(worst):>11} "
              f"{color_cum}{fmt_money(cumulative):>14}{reset}")

        total_trades += len(entries)
        total_wins += wins
        total_losses += losses
        grand_pnl += day_pnl

    decided_total = total_wins + total_losses
    win_pct_total = (total_wins / decided_total * 100) if decided_total else 0.0

    print("  " + "─" * 94)
    print(f"  {'TOTAL':<12} {total_trades:>6} {total_wins:>4} {total_losses:>4} "
          f"{win_pct_total:>6.1f}% {fmt_money(grand_pnl):>12}"
          f"{'':>11} {'':>11} {fmt_money(cumulative):>14}")

    # Reason breakdown
    print()
    reasons: dict[str, list[float]] = defaultdict(list)
    for c in closes:
        r = c.get('reason', 'UNKNOWN')
        reasons[r].append(float(c.get('pnl', 0)))
    print(f"  {'Reason':<15} {'Count':>6} {'Avg P&L':>10} {'Total P&L':>12}")
    print("  " + "─" * 48)
    for r, pnls in sorted(reasons.items(), key=lambda kv: sum(kv[1]), reverse=True):
        avg = sum(pnls) / len(pnls) if pnls else 0
        print(f"  {r:<15} {len(pnls):>6} {fmt_money(avg):>10} {fmt_money(sum(pnls)):>12}")

    print()


if __name__ == '__main__':
    main()
