# services/binance_executor.py

import ccxt
from core.models import Order, Trade
from core.enums import OrderStatus, OrderType, Side
from services.executor import OrderExecutor
from decimal import Decimal
from uuid import uuid4
from datetime import datetime



class BinanceExecutor(OrderExecutor):
    """
    Executes real orders on Binance (testnet or live).
    """
    def __init__(self, api_key, api_secret, testnet=True):
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future'
            }
        })

        if testnet:
            self.exchange.set_sandbox_mode(True)

        self.orders = {}
        self.trades = []
        self.broker = None  # set by LiveEngine or main script


    def submit_order(self, order):
        try:
            symbol = order.asset  # e.g. "BTC/USDT"
            qty = float(order.quantity)

            # ✅ Set leverage before any order
            try:
                self.exchange.set_leverage(int(order.leverage), symbol=symbol)
            except Exception as e:
                print(f"⚠️ Failed to set leverage {order.leverage}x on {symbol}: {e}")

            # ✅ Submit entry order
            if order.order_type == OrderType.MARKET:
                if order.side == Side.BUY:
                    result = self.exchange.create_market_buy_order(symbol, qty)
                elif order.side == Side.SELL:
                    result = self.exchange.create_market_sell_order(symbol, qty)
            elif order.order_type == OrderType.LIMIT:
                if not order.price:
                    raise ValueError("LIMIT order requires price")
                if order.side == Side.BUY:
                    result = self.exchange.create_limit_buy_order(symbol, qty, float(order.price))
                elif order.side == Side.SELL:
                    result = self.exchange.create_limit_sell_order(symbol, qty, float(order.price))
            else:
                raise ValueError(f"Unsupported order type: {order.order_type}")

            order_id = result["id"]
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

                print(f"✅ Trade executed: {order.side.name} {order.quantity} {symbol} @ {executed_price}")
            else:
                print(f"🕒 LIMIT order submitted (not yet filled): {order.side.name} {qty} @ {order.price}")

                # Note: You may implement polling for fill later

            # ✅ Attach SL/TP as bracket orders if needed
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
                    print(f"📉 Stop-loss placed at {order.stop_price}")
                except Exception as e:
                    print(f"❌ Failed to place SL order:", e)

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
                    print(f"📈 Take-profit placed at {order.take_profit}")
                except Exception as e:
                    print(f"❌ Failed to place TP order:", e)

            return trade if order.status == OrderStatus.FILLED else None

        except Exception as e:
            print("❌ Order failed:", e)
            order.status = OrderStatus.REJECTED
            return None

    def cancel_order(self, order_id: str):
        try:
            order = self.orders[order_id]
            symbol = order.asset.replace("/", "")
            self.exchange.cancel_order(order_id, symbol)
            order.status = OrderStatus.CANCELLED
        except Exception as e:
            print(f"[BinanceExecutor] ❌ Cancel failed: {e}")

    def fetch_order_status(self, order_id: str):
        try:
            order = self.orders[order_id]
            symbol = order.asset.replace("/", "")
            data = self.exchange.fetch_order(order_id, symbol)
            return OrderStatus.FILLED if data["status"] == "closed" else OrderStatus.PENDING
        except Exception:
            return None

    def check_exit_triggers(self, snapshot):
        """
        SL/TP logic is not yet implemented here for live — could be added
        by checking open positions + current price
        """
        pass
    
    def fetch_balance_usdt(self):
        balance = self.exchange.fetch_balance()
        usdt = balance['total'].get('USDT', 0)
        return Decimal(str(usdt))
