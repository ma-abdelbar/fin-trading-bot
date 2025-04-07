# live/engine.py

from services.broker import Broker
from services.trade_logger import TradeLogger
from core.models import Order
from backtest.enriched_snapshot import EnrichedSnapshot
from typing import Type
from domain.strategy_base import Strategy
from live.data_feed import BinanceDataFeed


class LiveEngine:
    def __init__(self, strategy_cls, executor, indicators=None, symbol="BTC/USDT", timeframe="1m", poll_interval=60):
        self.symbol = symbol
        self.indicators = indicators or {}
        self.strategy = strategy_cls()
        self.executor = executor
        self.broker = executor.broker
        self.strategy.broker = self.broker
        self.logger = self.broker.logger or TradeLogger()
        self.poll_interval = poll_interval
        self.feed = BinanceDataFeed(symbol=symbol, timeframe=timeframe)

    def run(self):
        import time
        print(f"🚀 Live engine started for {self.symbol}")
        
        while True:
            snapshot = self.feed.get_snapshot()

            for ind in self.indicators.values():
                ind.update(snapshot)

            enriched = EnrichedSnapshot(
                snapshot,
                {name: ind.get() for name, ind in self.indicators.items()}
            )

            self.executor.check_exit_triggers(snapshot)

            print(f"📡 Tick @ {snapshot.timestamp} | Price: {snapshot.close} | RSI: {self.indicators['rsi'].get()}")

            orders = self.strategy.on_data(enriched)
            for order in orders:
                order.execution_price = snapshot.close
                order.timestamp = snapshot.timestamp

                trade = self.executor.submit_order(order)  # ✅ Capture result

                if trade:  # ✅ Only if trade executed
                    self.broker.record_trade(trade)
                    self.logger.log_trade(trade, self.broker)

            time.sleep(self.poll_interval)
