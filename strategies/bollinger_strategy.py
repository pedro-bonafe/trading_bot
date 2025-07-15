import pandas as pd

class BollingerStrategy:
    """
    Estrategia basada en Bandas de Bollinger
    Señales:
        - Compra: cierre por debajo de la banda inferior
        - Venta: cierre por encima de la banda superior
    """

    def __init__(self, period=20, std_dev=2):
        self.period = period
        self.std_dev = std_dev

    def calculate_bollinger_bands(self, df):
        """Calcula las bandas de Bollinger"""
        df["SMA"] = df["close"].rolling(window=self.period).mean()
        df["STD"] = df["close"].rolling(window=self.period).std()
        df["Upper"] = df["SMA"] + (self.std_dev * df["STD"])
        df["Lower"] = df["SMA"] - (self.std_dev * df["STD"])
        return df

    def generate_signal(self, df: pd.DataFrame) -> str | None:
        """
        Devuelve 'buy', 'sell' o None si no hay señal.
        """
        df = self.calculate_bollinger_bands(df)

        if len(df) < 2:
            return None

        close_price = df["close"].iloc[-1]
        lower_band = df["Lower"].iloc[-1]
        upper_band = df["Upper"].iloc[-1]

        if close_price < lower_band:
            return "buy"
        elif close_price > upper_band:
            return "sell"
        else:
            return None
