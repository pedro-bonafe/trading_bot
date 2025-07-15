import MetaTrader5 as mt5
import pandas as pd

class DataFetcher:
    def __init__(self, symbol, timeframe=mt5.TIMEFRAME_M5, bars=300):
        self.symbol = symbol
        self.timeframe = timeframe
        self.bars = bars

    def get_ohlcv(self):
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, self.bars)
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df = df.rename(columns={
            'tick_volume': 'volume'
        })
        print("📋 Columnas del dataframe:", df.columns.tolist())
        return df
