from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass
class MarketSnapshot:
    symbol: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
