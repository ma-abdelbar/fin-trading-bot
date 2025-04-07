# indicators/indicator_base.py
from abc import ABC, abstractmethod

class Indicator(ABC):
    @abstractmethod
    def update(self, snapshot) -> None:
        pass

    @abstractmethod
    def get(self):
        pass

    def get_series(self):
        """
        Optional: return full time-aligned series for plotting.
        Should return a tuple: (timestamps, values)
        """
        return None
