from typing import Type
from services.mock_executor import MockExecutor
from services.broker import Broker
from backtest.dataloader import SparkOHLCVLoader
from backtest.snapshot import MarketSnapshot
from backtest.enriched_snapshot import EnrichedSnapshot
from services.trade_logger import TradeLogger
from core.models import Order, Trade
from core.enums import OrderStatus
from domain.strategy_base import Strategy
import matplotlib.pyplot as plt

class BacktestEngine:
    def __init__(self, strategy_cls: Type[Strategy], symbol: str, timeframe: str, account_balance=10000,
                 plot=False, indicators=None, start=None, end=None):
        self.strategy = strategy_cls()
        self.symbol = symbol
        self.timeframe = timeframe
        self.executor = MockExecutor()
        self.broker = Broker(account_balance=account_balance)
        self.executor.broker = self.broker 
        self.strategy.broker = self.broker  # 👈 patch broker reference
        self.loader = SparkOHLCVLoader(symbol=symbol, timeframe=timeframe, start=start, end=end)
        self.logger = TradeLogger()
        self.broker.logger = self.logger
        self.plot = plot
        self.indicators = indicators or {}

    def run(self):
        self.logger.log_start(self.broker.account_balance)

        for snapshot in self.loader.stream_snapshots():
            for ind in self.indicators.values():
                ind.update(snapshot)

            enriched = EnrichedSnapshot(
                snapshot,
                {name: ind.get() for name, ind in self.indicators.items()}
            )

            self.executor.check_exit_triggers(enriched)
            self.executor.check_pending_limits(enriched)

            orders = self.strategy.on_data(enriched)

            for order in orders:
                order_id = self.executor.submit_order(order)

                # Only record/log trade if a trade actually happened
                if self.executor.orders[order_id].status == OrderStatus.FILLED:
                    # Find the trade that corresponds to this order
                    related_trades = [t for t in self.executor.trades if t.order == self.executor.orders[order_id]]
                    if related_trades:
                        trade = related_trades[-1]
                        self.broker.record_trade(trade)
                        self.logger.log_trade(trade, self.broker)

        # ✅ Handle any final closing logic
        if hasattr(self.strategy, "finalize"):
            final_orders = self.strategy.finalize(snapshot)
            for order in final_orders:
                order.execution_price = snapshot.close
                order.timestamp = snapshot.timestamp

                order_id = self.executor.submit_order(order)
                trade = self.executor.trades[-1]

                self.broker.record_trade(trade)
                self.logger.log_trade(trade, self.broker)

        self.broker.last_price = snapshot.close
        self.logger.log_end(self.broker)

        # ✅ Optional indicator plot
        if hasattr(self, "plot") and self.plot:
            self.plot_trades(
                overlay_indicators={},  # <-- You can move indicators here if needed
                subplot_indicators={k: v for k, v in self.indicators.items()}
            )

            


    def plot_trades(self, overlay_indicators=None, subplot_indicators=None):
        closes = []
        timestamps = []
        buy_times, buy_prices = [], []
        sell_times, sell_prices = [], []

        for snapshot in self.loader.stream_snapshots():
            closes.append(snapshot.close)
            timestamps.append(snapshot.timestamp)

        for trade in self.executor.trades:
            if trade.order.side.name == "BUY":
                buy_times.append(trade.timestamp)
                buy_prices.append(float(trade.execution_price))
            elif trade.order.side.name == "SELL":
                sell_times.append(trade.timestamp)
                sell_prices.append(float(trade.execution_price))

        # Handle figure and subplots
        n_subplots = 2 if subplot_indicators else 1
        fig, axs = plt.subplots(n_subplots, 1, figsize=(12, 6), sharex=True, gridspec_kw={'height_ratios': [3, 1] if n_subplots == 2 else [1]})

        price_ax = axs[0] if n_subplots == 2 else axs
        price_ax.plot(timestamps, closes, label="Close Price", color="black")
        price_ax.scatter(buy_times, buy_prices, color="green", marker="^", label="BUY", zorder=5)
        price_ax.scatter(sell_times, sell_prices, color="red", marker="v", label="SELL", zorder=5)

        if overlay_indicators:
            for name, indicator in overlay_indicators.items():
                series = indicator.get_series()
                if series:
                    ts, values = series
                    price_ax.plot(ts, values, label=name)

        price_ax.set_title(f"{self.symbol} — {self.timeframe} Backtest")
        price_ax.set_ylabel("Price")
        price_ax.legend()
        price_ax.grid(True)

        if subplot_indicators:
            sub_ax = axs[1]
            for name, indicator in subplot_indicators.items():
                series = indicator.get_series()
                if series:
                    ts, values = series
                    sub_ax.plot(ts, values, label=name)
            sub_ax.set_ylabel("Indicator")
            sub_ax.set_xlabel("Time")
            sub_ax.legend()
            sub_ax.grid(True)

        plt.tight_layout()
        plt.show()

    def _was_position_closed(self, trade: Trade) -> bool:
        """Check if this trade closed the position."""
        symbol = trade.order.asset
        return symbol not in self.broker.positions

    
