from decimal import Decimal
from core.enums import OrderType, Side
from core.models import Order, Trade
from services.mock_executor import MockExecutor
from services.broker import Broker

def main():
    # 1. Set up executor and broker
    executor = MockExecutor()
    broker = Broker(starting_cash=Decimal("1000.00"), executor=executor)

    # 2. Submit a mock BUY order
    buy_order = Order(
        asset="BTC/USDT",
        side=Side.BUY,
        quantity=Decimal("0.01"),
        order_type=OrderType.MARKET
    )
    order_id = broker.submit_order(buy_order)
    trade = executor.trades[-1]  # Get last trade
    broker.record_trade(trade)

    print("\n✅ After BUY:")
    broker.print_status()

    # 3. Submit a SELL order
    sell_order = Order(
        asset="BTC/USDT",
        side=Side.SELL,
        quantity=Decimal("0.01"),
        order_type=OrderType.MARKET
    )
    sell_id = broker.submit_order(sell_order)
    sell_trade = executor.trades[-1]
    broker.record_trade(sell_trade)

    print("\n✅ After SELL:")
    broker.print_status()

if __name__ == "__main__":
    main()
