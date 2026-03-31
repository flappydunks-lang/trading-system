import yfinance as yf
import traceback

tests = [
    ("1y", "1d"),
    ("60d", "5m"),
]

for period, interval in tests:
    try:
        print(f"\n=== Trying ES=F period={period}, interval={interval} ===")
        df = yf.download("ES=F", period=period, interval=interval, progress=False, auto_adjust=True)
        if df is None:
            print("Result: None")
            continue
        print("Empty:", df.empty)
        print("Shape:", getattr(df, 'shape', None))
        print(df.head(3).to_string())
    except Exception as e:
        print("Exception:")
        traceback.print_exc()
print('\nDone')
