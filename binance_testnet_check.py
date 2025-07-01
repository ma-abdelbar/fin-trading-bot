import os
import ccxt
from config.settings import BINANCE_API_KEY, BINANCE_API_SECRET
print(BINANCE_API_KEY)

api_key = BINANCE_API_KEY
api_secret = BINANCE_API_SECRET

print("🔑 API KEY:", api_key)
print("🔐 API SECRET:", api_secret)


exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

exchange.set_sandbox_mode(True)
exchange.urls['api'] = exchange.urls['test']

try:
    print("✅ Fetching balance...")
    balance = exchange.fetch_balance()
    print("Balance fetched:", balance['total'])

except Exception as e:
    print("❌ ERROR:", str(e))
