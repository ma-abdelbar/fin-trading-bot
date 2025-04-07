import ccxt
import pandas as pd
from datetime import datetime, timedelta
import os
import time

class OHLCVDownloader:
    def __init__(self, exchange_name="binance", symbol="BTC/USDT", limit=1000, pause=1.2):
        self.exchange = getattr(ccxt, exchange_name)()
        self.symbol = symbol
        self.limit = limit
        self.pause = pause  # delay to avoid rate limits

    def fetch_ohlcv_range(self, timeframe: str, start_date: str) -> pd.DataFrame:
        since = int(pd.Timestamp(start_date).timestamp() * 1000)
        now = int(datetime.utcnow().timestamp() * 1000)
        all_data = []

        while since < now:
            batch = self.exchange.fetch_ohlcv(self.symbol, timeframe, since=since, limit=self.limit)

            if not batch:
                break  # No more data available

            all_data.extend(batch)

            # Update 'since' to last timestamp + 1 ms
            last_ts = batch[-1][0]
            since = last_ts + 1

            print(f"Fetched {len(batch)} candles up to {pd.to_datetime(last_ts, unit='ms')}")
            time.sleep(self.pause)  # Respect rate limits

        df = pd.DataFrame(all_data, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df

    def save_to_parquet(self, df: pd.DataFrame, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_parquet(path, index=False, engine="pyarrow", coerce_timestamps="ms")
        print(f"✅ Saved to {path}")
