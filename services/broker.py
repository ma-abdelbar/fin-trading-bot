from decimal import Decimal
from typing import Dict
from collections import defaultdict
from core.models import Order, Trade, Position
from core.enums import Side
from services.executor import OrderExecutor

class Broker:
    """
    Manages portfolio state, submits orders through an executor,
    and tracks positions and cash.
    """

    def __init__(self, account_balance: Decimal, logger=None):
        self.account_balance = account_balance  # Realized PnL rolls into this
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.logger = logger
        self.last_price = None


    def submit_order(self, order: Order) -> str:
        """
        Submit an order via the executor.
        """
        order_id = self.executor.submit_order(order)
        return order_id
    

    def record_trade(self, trade: Trade):
        self.trades.append(trade)
        order = trade.order
        symbol = order.asset
        qty = trade.quantity
        price = trade.execution_price
        side = order.side

        pos = self.positions.get(symbol)

        # --- Opening new position ---
        if not pos:
            exposure = qty * price
            leverage = order.leverage or Decimal("1")
            margin_required = exposure / leverage

            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=qty,
                average_entry_price=price,
                side=side,
                leverage=leverage,
                margin=margin_required,
                stop_loss=order.stop_price,
                take_profit=order.take_profit
            )
            return

        # --- Scaling into existing position ---
        if pos.side == side:
            total_qty = pos.quantity + qty
            new_avg_price = ((pos.quantity * pos.average_entry_price) + (qty * price)) / total_qty
            new_exposure = total_qty * price
            new_margin = new_exposure / pos.leverage

            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=total_qty,
                average_entry_price=new_avg_price,
                side=side,
                leverage=pos.leverage,
                margin=new_margin,
                stop_loss=pos.stop_loss,
                take_profit=pos.take_profit
            )
            return

        # --- Closing or flipping (opposite side) ---
        closing_qty = min(pos.quantity, qty)
        remaining_qty = abs(pos.quantity - qty)

        if pos.side == Side.BUY:
            pnl = (price - pos.average_entry_price) * closing_qty
        else:
            pnl = (pos.average_entry_price - price) * closing_qty

        self.account_balance += pnl
        margin_released = (closing_qty / pos.quantity) * pos.margin

        # Equity = balance right after PnL is realized (no unrealized PnL at this point)
        if self.logger:
            equity = round(self.account_balance, 2)
            self.logger.log_close_position(
                symbol,
                pnl,
                margin_released=round(margin_released, 2),
                timestamp=trade.timestamp
            )

        if qty > pos.quantity:
            # Flip to new position
            new_exposure = remaining_qty * price
            new_margin = new_exposure / (order.leverage or Decimal("1"))

            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=remaining_qty,
                average_entry_price=price,
                side=side,
                leverage=order.leverage,
                margin=new_margin,
                stop_loss=order.stop_price,
                take_profit=order.take_profit
            )

        elif qty < pos.quantity:
            # Partial close
            remaining_margin = pos.margin * (remaining_qty / pos.quantity)

            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=remaining_qty,
                average_entry_price=pos.average_entry_price,
                side=pos.side,
                leverage=pos.leverage,
                margin=remaining_margin,
                stop_loss=pos.stop_loss,
                take_profit=pos.take_profit
            )

        else:
            # Full close
            del self.positions[symbol]



    def get_position(self, symbol: str) -> Position:
        """
        Return the current position for a symbol, if any.
        """
        return self.positions.get(symbol)
    
    
    def get_total_margin(self) -> Decimal:
        return sum((pos.margin for pos in self.positions.values()), Decimal("0"))



    def print_status(self):
        """
        Debug print for cash and current positions.
        """
        print(f"💰 Cash: {self.cash}")
        print(f"📈 Positions:")

        total_position_value = Decimal("0")
        for symbol, pos in self.positions.items():
            market_price = Decimal(getattr(self, "last_price", pos.average_entry_price))
            position_value = pos.quantity * market_price
            total_position_value += position_value

            print(f"  {symbol}: {pos.quantity} @ {pos.average_entry_price}  "
                f"→ Value: {position_value:.2f} USDT")

        print(f"📊 Total Account Value: {self.account_balance:.2f}")
    
