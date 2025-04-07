from abc import ABC, abstractmethod
from core.models import Order

class OrderExecutor(ABC):
    """
    Interface for executing orders on any broker/exchange.

    All concrete executors (e.g., BinanceExecutor, MockExecutor)
    must implement this interface.
    """

    @abstractmethod
    def submit_order(self, order: Order):
        """
        Submit an order to the broker/exchange.
        """
        pass

    @abstractmethod
    def cancel_order(self, order_id: str):
        """
        Attempt to cancel an existing order.
        """
        pass

    @abstractmethod
    def fetch_order_status(self, order_id: str):
        """
        Check current status of a previously submitted order.
        """
        pass
