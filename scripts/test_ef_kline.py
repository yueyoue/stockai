import efinance as ef

# Test different kline methods
print("=== Method 1: get_quote_history ===")
try:
    df = ef.stock.get_quote_history("600519", klt=101)
    print("rows:", len(df))
    if not df.empty:
        print(df.tail(2).to_string())
except Exception as e:
    print("ERROR:", type(e).__name__, str(e)[:500])

print("\n=== Method 2: with beg/end ===")
try:
    df = ef.stock.get_quote_history("600519", beg="20260101", end="20260813", klt=101)
    print("rows:", len(df))
    if not df.empty:
        print(df.tail(2).to_string())
except Exception as e:
    print("ERROR:", type(e).__name__, str(e)[:500])

print("\n=== Method 3: with market ===")
try:
    df = ef.stock.get_quote_history("600519", market="沪A", klt=101)
    print("rows:", len(df))
except Exception as e:
    print("ERROR:", type(e).__name__, str(e)[:500])

print("\n=== Method 4: with secid ===")
try:
    df = ef.stock.get_quote_history("1.600519", klt=101)
    print("rows:", len(df))
except Exception as e:
    print("ERROR:", type(e).__name__, str(e)[:500])
