import httpx
import json

# Test kline API directly
url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
params = {
    "fields1": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13",
    "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
    "beg": "19000101",
    "end": "20500101",
    "rtntype": "6",
    "secid": "1.600519",
    "klt": "101",
    "fqt": "1",
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://finance.eastmoney.com/",
}

print("=== Test kline API ===")
try:
    resp = httpx.get(url, params=params, headers=headers, timeout=15)
    print("Status:", resp.status_code)
    data = resp.json()
    klines = data.get("data", {}).get("klines", [])
    print("Klines:", len(klines))
    if klines:
        print("Last 2:")
        for k in klines[-2:]:
            print(" ", k)
except Exception as e:
    print("ERROR:", type(e).__name__, str(e)[:500])

# Test index API
print("\n=== Test index API ===")
try:
    resp = httpx.get(
        "https://push2.eastmoney.com/api/qt/ulist.np/get",
        params={"fltt": "2", "fields": "f2,f3,f4,f12,f14", "secids": "1.000001,0.399001,0.399006,1.000300"},
        headers=headers,
        timeout=10,
    )
    print("Status:", resp.status_code)
    data = resp.json()
    for item in data.get("data", {}).get("diff", []):
        print(f"  {item.get('f14')}: {item.get('f2')} ({item.get('f3')}%)")
except Exception as e:
    print("ERROR:", type(e).__name__, str(e)[:500])
