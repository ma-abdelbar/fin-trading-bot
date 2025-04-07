from decimal import Decimal
from domain.simple_rsi_strategy import SimpleRSIStrategy
import domain.sample_strategies as ss
from indicators.rsi import RSIIndicator
from services.broker import Broker
from services.trade_logger import TradeLogger
from services.binance_executor import BinanceExecutor
from config.settings import BINANCE_API_KEY, BINANCE_API_SECRET
from live.engine import LiveEngine


def fetch_balance_usdt(executor):
    balance = executor.exchange.fetch_balance()
    usdt = balance['total'].get('USDT', 0)
    return Decimal(str(usdt))


def main():
    executor = BinanceExecutor(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET, testnet=True)
    balance = fetch_balance_usdt(executor)
    print(f"💰 Testnet account balance (USDT): {balance}")

    broker = Broker(account_balance=balance, logger=TradeLogger())
    executor.broker = broker
    broker.executor = executor

    indicators = {
        "rsi": RSIIndicator(period=14),
    }

    engine = LiveEngine(
        strategy_cls=lambda: ss.BuySell(
            size_fraction=0.1,                    # Use 100% of testnet account
            sl_pct=0.05,
            tp_pct=20.0,
            leverage=20,
            symbol="BTC/USDT",
            price=Decimal("60000")               # 👈 Limit entry at 60k
        ),
        executor=executor,
        indicators=indicators,
        symbol="BTC/USDT",
        timeframe="1m",
        poll_interval=60
    )

    engine.run()


if __name__ == "__main__":
    main()
