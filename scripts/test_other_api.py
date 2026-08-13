import httpx

# Test Tencent finance API for K-line data
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://stockapp.finance.qq.com/",
}

# Method 1: Tencent web API
print("=== Tencent K-line API ===")
try:
    # Tencent uses sh600519 format
    url = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
    params = {
        "param": "sh600519,day,2026-01-01,2026-08-13,60,qfq",
    }
    resp = httpx.get(url, params=params, headers=headers, timeout=15)
    print("Status:", resp.status_code)
    data = resp.json()
    qfqday = data.get("data", {}).get("sh600519", {}).get("qfqday", [])
    if not qfqday:
        qfqday = data.get("data", {}).get("sh600519", {}).get("day", [])
    print("Klines:", len(qfqday))
    if qfqday:
        print("Last 2:")
        for k in qfqday[-2:]:
            print(" ", k)
except Exception as e:
    print("ERROR:", type(e).__name__, str(e)[:500])

# Method 2: Sina API
print("\n=== Sina K-line API ===")
try:
    url = "https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
    params = {
        "symbol": "sh600519",
        "scale": "240",
        "ma": "no",
        "datalen": "60",
    }
    resp = httpx.get(url, params=params, headers=headers, timeout=15)
    print("Status:", resp.status_code)
    if resp.status_code == 200:
        import json
        data = json.loads(resp.text)
        print("Klines:", len(data))
        if data:
            print("Last:", data[-1])
except Exception as e:
    print("ERROR:", type(e).__name__, str(e)[:500])

# Method 3: Netease API
print("\n=== Netease K-line API ===")
try:
    url = "https://quotes.money.163.com/service/chddata.html"
    params = {
        "code": "0600519",
        "start": "20260101",
        "end": "20260813",
        "fields": "TCLOSE;HIGH;LOW;TOPEN;LCLOSE;CHG;PCHG;TURNOVER;VOTURNOVER;VATURNOVER",
    }
    resp = httpx.get(url, params=params, headers=headers, timeout=15)
    print("Status:", resp.status_code)
    if resp.status_code == 200:
        lines = resp.text.strip().split('\n')
        print("Rows:", len(lines) - 1)
        if len(lines) > 1:
            print("Last:", lines[-1])
except Exception as e:
    print("ERROR:", type(e).__name__, str(e)[:500])
