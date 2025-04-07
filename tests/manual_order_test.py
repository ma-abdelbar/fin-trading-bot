from decimal import Decimal
from core.enums import OrderType, Side
from core.models import Order
from services.mock_executor import MockExecutor
from services.broker import Broker

def main():
    executor = MockExecutor()
    broker = Broker(starting_cash=Decimal("1000.00"), executor=executor)

    # --- MANUAL ORDER CREATION ---
    order = Order(
        asset="BTC/USDT",
        side=Side.BUY,                   # Change to Side.SELL to test short side
        quantity=Decimal("0.005"),
        order_type=OrderType.LIMIT,      # Try OrderType.MARKET or STOP too
        price=Decimal("99.00"),          # Only used for LIMIT and STOP
        iceberg=None                     # Add support later
    )

    print("📤 Submitting manual order...")
    order_id = broker.submit_order(order)

    # In MockExecutor, it fills immediately
    trade = executor.trades[-1]
    broker.record_trade(trade)

    print("\n✅ Final State:")
    broker.print_status()

if __name__ == "__main__":
    main()
