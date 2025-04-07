from decimal import Decimal
from core.models import Order, Trade
from services.mock_executor import MockExecutor
from services.broker import Broker
from domain.sample_strategies import AlwaysBuyBTC

def main():
    # Setup executor, broker, and strategy
    executor = MockExecutor()
    broker = Broker(starting_cash=Decimal("1000.00"), executor=executor)
    strategy = AlwaysBuyBTC()

    # Simulate a simple stream of candles (5 steps)
    for i in range(5):
        print(f"\n⏱️ Tick {i + 1}")
        market_data = {"close": Decimal("100.00")}  # Mocked price
        orders = strategy.on_data(market_data)

        for order in orders:
            order_id = broker.submit_order(order)
            trade = executor.trades[-1]
            broker.record_trade(trade)

        broker.print_status()

if __name__ == "__main__":
    main()
