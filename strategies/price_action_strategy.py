import pandas as pd

class PriceActionStrategy:
    """
    Detecta patrón de vela envolvente simple.
    """
    def generate_signal(self, df: pd.DataFrame) -> str | None:
        if len(df) < 2:
            return None

        prev = df.iloc[-2]
        curr = df.iloc[-1]

        # Vela envolvente alcista: cuerpo actual envuelve cuerpo anterior y cierra arriba
        if curr['close'] > curr['open'] and prev['close'] < prev['open'] \
            and curr['open'] < prev['close'] and curr['close'] > prev['open']:
            return "buy"

        # Vela envolvente bajista
        if curr['close'] < curr['open'] and prev['close'] > prev['open'] \
            and curr['open'] > prev['close'] and curr['close'] < prev['open']:
            return "sell"

        return None
