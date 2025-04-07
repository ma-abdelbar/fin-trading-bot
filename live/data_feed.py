# live/data_feed.py

import ccxt
from datetime import datetime
from decimal import Decimal
from backtest.snapshot import MarketSnapshot


class BinanceDataFeed:
    def __init__(self, symbol="BTC/USDT", timeframe="1m"):
        self.exchange = ccxt.binance()
        self.symbol = symbol
        self.timeframe = timeframe

    def get_snapshot(self) -> MarketSnapshot:
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe=self.timeframe, limit=1)[0]
            ts, o, h, l, c, v = ohlcv

            return MarketSnapshot(
                symbol=self.symbol,
                timestamp=datetime.utcfromtimestamp(ts / 1000),
                open=Decimal(str(o)),
                high=Decimal(str(h)),
                low=Decimal(str(l)),
                close=Decimal(str(c)),
                volume=Decimal(str(v))
            )
        except Exception as e:
            print(f"[BinanceDataFeed] ⚠️ Failed to fetch OHLCV: {e}")
            raise
