# services/bitget_executor.py

import ccxt
from core.models import Order, Trade
from core.enums import OrderStatus, OrderType, Side
from services.executor import OrderExecutor
from decimal import Decimal
from datetime import datetime


class BitgetExecutor(OrderExecutor):
    """
    Executes real orders on Bitget (testnet or live).
    """
    def __init__(self, api_key, api_secret, password=None, testnet=False):
        self.exchange = ccxt.bitget({
            'apiKey': api_key,
            'secret': api_secret,
            'password': password,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'swap'
            }
        })

        if testnet:
            self.exchange.set_sandbox_mode(True)

        self.orders = {}
        self.trades = []
        self.broker = None  # set by LiveEngine

    def submit_order(self, order):
        try:
            symbol = order.asset
            qty = float(order.quantity)

            # Set leverage first
            try:
                self.exchange.set_leverage(int(order.leverage), symbol=symbol)
            except Exception as e:
                print(f"⚠️ Bitget leverage set failed for {symbol}: {e}")

            # Submit entry order
            if order.order_type == OrderType.MARKET:
                side = 'buy' if order.side == Side.BUY else 'sell'
                result = self.exchange.create_market_order(symbol, side, qty)
            elif order.order_type == OrderType.LIMIT:
                if not order.price:
                    raise ValueError("LIMIT order requires price")
                side = 'buy' if order.side == Side.BUY else 'sell'
                result = self.exchange.create_limit_order(symbol, side, qty, float(order.price))
            else:
                raise ValueError(f"Unsupported order type: {order.order_type}")

            order_id = result['id']
            order.timestamp = datetime.utcnow()
            order.status = OrderStatus.PENDING
            self.orders[order_id] = order

            status = result.get("status", "").lower()
            executed_price = result.get("average") or result.get("price")

            if status in ("closed", "filled"):
                order.status = OrderStatus.FILLED
                order.execution_price = Decimal(str(executed_price))

                trade = Trade(
                    order=order,
                    quantity=order.quantity,
                    execution_price=order.execution_price,
                    timestamp=order.timestamp
                )
                self.trades.append(trade)

                print(f"✅ Bitget trade executed: {order.side.name} {order.quantity} {symbol} @ {executed_price}")
            else:
                print(f"🕒 Bitget LIMIT order submitted (pending): {order.side.name} {qty} @ {order.price}")

            # SL/TP brackets
            if order.stop_price:
                try:
                    self.exchange.create_order(
                        symbol=symbol,
                        type='STOP_MARKET',
                        side='sell' if order.side == Side.BUY else 'buy',
                        amount=qty,
                        params={
                            'stopPrice': float(order.stop_price),
                            'closePosition': True
                        }
                    )
                    print(f"📉 Bitget SL placed at {order.stop_price}")
                except Exception as e:
                    print(f"❌ Bitget SL failed:", e)

            if order.take_profit:
                try:
                    self.exchange.create_order(
                        symbol=symbol,
                        type='TAKE_PROFIT_MARKET',
                        side='sell' if order.side == Side.BUY else 'buy',
                        amount=qty,
                        params={
                            'stopPrice': float(order.take_profit),
                            'closePosition': True
                        }
                    )
                    print(f"📈 Bitget TP placed at {order.take_profit}")
                except Exception as e:
                    print(f"❌ Bitget TP failed:", e)

            return trade if order.status == OrderStatus.FILLED else None

        except Exception as e:
            print("❌ Bitget order failed:", e)
            order.status = OrderStatus.REJECTED
            return None

    def cancel_order(self, order_id: str):
        try:
            order = self.orders[order_id]
            symbol = order.asset.replace("/", "")
            self.exchange.cancel_order(order_id, symbol)
            order.status = OrderStatus.CANCELLED
        except Exception as e:
            print(f"[BitgetExecutor] ❌ Cancel failed: {e}")

    def fetch_order_status(self, order_id: str):
        try:
            order = self.orders[order_id]
            symbol = order.asset.replace("/", "")
            data = self.exchange.fetch_order(order_id, symbol)
            return OrderStatus.FILLED if data["status"] == "closed" else OrderStatus.PENDING
        except Exception:
            return None

    def fetch_balance_usdt(self):
        balance = self.exchange.fetch_balance()
        usdt = balance['total'].get('USDT', 0)
        return Decimal(str(usdt))
