import csv
from datetime import datetime
import os

class TradeLogger:
    def __init__(self, filename="trades_log.csv"):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'symbol', 'signal', 'volume', 'price', 'sl', 'tp', 'order_id'])

    def log_trade(self, symbol, signal, volume, price, sl, tp, order_id):
        with open(self.filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                symbol, signal, volume, price, sl, tp, order_id
            ])
        print(f"📝 Trade registrado: {symbol} {signal} @ {price}")
