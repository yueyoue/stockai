import akshare as ak
import sys

print('akshare version:', ak.__version__)

# Test 1: get stock spot data
print('\n=== Test 1: spot data ===')
try:
    df = ak.stock_zh_a_spot_em()
    print('rows:', len(df))
    print(df.columns.tolist())
    row = df[df['代码'] == '600519']
    if not row.empty:
        print(row.iloc[0].to_dict())
    else:
        print('600519 not found')
except Exception as e:
    print('ERROR:', type(e).__name__, str(e)[:300])

# Test 2: get kline
print('\n=== Test 2: kline ===')
try:
    df = ak.stock_zh_a_hist(symbol='600519', period='daily', adjust='qfq')
    print('rows:', len(df))
    print(df.tail(2).to_string())
except Exception as e:
    print('ERROR:', type(e).__name__, str(e)[:300])

# Test 3: get index
print('\n=== Test 3: index ===')
try:
    df = ak.stock_zh_index_spot_em()
    print('rows:', len(df))
    target = df[df['名称'].isin(['上证指数', '深证成指', '创业板指'])]
    print(target[['代码', '名称', '最新价', '涨跌幅']].to_string())
except Exception as e:
    print('ERROR:', type(e).__name__, str(e)[:300])
