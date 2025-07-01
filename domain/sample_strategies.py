from decimal import Decimal
from core.enums import OrderType, Side
from typing import List, Optional
from core.models import Order
from domain.strategy_base import Strategy

class AlwaysBuyBTC(Strategy):
    """
    Toy strategy that buys a fixed amount every tick.
    """

    def on_data(self, data: dict) -> List[Order]:
        return [
            Order(
                asset="BTC/USDT",
                side=Side.BUY,
                quantity=Decimal("0.001"),
                order_type=OrderType.MARKET
            )
        ]
    
class BuyHold(Strategy):
    """
    Buy and hold strategy — enters once, holds.
    """
    def __init__(self, size_fraction=1.0, leverage=1.0, symbol: str = None, price: Optional[float] = None):
        self.bought = False
        self.size_fraction = Decimal(str(size_fraction))
        self.leverage = leverage
        self.symbol = symbol
        self.limit_price = Decimal(str(price)) if price is not None else None

    def on_data(self, data) -> List[Order]:
        if self.bought:
            return []

        self.bought = True
        price = self.limit_price if self.limit_price else Decimal(data.close)
        balance = self.broker.account_balance

        quantity = self.compute_quantity(
            account_balance=balance,
            price=float(price),
            size_fraction=float(self.size_fraction),
            leverage=float(self.leverage)
        )

        return [Order(
            asset=self.symbol,
            side=Side.BUY,
            quantity=quantity,
            order_type=OrderType.LIMIT if self.limit_price else OrderType.MARKET,
            price=self.limit_price,
            leverage=self.leverage,
            timestamp=data.timestamp,
            client_tag="entry"
        )]


class BuySell(Strategy):
    """
    Buys a % of capital at the first candle, sells at the last candle.
    Supports LIMIT or MARKET entry via `price`.
    """
    def __init__(self, size_fraction=1.0, sl_pct=None, tp_pct=None, leverage=1.0, symbol: str = None, price: Optional[float] = None):
        self.bought = False
        self.sold = False
        self.size_fraction = Decimal(str(size_fraction))
        self.sl_pct = sl_pct
        self.tp_pct = tp_pct
        self.leverage = leverage
        self.symbol = symbol
        self.limit_price = Decimal(str(price)) if price is not None else None

    def on_data(self, data) -> List[Order]:
        if not self.bought:
            self.bought = True

            price = self.limit_price if self.limit_price else Decimal(data.close)
            balance = self.broker.account_balance

            quantity = self.compute_quantity(
                account_balance=balance,
                price=float(price),
                size_fraction=float(self.size_fraction),
                leverage=float(self.leverage)
            )

            sl = self.compute_stop_loss(float(price), self.sl_pct, Side.BUY, self.leverage)
            tp = self.compute_take_profit(float(price), self.tp_pct, Side.BUY, self.leverage)

            return [Order(
                asset=self.symbol,
                side=Side.BUY,
                quantity=quantity,
                order_type=OrderType.LIMIT if self.limit_price else OrderType.MARKET,
                price=self.limit_price,
                stop_price=Decimal(sl) if sl else None,
                take_profit=Decimal(tp) if tp else None,
                leverage=self.leverage,
                timestamp=data.timestamp,
                client_tag="entry"
            )]

        return []

    def finalize(self, snapshot) -> List[Order]:
        if self.bought and not self.sold:
            self.sold = True
            pos = self.broker.get_position(self.symbol)
            if pos:
                return [Order(
                    asset=self.symbol,
                    side=Side.SELL,
                    quantity=pos.quantity,
                    order_type=OrderType.MARKET,
                    timestamp=snapshot.timestamp,
                    leverage=pos.leverage,
                    client_tag="close"
                )]
        return []


class SellBuy(Strategy):
    """
    Shorts a % of capital at the first candle, then buys back (closes) at the last candle (backtest only).
    Supports LIMIT or MARKET entries via `price`.
    """
    def __init__(self, size_fraction=1.0, sl_pct=None, tp_pct=None, leverage=1.0, symbol: str = None, price: Optional[float] = None):
        self.sold = False
        self.covered = False
        self.size_fraction = Decimal(str(size_fraction))
        self.sl_pct = sl_pct
        self.tp_pct = tp_pct
        self.leverage = leverage
        self.symbol = symbol
        self.last_timestamp = None
        self.limit_price = Decimal(str(price)) if price is not None else None

    def on_data(self, data) -> List[Order]:
        self.last_timestamp = data.timestamp

        if not self.sold:
            self.sold = True

            price = self.limit_price if self.limit_price else Decimal(data.close)
            balance = self.broker.account_balance

            quantity = self.compute_quantity(
                account_balance=balance,
                price=float(price),
                size_fraction=float(self.size_fraction),
                leverage=float(self.leverage)
            )

            sl = self.compute_stop_loss(float(price), self.sl_pct, Side.SELL, self.leverage)
            tp = self.compute_take_profit(float(price), self.tp_pct, Side.SELL, self.leverage)

            return [Order(
                asset=self.symbol,
                side=Side.SELL,
                quantity=quantity,
                order_type=OrderType.LIMIT if self.limit_price else OrderType.MARKET,
                price=self.limit_price,  # only set for LIMIT
                stop_price=Decimal(sl) if sl else None,
                take_profit=Decimal(tp) if tp else None,
                leverage=self.leverage,
                timestamp=data.timestamp,
                client_tag="entry"
            )]

        return []

    def finalize(self, snapshot) -> List[Order]:
        if self.sold and not self.covered:
            self.covered = True
            pos = self.broker.positions.get(self.symbol)
            if pos:
                return [Order(
                    asset=self.symbol,
                    side=Side.BUY,
                    quantity=pos.quantity,
                    order_type=OrderType.MARKET,
                    timestamp=snapshot.timestamp,
                    leverage=self.leverage,
                    client_tag="close"
                )]
        return []



