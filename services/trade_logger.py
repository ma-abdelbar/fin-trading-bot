from decimal import Decimal
from services.broker import Broker
from core.models import Trade
from core.enums import Side

class TradeLogger:
    def __init__(self):
        pass

    def log_trade(self, trade: Trade, broker: Broker):
        order = trade.order
        symbol = order.asset
        side = order.side.name
        qty = round(trade.quantity, 4)
        price = round(trade.execution_price, 2)
        ts = trade.timestamp

        # Retrieve current margin and leverage
        pos = broker.get_position(symbol)
        margin = round(pos.margin, 2) if pos else 0
        leverage = order.leverage or 1
        balance = round(broker.account_balance, 2)

        # SL/TP/Tag extra info
        extra_info = ""
        if order.stop_price:
            extra_info += f" SL: {round(order.stop_price, 2)}"
        if order.take_profit:
            extra_info += f" TP: {round(order.take_profit, 2)}"
        if order.client_tag:
            extra_info += f" Tag: {order.client_tag}"

        print(
            f"🕒 {ts} | 💼 Trade Executed: {side} {qty} {symbol} @ {price}"
            f" | Margin: {margin:.2f} | {leverage}x | Balance: {balance:.2f}"
            f"{extra_info} Type: {order.order_type.name}"
        )

    def log_close_position(self, symbol, pnl: Decimal, margin_released=None, timestamp=None):
        direction = "📈" if pnl > 0 else "📉"
        margin_str = f" | Margin Released: {margin_released:.2f}" if margin_released else ""
        ts = timestamp or "🕒"
        print(f"{ts} | 🔁 Position Closed: {symbol} | Realized PnL: {direction} {pnl:+.2f}{margin_str}")

    def log_start(self, starting_cash):
        print(f"🚀 Starting backtest with initial balance: {starting_cash:.2f}")

    def log_end(self, broker: Broker):
        margin = round(broker.get_total_margin(), 2)
        balance = round(broker.account_balance, 2)
        print(f"\n🏁 Final Account State | Balance: {balance:.2f} | Margin Used: {margin:.2f}")
