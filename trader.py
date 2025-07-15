import MetaTrader5 as mt5

class Trader:
    def __init__(self, symbol):
        self.symbol = symbol
        self.symbol_info = mt5.symbol_info(symbol)

    def calculate_volume(self, capital, risk_pct, sl_pips):
        point = self.symbol_info.point
        contract = self.symbol_info.trade_contract_size
        pip_value = contract * point
        risk = capital * risk_pct / 100
        volume = risk / (sl_pips * pip_value)
        return round(volume, 2)

    def send_order(self, direction, volume, sl_pips, tp_pips):
        tick = mt5.symbol_info_tick(self.symbol)
        price = tick.ask if direction == 'BUY' else tick.bid
        point = self.symbol_info.point

        sl = price - sl_pips * point if direction == 'BUY' else price + sl_pips * point
        tp = price + tp_pips * point if direction == 'BUY' else price - tp_pips * point
        order_type = mt5.ORDER_TYPE_BUY if direction == 'BUY' else mt5.ORDER_TYPE_SELL

        for mode in [mt5.ORDER_FILLING_RETURN, mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_FOK]:
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": volume,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mode
            }
            result = mt5.order_send(request)
            if result.retcode in [mt5.TRADE_RETCODE_DONE, mt5.TRADE_RETCODE_PLACED]:
                print(f"✅ Orden enviada ({direction}) con SL/TP")
                return result
            else:
                print(f"❌ Error modo {mode} - {result.retcode} | {result.comment}")
        return None

    def close_positions(self):
        positions = mt5.positions_get(symbol=self.symbol)
        for pos in positions:
            opposite_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
            tick = mt5.symbol_info_tick(pos.symbol)
            price = tick.bid if opposite_type == mt5.ORDER_TYPE_SELL else tick.ask

            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": pos.ticket,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": opposite_type,
                "price": price,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK
            }
            result = mt5.order_send(close_request)
            print(f"🔁 Cierre {pos.symbol} - Retcode: {result.retcode}")
