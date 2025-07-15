import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from strategies.ema_crossover import EMACrossoverStrategy
from strategies.rsi_strategy import RSIStrategy

# === Parámetros ===
SYMBOL = "USDCAD"
TIMEFRAME = mt5.TIMEFRAME_D1
START_DATE = datetime(2019, 1, 1)
END_DATE = datetime(2023, 12, 31)
TP_PIPS = 60
SL_PIPS = 30
RAW_DATA_PATH = "data/raw_data/usdcad_ohlcv.csv"
LABELED_DATA_PATH = "data/labeled_data/training_data.csv"


def init_mt5():
    if not mt5.initialize():
        raise RuntimeError("MT5 no pudo inicializarse")


def fetch_raw_data():
    rates = mt5.copy_rates_range(SYMBOL, TIMEFRAME, START_DATE, END_DATE)
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df.to_csv(RAW_DATA_PATH, index=False)
    return df


def compute_indicators(df):
    df["ema_fast"] = df["close"].ewm(span=10).mean()
    df["ema_slow"] = df["close"].ewm(span=30).mean()
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))
    return df


def generate_signals(df):
    ema = EMACrossoverStrategy()
    rsi = RSIStrategy()
    signals = []

    for i in range(len(df)):
        sub = df.iloc[:i+1]
        ema_signal = ema.generate_signal(sub)
        rsi_signal = rsi.generate_signal(sub)
        signals.append({
            "ema_signal": ema_signal or "none",
            "rsi_signal": rsi_signal or "none"
        })

    return pd.DataFrame(signals)


def generate_labels(df):
    labels = []

    for i in range(len(df) - 5):
        row = df.iloc[i]
        future = df.iloc[i+1:i+6]
        buy_profit = max(future["high"] - row["close"]) * 10000
        sell_profit = max(row["close"] - future["low"]) * 10000

        if buy_profit >= TP_PIPS:
            labels.append("buy")
        elif sell_profit >= TP_PIPS:
            labels.append("sell")
        else:
            labels.append("none")

    labels.extend(["none"] * 5)
    return labels


def main():
    init_mt5()
    df = fetch_raw_data()
    df = compute_indicators(df)
    signal_df = generate_signals(df)
    label_series = generate_labels(df)

    df = df.reset_index(drop=True).join(signal_df)
    df["label"] = label_series
    df.to_csv(LABELED_DATA_PATH, index=False)

    print(f"✅ Datos crudos guardados en: {RAW_DATA_PATH}")
    print(f"✅ Dataset etiquetado guardado en: {LABELED_DATA_PATH}")


if __name__ == "__main__":
    main()