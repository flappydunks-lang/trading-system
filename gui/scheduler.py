"""FinalAI Quantum — Auto-Scheduler

Creates/removes Windows Task Scheduler tasks to auto-start the trading bot
at market open and stop at market close. Toggle on/off from the app.

Usage:
    python gui/scheduler.py enable   — create scheduled tasks
    python gui/scheduler.py disable  — remove scheduled tasks
    python gui/scheduler.py status   — check if enabled
"""

import subprocess, sys, os
from pathlib import Path

PYTHON = str(Path(sys.executable))
REPO = str(Path(__file__).resolve().parent.parent)
TASK_PREFIX = "FinalAI_Quantum"

# Trading.py auto-scan script (runs as the bot)
SCAN_SCRIPT = REPO + "\\Trading.py"

# Schedule: market open (9:25 AM ET) and close (4:05 PM ET), Mon-Fri
OPEN_TIME = "09:25"
CLOSE_TIME = "16:05"


def _run(cmd, check=False):
    """Run a command and return (success, output)."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return r.returncode == 0, r.stdout + r.stderr
    except Exception as e:
        return False, str(e)


def enable():
    """Create Windows Task Scheduler tasks for auto-trading."""
    # Task 1: Start bot at market open (Mon-Fri 9:25 AM)
    ok1, out1 = _run(
        f'schtasks /create /tn "{TASK_PREFIX}_MarketOpen" '
        f'/tr "\\\"{PYTHON}\\\" \\\"{SCAN_SCRIPT}\\\" --auto-scan" '
        f'/sc weekly /d MON,TUE,WED,THU,FRI /st {OPEN_TIME} '
        f'/f /rl HIGHEST'
    )

    # Task 2: Stop bot at market close (Mon-Fri 4:05 PM)
    ok2, out2 = _run(
        f'schtasks /create /tn "{TASK_PREFIX}_MarketClose" '
        f'/tr "taskkill /f /im python.exe /fi \\"WINDOWTITLE eq FinalAI*\\"" '
        f'/sc weekly /d MON,TUE,WED,THU,FRI /st {CLOSE_TIME} '
        f'/f /rl HIGHEST'
    )

    if ok1:
        print(f"[+] Market open task created ({OPEN_TIME} ET, Mon-Fri)")
    else:
        print(f"[-] Failed to create open task: {out1[:200]}")

    if ok2:
        print(f"[+] Market close task created ({CLOSE_TIME} ET, Mon-Fri)")
    else:
        print(f"[-] Failed to create close task: {out2[:200]}")

    # Save state
    Path(REPO + "/config/auto_schedule.json").write_text('{"enabled": true}')
    print("\nAuto-schedule ENABLED. The bot will start at 9:25 AM and stop at 4:05 PM ET.")
    return ok1 and ok2


def disable():
    """Remove the scheduled tasks."""
    _run(f'schtasks /delete /tn "{TASK_PREFIX}_MarketOpen" /f')
    _run(f'schtasks /delete /tn "{TASK_PREFIX}_MarketClose" /f')
    try:
        Path(REPO + "/config/auto_schedule.json").write_text('{"enabled": false}')
    except Exception:
        pass
    print("Auto-schedule DISABLED.")
    return True


def status():
    """Check if auto-schedule is enabled."""
    try:
        import json
        data = json.loads(Path(REPO + "/config/auto_schedule.json").read_text())
        enabled = data.get('enabled', False)
    except Exception:
        enabled = False

    ok1, _ = _run(f'schtasks /query /tn "{TASK_PREFIX}_MarketOpen" 2>nul')
    ok2, _ = _run(f'schtasks /query /tn "{TASK_PREFIX}_MarketClose" 2>nul')

    print(f"Config: {'ENABLED' if enabled else 'DISABLED'}")
    print(f"Open task:  {'EXISTS' if ok1 else 'NOT FOUND'}")
    print(f"Close task: {'EXISTS' if ok2 else 'NOT FOUND'}")
    return enabled and ok1 and ok2


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gui/scheduler.py [enable|disable|status]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "enable":
        enable()
    elif cmd == "disable":
        disable()
    elif cmd == "status":
        status()
    else:
        print(f"Unknown command: {cmd}")
