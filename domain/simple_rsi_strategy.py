# domain/simple_rsi_strategy.py
from decimal import Decimal
from typing import List, Optional
from core.enums import Side, OrderType
from core.models import Order
from domain.strategy_base import Strategy

class SimpleRSIStrategy(Strategy):
    def __init__(self,
                 size_fraction=0.3,
                 rsi_low=30,
                 rsi_high=70,
                 sl_pct: Optional[float] = None,
                 tp_pct: Optional[float] = None, leverage=1.0, symbol: str = None):
        self.size_fraction = Decimal(str(size_fraction))
        self.rsi_low = rsi_low
        self.rsi_high = rsi_high
        self.sl_pct = sl_pct
        self.tp_pct = tp_pct
        self.leverage = leverage
        self.symbol = symbol

    def on_data(self, data) -> List[Order]:
        rsi = data.indicators.get("rsi")
        if rsi is None:
            return []

        price = Decimal(data.close)
        pos = self.broker.get_position(self.symbol)
        orders = []

        if pos is None:
            # Fresh entry
            quantity = self.compute_quantity(
                account_balance=self.broker.account_balance,
                price=float(price),
                size_fraction=float(self.size_fraction),
                leverage=float(self.leverage)
            )

            if rsi < self.rsi_low:
                side = Side.BUY
            elif rsi > self.rsi_high:
                side = Side.SELL
            else:
                return []

            sl = self.compute_stop_loss(float(price), self.sl_pct, side, leverage=self.leverage)
            tp = self.compute_take_profit(float(price), self.tp_pct, side, leverage=self.leverage)

            orders.append(Order(
                asset=self.symbol,
                side=side,
                quantity=quantity,
                order_type=OrderType.MARKET,
                timestamp=data.timestamp,
                execution_price=price,
                leverage=self.leverage,
                stop_price=Decimal(sl) if sl else None,
                take_profit=Decimal(tp) if tp else None,
                client_tag="entry"
            ))
            return orders

        # Flip logic
        current_side = pos.side
        flip_signal = None

        if rsi < self.rsi_low and current_side == Side.SELL:
            flip_signal = Side.BUY
        elif rsi > self.rsi_high and current_side == Side.BUY:
            flip_signal = Side.SELL

        if flip_signal:
            # 1. Close
            orders.append(Order(
                asset=self.symbol,
                side=flip_signal,
                quantity=pos.quantity,
                order_type=OrderType.MARKET,
                timestamp=data.timestamp,
                execution_price=price,
                leverage=self.leverage,
                client_tag="close"
            ))

            # 2. Recalculate available cash post-close
            if pos.side == Side.BUY:
                pnl = (price - pos.average_entry_price) * pos.quantity
            else:
                pnl = (pos.average_entry_price - price) * pos.quantity

            projected_balance = self.broker.account_balance + pnl + pos.margin
            
            quantity = self.compute_quantity(
            account_balance=projected_balance,
            price=float(price),
            size_fraction=float(self.size_fraction),
            leverage=float(self.leverage)
        )

            sl = self.compute_stop_loss(float(price), self.sl_pct, flip_signal, leverage=self.leverage)
            tp = self.compute_take_profit(float(price), self.tp_pct, flip_signal, leverage=self.leverage)

            orders.append(Order(
                asset=self.symbol,
                side=flip_signal,
                quantity=quantity,
                order_type=OrderType.MARKET,
                timestamp=data.timestamp,
                execution_price=price,
                leverage=self.leverage,
                stop_price=Decimal(sl) if sl else None,
                take_profit=Decimal(tp) if tp else None,
                client_tag="reentry"
            ))

        return orders
