from abc import ABC, abstractmethod
from typing import List, Optional
from core.models import Order
from core.enums import Side
from decimal import Decimal, ROUND_DOWN


class Strategy(ABC):
    """
    Base interface for any trading strategy.

    The strategy receives market data and returns one or more orders.
    """

    @abstractmethod
    def on_data(self, data: dict) -> List[Order]:
        """
        Called on every time step (new candle/tick).

        Args:
            data (dict): Latest market data snapshot (price, indicators, etc.)

        Returns:
            List[Order]: Orders to be submitted.
        """
        pass

    def compute_stop_loss(self, entry_price: float, sl_pct: Optional[float], side, leverage: Optional[float] = 1.0) -> Optional[float]:
        if sl_pct is None:
            return None
        price_pct = sl_pct / leverage
        return entry_price * (1 - price_pct) if side == Side.BUY else entry_price * (1 + price_pct)

    def compute_take_profit(self, entry_price: float, tp_pct: Optional[float], side, leverage: Optional[float] = 1.0) -> Optional[float]:
        if tp_pct is None:
            return None
        price_pct = tp_pct / leverage
        return entry_price * (1 + price_pct) if side == Side.BUY else entry_price * (1 - price_pct)


    def compute_quantity(self, account_balance: Decimal, price: float, size_fraction: float, leverage: float) -> Decimal:
        """
        Computes position size (quantity) using leverage.

        Args:
            cash_available: how much total cash you can spend
            price: current asset price
            cash_fraction: fraction of cash to use (e.g. 0.3 = 30%)
            leverage: intended leverage (e.g. 10x)

        Returns:
            Decimal quantity
        """
        notional = account_balance * Decimal(str(size_fraction)) * Decimal(str(leverage))
        quantity = notional / Decimal(str(price))
        return quantity.quantize(Decimal('0.0001'), rounding=ROUND_DOWN)  # round to 4 decimals (or symbol-specific)


