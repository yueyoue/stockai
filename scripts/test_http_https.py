import httpx

headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.eastmoney.com/"}

# Test HTTP vs HTTPS
print("=== HTTP (port 80) ===")
try:
    resp = httpx.get("http://push2.eastmoney.com/api/qt/ulist.np/get",
        params={"fltt": "2", "fields": "f2,f3,f4,f12,f14", "secids": "1.000001"},
        headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {str(e)[:200]}")

print("\n=== HTTPS (port 443) ===")
try:
    resp = httpx.get("https://push2.eastmoney.com/api/qt/ulist.np/get",
        params={"fltt": "2", "fields": "f2,f3,f4,f12,f14", "secids": "1.000001"},
        headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    print(resp.text[:300])
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {str(e)[:200]}")

# Test realtime via HTTPS
print("\n=== Realtime via HTTPS ===")
try:
    resp = httpx.get("https://push2.eastmoney.com/api/qt/clist/get",
        params={"pn": "1", "pz": "5", "po": "1", "np": "1", "fltt": "2", "invt": "2",
                "fid": "f12", "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048",
                "fields": "f12,f14,f3,f2"},
        headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    print(resp.text[:300])
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {str(e)[:200]}")
