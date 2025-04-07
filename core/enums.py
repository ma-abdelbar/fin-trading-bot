from enum import Enum, auto

class OrderType(Enum):
    """
    Specifies the type of order being submitted.
    - MARKET: Execute immediately at best available price
    - LIMIT: Execute only at a specific or better price
    - STOP: Becomes a market order once a trigger price is hit
    """
    MARKET = auto()
    LIMIT = auto()
    STOP = auto()
    STOP_LIMIT = auto()  # ← Add this

class OrderStatus(Enum):
    """
    Tracks the lifecycle state of an order.
    """
    PENDING = auto()
    FILLED = auto()
    CANCELLED = auto()
    REJECTED = auto()

class Side(Enum):
    """
    Indicates the trading direction.
    """
    BUY = auto()
    SELL = auto()
