import httpx

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}

apis = [
    ("腾讯K线", "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sh600519,day,,,5,qfq"),
    ("新浪K线", "https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh600519&scale=240&ma=no&datalen=5"),
    ("腾讯实时", "https://qt.gtimg.cn/q=sh600519"),
    ("新浪实时", "https://hq.sinajs.cn/list=sh600519"),
    ("东方财富HTTPS", "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&fields=f2,f3,f14&secids=1.000001"),
    ("东方财富HTTP", "http://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&fields=f2,f3,f14&secids=1.000001"),
]

for name, url in apis:
    try:
        resp = httpx.get(url, headers=headers, timeout=10, follow_redirects=True)
        print(f"✅ {name}: {resp.status_code} ({len(resp.text)} bytes)")
        if len(resp.text) < 200:
            print(f"   {resp.text[:150]}")
    except Exception as e:
        print(f"❌ {name}: {type(e).__name__}: {str(e)[:100]}")
