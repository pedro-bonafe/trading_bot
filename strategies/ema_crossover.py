class EMACrossoverStrategy:
    def __init__(self, fast=12, slow=26):
        self.fast = fast
        self.slow = slow

    def generate_signal(self, df):
        df['ema_fast'] = df['close'].ewm(span=self.fast, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=self.slow, adjust=False).mean()

        df['prev_fast'] = df['ema_fast'].shift(1)
        df['prev_slow'] = df['ema_slow'].shift(1)

        last = df.iloc[-1]
        if last['prev_fast'] < last['prev_slow'] and last['ema_fast'] > last['ema_slow']:
            return 'BUY'
        elif last['prev_fast'] > last['prev_slow'] and last['ema_fast'] < last['ema_slow']:
            return 'SELL'
        return None
