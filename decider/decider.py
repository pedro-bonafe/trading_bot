import pandas as pd
from typing import Optional

class Decider:
    """
    Modelo de decisión que selecciona una señal entre múltiples estrategias,
    basándose en las señales y los datos de mercado (tickers).
    """

    def __init__(self):
        # Aquí podríamos cargar un modelo entrenado en el futuro
        pass

    def decide(self, signal_dict: dict[str, Optional[str]], ticker_data: pd.DataFrame) -> Optional[str]:
        """
        Recibe un diccionario de señales por estrategia y datos OHLCV+.

        Por ahora, implementa una lógica simple de votación por mayoría entre BUY y SELL.

        :param signal_dict: dict con señales por estrategia (ej: {'EMA': 'buy', 'RSI': 'sell', ...})
        :param ticker_data: pd.DataFrame con columnas: ['time', 'open', 'high', 'low', 'close', 'volume', ...]
        :return: 'buy', 'sell' o None
        """
        buy_votes = sum(1 for s in signal_dict.values() if s == "buy")
        sell_votes = sum(1 for s in signal_dict.values() if s == "sell")

        if buy_votes > sell_votes:
            return "buy"
        elif sell_votes > buy_votes:
            return "sell"
        else:
            return None
