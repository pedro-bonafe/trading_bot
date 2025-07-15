import pandas as pd

class VolumeStrategy:
    """
    Confirma señales con volumen alto (simplificado).
    """
    def __init__(self, volume_threshold=1.5):
        self.volume_threshold = volume_threshold

    def generate_signal(self, df: pd.DataFrame) -> str | None:
        if len(df) < 2:
            return None

        curr_volume = df.iloc[-1]['volume']
        avg_volume = df['volume'][-20:].mean()

        if curr_volume > avg_volume * self.volume_threshold:
            # Retorna señal 'buy' o 'sell' según tendencia del precio
            if df.iloc[-1]['close'] > df.iloc[-2]['close']:
                return "buy"
            elif df.iloc[-1]['close'] < df.iloc[-2]['close']:
                return "sell"

        return None
