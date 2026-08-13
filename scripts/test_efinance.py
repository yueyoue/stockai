import efinance as ef
import sys

print('efinance imported OK')

# Test realtime quote
print('\n=== Test realtime quotes ===')
try:
    df = ef.stock.get_realtime_quotes()
    print('rows:', len(df))
    print('columns:', df.columns.tolist()[:10])
    row = df[df['股票代码'] == '600519']
    if not row.empty:
        print('600519:', row.iloc[0].to_dict())
    else:
        print('600519 not found in', len(df), 'rows')
except Exception as e:
    print('ERROR:', type(e).__name__, str(e)[:500])

# Test kline
print('\n=== Test kline ===')
try:
    df = ef.stock.get_quote_history('600519', klt=101)
    print('rows:', len(df))
    print(df.tail(3).to_string())
except Exception as e:
    print('ERROR:', type(e).__name__, str(e)[:500])
