# run_backtest.py
from decimal import Decimal
from domain.simple_rsi_strategy import SimpleRSIStrategy
import domain.sample_strategies as ss
from indicators.rsi import RSIIndicator
from backtest.engine import BacktestEngine

def main():
    symbol = "BTCUSDT"  # ✅ Define once

    engine = BacktestEngine(
        strategy_cls=lambda: ss.BuySell(
            size_fraction=0.3,
            sl_pct=0.05,
            tp_pct=0.1,
            leverage=10,
            symbol="BTCUSDT",
            price=Decimal("28732")  # optional
        ),
        symbol=symbol,
        timeframe="1m",
        account_balance=10000,
        plot=True,
        indicators={"rsi": RSIIndicator(period=14)},
        start="2021-01-01",
        end="2021-01-02"
    )
    print(engine.broker.account_balance)
    engine.run()

if __name__ == "__main__":
    
    main()
