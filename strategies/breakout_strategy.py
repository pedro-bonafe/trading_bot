import pandas as pd

class BreakoutStrategy:
    """
    Detecta rupturas de rango basado en max y min de últimas N velas.
    """
    def __init__(self, period=20):
        self.period = period

    def generate_signal(self, df: pd.DataFrame) -> str | None:
        if len(df) < self.period + 1:
            return None

        recent = df[-self.period-1:-1]
        max_range = recent['high'].max()
        min_range = recent['low'].min()

        last_close = df.iloc[-1]['close']

        if last_close > max_range:
            return "buy"
        elif last_close < min_range:
            return "sell"
        else:
            return None
