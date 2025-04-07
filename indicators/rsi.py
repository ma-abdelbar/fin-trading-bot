# indicators/rsi.py
from indicators.indicator_base import Indicator
from collections import deque

class RSIIndicator(Indicator):
    def __init__(self, period=14):
        self.period = period
        self.closes = deque(maxlen=period + 1)
        self.timestamps = []
        self.values = []
        self.rsi = None

    def update(self, snapshot):
        self.closes.append(float(snapshot.close))
        if len(self.closes) < self.period + 1:
            return

        deltas = [self.closes[i+1] - self.closes[i] for i in range(len(self.closes) - 1)]
        gains = [max(d, 0) for d in deltas[-self.period:]]
        losses = [max(-d, 0) for d in deltas[-self.period:]]

        avg_gain = sum(gains) / self.period
        avg_loss = sum(losses) / self.period or 1e-10

        rs = avg_gain / avg_loss
        self.rsi = 100 - (100 / (1 + rs))
        self.timestamps.append(snapshot.timestamp)
        self.values.append(self.rsi)

    def get(self):
        return self.rsi
    
    def get_series(self):
        return self.timestamps, self.values
