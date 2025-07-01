from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from core.enums import OrderType, OrderStatus, Side
from typing import Optional, List

@dataclass
class Order:
    """
    Represents a single instruction to the broker/exchange.

    Attributes:
        asset: The symbol being traded (e.g. 'BTC/USDT')
        side: BUY or SELL
        quantity: Size of the order (in base asset units)
        order_type: Type of the order (market, limit, etc.)
        price: Limit or stop price if applicable
        iceberg: If set, only this much is revealed to the market at once
        time_in_force: Future addition for GTC, IOC, FOK, etc.
        client_tag: Optional user-defined metadata
    """
    asset: str
    side: Side
    quantity: Decimal
    order_type: OrderType
    price: Optional[Decimal] = None
    execution_price: Optional[Decimal] = None
    leverage: Decimal = Decimal("1")
    stop_price: Optional[Decimal] = None  # For STOP/STOP_LIMIT
    take_profit: Optional[Decimal] = None
    iceberg: Optional[Decimal] = None
    status: OrderStatus = OrderStatus.PENDING
    timestamp: datetime = field(default_factory=datetime.utcnow)
    client_tag: Optional[str] = None

# @dataclass
# class BracketOrder:
#     id: str
#     entry_order: Order
#     stop_order: Order
#     target_order: Order
#     active: bool = True
#     filled: bool = False


@dataclass
class Trade:
    """
    Represents an executed trade that results from an order.
    """
    order: Order
    execution_price: Decimal
    quantity: Decimal
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Position:
    symbol: str
    quantity: Decimal
    average_entry_price: Decimal
    side: Side
    leverage: Decimal = Decimal("1")
    margin: Optional[Decimal] = None
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None


    @property
    def notional_value(self) -> Decimal:
        return self.quantity * self.average_entry_price * self.leverage
