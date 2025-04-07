from core.models import Order, Trade
from core.enums import OrderStatus, Side, OrderType
from services.executor import OrderExecutor
from uuid import uuid4
from decimal import Decimal

class MockExecutor(OrderExecutor):
    """
    Simulates order execution without connecting to a real exchange.

    Good for local testing of trading logic and strategy behavior.
    """

    def __init__(self, broker=None):
        self.broker = broker
        self.orders = {}  # order_id -> Order
        self.trades = []  # List of Trade objects
        # self.watched_exits = []  # To track SL/TP conditions


    def submit_order(self, order: Order) -> str:
        """
        Handles MARKET and LIMIT orders for backtesting.
        MARKET orders are filled immediately.
        LIMIT orders are stored as PENDING and checked via check_pending_limits().
        """
        order_id = str(uuid4())
        self.orders[order_id] = order

        if order.order_type == OrderType.MARKET:
            order.status = OrderStatus.FILLED
            # In backtest, we simulate immediate market fill at close
            order.execution_price = order.execution_price or Decimal("0")  # will be set in engine or strategy
            order.timestamp = order.timestamp or datetime.utcnow()

            trade = Trade(
                order=order,
                execution_price=order.execution_price,
                quantity=order.quantity,
                timestamp=order.timestamp
            )
            self.trades.append(trade)
            return order_id

        elif order.order_type == OrderType.LIMIT:
            order.status = OrderStatus.PENDING
            print(f"[MockExecutor] LIMIT order queued: {order.side.name} {order.quantity} @ {order.price}")
            return order_id

        else:
            print(f"[MockExecutor] Unsupported order type: {order.order_type}")
            return order_id


    def cancel_order(self, order_id: str):
        """
        Simulate cancellation of an order (if not already filled).
        """
        order = self.orders.get(order_id)
        if order and order.status == OrderStatus.PENDING:
            order.status = OrderStatus.CANCELLED
            print(f"[MockExecutor] Cancelled order {order_id}")
        else:
            print(f"[MockExecutor] Cannot cancel: Order already filled or unknown")

    def fetch_order_status(self, order_id: str):
        """
        Return the current status of the given order.
        """
        order = self.orders.get(order_id)
        return order.status if order else None
    
    def check_exit_triggers(self, snapshot):
        # from decimal import Decimal  # to be safe
        price_high = Decimal(snapshot.high)
        price_low = Decimal(snapshot.low)
        price_close = Decimal(snapshot.close)

        triggered = []

        for symbol, pos in list(self.broker.positions.items()):
            sl = pos.stop_loss
            tp = pos.take_profit
            exit_side = Side.BUY if pos.side == Side.SELL else Side.SELL

            # Log current state
            # print(f"🔍 Checking SL/TP for {symbol} | SL={sl} TP={tp} | Side={pos.side.name}")

            if pos.side == Side.BUY:
                sl_hit = sl and price_low <= sl
                tp_hit = tp and price_high >= tp
            else:  # pos.side == Side.SELL
                sl_hit = sl and price_high >= sl
                tp_hit = tp and price_low <= tp

            if sl_hit or tp_hit:
                print(f"🚨 Triggered exit for {symbol}: SL={sl_hit}, TP={tp_hit}")
                exit_order = Order(
                    asset=symbol,
                    side=exit_side,
                    quantity=pos.quantity,
                    order_type=OrderType.MARKET,
                    execution_price=price_close,
                    timestamp=snapshot.timestamp,
                    leverage=pos.leverage,  # ✅ This line is key
                    client_tag="tp_exit" if tp_hit else "sl_exit"
                )
                self.submit_order(exit_order)
                trade = Trade(order=exit_order, execution_price=price_close, quantity=pos.quantity, timestamp=snapshot.timestamp)
                self.trades.append(trade)
                self.broker.record_trade(trade)
                if self.broker.logger:
                    self.broker.logger.log_trade(trade, self.broker)

    def check_pending_limits(self, snapshot):
        filled = []
        for order_id, order in list(self.orders.items()):
            if order.status != OrderStatus.PENDING:
                continue

            if not order.price:
                continue

            limit_price = Decimal(order.price)
            fill = False

            if order.side == Side.BUY and snapshot.low <= limit_price:
                fill = True
            elif order.side == Side.SELL and snapshot.high >= limit_price:
                fill = True

            if fill:
                order.status = OrderStatus.FILLED
                order.execution_price = limit_price
                order.timestamp = snapshot.timestamp

                trade = Trade(
                    order=order,
                    execution_price=limit_price,
                    quantity=order.quantity,
                    timestamp=snapshot.timestamp
                )
                self.trades.append(trade)
                self.broker.record_trade(trade)
                if self.broker.logger:
                    self.broker.logger.log_trade(trade, self.broker)

                filled.append(order_id)
        return filled
