import efinance as ef
import httpx

# Test 1: efinance realtime
print("=== efinance realtime ===")
df = ef.stock.get_realtime_quotes()
print(f"Total rows: {len(df)}")
row = df[df['股票代码'] == '600519']
if not row.empty:
    r = row.iloc[0]
    print(f"Price: {r.get('最新价')}")
    print(f"Change: {r.get('涨跌幅')}%")
    print(f"Volume: {r.get('成交量')}")
else:
    print("600519 not found")

# Test 2: Index API
print("\n=== Index API ===")
try:
    resp = httpx.get(
        "https://push2.eastmoney.com/api/qt/ulist.np/get",
        params={"fltt": "2", "fields": "f2,f3,f4,f12,f14", "secids": "1.000001,0.399001,0.399006,1.000300"},
        headers={"User-Agent": "Mozilla/5.0", "Referer": "https://finance.eastmoney.com/"},
        timeout=10,
    )
    print(f"Status: {resp.status_code}")
    data = resp.json()
    for item in data.get("data", {}).get("diff", []):
        print(f"  {item.get('f14')}: {item.get('f2')} ({item.get('f3')}%)")
except Exception as e:
    print(f"ERROR: {e}")
