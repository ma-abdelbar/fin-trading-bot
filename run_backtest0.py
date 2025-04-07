from backtest.engine import BacktestEngine
from domain.sample_strategies import AlwaysBuyBTC
from domain.sample_strategies import BuyHold
from domain.sample_strategies import BuySell
from domain.sample_strategies import SellBuy
from domain.simple_rsi_strategy import SimpleRSIStrategy
from indicators.rsi import RSIIndicator


def main():
    engine = BacktestEngine(
        strategy_cls=lambda: SimpleRSIStrategy(
            cash_fraction=0.3,
            sl_pct=0.05,      # Means max 5% account risk
            tp_pct=0.15,      # Target 15% profit on position
            leverage=10,      # Leverage used for scaling SL/TP and position size
            symbol="BTC/USDT"
        ),
        symbol="BTC/USDT",
        timeframe="1m",         # Use lower TF for more signal activity
        starting_cash=10_000,
        plot=True,
        indicators={"rsi": RSIIndicator(period=14)},
        start="2021-01-01",     # Or a date range you have data for
        end="2021-01-10"
    )

    engine.run()

if __name__ == "__main__":
    main()
