# strategies/macd_strategy.py

import pandas as pd

class MACDStrategy:
    """
    Estrategia MACD (Moving Average Convergence Divergence)
    Señales:
        - Compra: MACD cruza hacia arriba la Signal Line
        - Venta: MACD cruza hacia abajo la Signal Line
    """

    def __init__(self, fast_period=12, slow_period=26, signal_period=9):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def calculate_macd(self, df):
        """Calcula las columnas MACD, Signal y Histogram en el dataframe"""
        df["EMA_fast"] = df["close"].ewm(span=self.fast_period, adjust=False).mean()
        df["EMA_slow"] = df["close"].ewm(span=self.slow_period, adjust=False).mean()
        df["MACD"] = df["EMA_fast"] - df["EMA_slow"]
        df["Signal"] = df["MACD"].ewm(span=self.signal_period, adjust=False).mean()
        df["Hist"] = df["MACD"] - df["Signal"]
        return df

    def generate_signal(self, df: pd.DataFrame) -> str | None:
        """
        Devuelve 'buy', 'sell' o None según el cruce de MACD y Signal.
        """
        df = self.calculate_macd(df)

        if len(df) < 2:
            return None

        prev_macd = df["MACD"].iloc[-2]
        prev_signal = df["Signal"].iloc[-2]
        curr_macd = df["MACD"].iloc[-1]
        curr_signal = df["Signal"].iloc[-1]

        if prev_macd < prev_signal and curr_macd > curr_signal:
            return "buy"
        elif prev_macd > prev_signal and curr_macd < curr_signal:
            return "sell"
        else:
            return None
