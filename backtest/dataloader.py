from pyspark.sql import SparkSession
from backtest.snapshot import MarketSnapshot
from config.settings import DATA_PATH
import os
from datetime import datetime

class SparkOHLCVLoader:
    def __init__(self, symbol: str, timeframe: str, start=None, end=None):
        self.symbol = symbol
        self.timeframe = timeframe
        self.path = os.path.join(DATA_PATH, symbol, f"{symbol}_{timeframe}.parquet")
        self.spark = SparkSession.builder.appName("OHLCVLoader").getOrCreate()
        self.start = start
        self.end = end

    def load_data(self):
        df = self.spark.read.parquet(self.path)

        if self.start:
            df = df.filter(df.timestamp >= self._parse_time(self.start))
        if self.end:
            df = df.filter(df.timestamp <= self._parse_time(self.end))

        return df.orderBy("timestamp")

    def stream_snapshots(self):
        df = self.load_data()
        for row in df.collect():
            yield MarketSnapshot(
                symbol=self.symbol,
                timestamp=row["timestamp"],
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                volume=row["volume"]
            )

    def _parse_time(self, time_str):
        # Support both "YYYY-MM-DD" and "YYYY-MM-DD HH:MM"
        formats = ["%Y-%m-%d", "%Y-%m-%d %H:%M"]
        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Invalid date format: {time_str}")
