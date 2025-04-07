# backtest/enriched_snapshot.py
class EnrichedSnapshot:
    def __init__(self, snapshot, indicators: dict):
        self.snapshot = snapshot
        self.indicators = indicators

    def __getattr__(self, item):
        # So we can access snapshot.open etc directly
        return getattr(self.snapshot, item)
