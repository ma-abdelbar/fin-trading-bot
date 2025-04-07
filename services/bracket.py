import uuid
from core.models import Order, BracketOrder
from services.broker import Broker
from decimal import Decimal
from core.enums import Side, OrderType

class BracketOrderManager:
    def __init__(self, broker: Broker):
        self.broker = broker
        self.brackets = {}  # bracket_id -> BracketOrder

    def create_bracket(self, asset: str, qty: Decimal, entry_price: Decimal, stop_price: Decimal, target_price: Decimal):
        bracket_id = str(uuid.uuid4())

        # 1. Entry Order
        entry_order = Order(
            asset=asset,
            side=Side.BUY,
            quantity=qty,
            order_type=OrderType.LIMIT,
            price=entry_price
        )

        # 2. Stop-Loss Order (to be submitted *after* entry fills)
        stop_order = Order(
            asset=asset,
            side=Side.SELL,
            quantity=qty,
            order_type=OrderType.STOP,
            stop_price=stop_price
        )

        # 3. Take-Profit Order
        target_order = Order(
            asset=asset,
            side=Side.SELL,
            quantity=qty,
            order_type=OrderType.LIMIT,
            price=target_price
        )

        bracket = BracketOrder(
            id=bracket_id,
            entry_order=entry_order,
            stop_order=stop_order,
            target_order=target_order
        )

        # Submit entry order via broker
        print(f"📥 Submitting entry order for bracket {bracket_id}")
        self.broker.submit_order(entry_order)
        self.brackets[bracket_id] = bracket
        return bracket_id

    def on_trade(self, trade):
        """
        Called whenever a trade is executed.
        Used to monitor and manage bracket logic.
        """
        for bid, bracket in self.brackets.items():
            if not bracket.active:
                continue

            if trade.order == bracket.entry_order and not bracket.filled:
                # Entry filled → submit exits
                print(f"✅ Entry filled for bracket {bid}. Submitting exits.")
                self.broker.submit_order(bracket.stop_order)
                self.broker.submit_order(bracket.target_order)
                bracket.filled = True

            elif trade.order == bracket.stop_order or trade.order == bracket.target_order:
                print(f"🚪 Bracket {bid} exited via {'stop' if trade.order == bracket.stop_order else 'target'}")
                bracket.active = False  # Cancel other? (in real system you'd cancel sibling)

