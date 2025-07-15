from decider.decider import Decider

class StrategyManager:
    def __init__(self, strategies):
        self.strategies = strategies
        self.last_signal = None
        self.decider = Decider()

    def generate_signals(self, df):
        signals = {}
        for strat in self.strategies:
            try:
                name = strat.__class__.__name__
                signals[name] = strat.generate_signal(df)
            except Exception as e:
                signals[name] = f"⚠️ Error: {e}"
        return signals

    def resolve_signal(self, signals, df):
        # Solo pasamos señales válidas (buy/sell/None) al Decider
        filtered_signals = {
            k: v for k, v in signals.items()
            if v in ["buy", "sell", None]
        }
        return self.decider.decide(filtered_signals, df)

    def should_trade(self, new_signal):
        if new_signal and new_signal != self.last_signal:
            self.last_signal = new_signal
            return True
        return False

    def close_on_signal_change(self, new_signal):
        if new_signal != self.last_signal and self.last_signal is not None:
            from trader import Trader
            print("🔁 Señal cambiada, cerrando posición anterior...")
            Trader().close_positions()
