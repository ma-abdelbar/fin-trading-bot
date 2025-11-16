import matplotlib
matplotlib.use('TkAgg')
from decimal import Decimal
from domain.simple_rsi_strategy import SimpleRSIStrategy
from indicators.rsi import RSIIndicator
from backtest.engine import BacktestEngine


def main():
    symbol = "BTCUSDT"

    engine = BacktestEngine(
        strategy_cls=lambda: SimpleRSIStrategy(
            size_fraction=0.3,
            leverage=5,
            symbol=symbol,
            rsi_low=30,
            rsi_high=70
        ),
        symbol=symbol,
        timeframe="1m",
        account_balance=10000,
        plot=True,
        indicators={"rsi": RSIIndicator(period=14)},
        start="2021-01-01",
        end="2021-01-02"
    )

    print(f"🔁 Starting with balance: {engine.broker.account_balance}")
    engine.run()


if __name__ == "__main__":
    main()
