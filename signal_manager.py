import MetaTrader5 as mt5

class SignalManager:
    def __init__(self, symbol):
        self.symbol = symbol
        self.last_signal = None

    def should_trade(self, current_signal):
        if current_signal and current_signal != self.last_signal:
            print(f"🔄 Señal nueva: {current_signal} (anterior: {self.last_signal})")
            self.last_signal = current_signal
            return True
        return False

    def close_on_signal_change(self, current_signal):
        if not current_signal:
            return
        positions = mt5.positions_get(symbol=self.symbol)
        if positions:
            for pos in positions:
                if (pos.type == mt5.ORDER_TYPE_BUY and current_signal == 'SELL') or \
                   (pos.type == mt5.ORDER_TYPE_SELL and current_signal == 'BUY'):
                    print("❌ Señal contraria → cerrando posición actual")
                    from trader import Trader
                    trader = Trader(self.symbol)
                    trader.close_positions()
