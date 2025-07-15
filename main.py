import time
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
import MetaTrader5 as mt5

from mt5_connector import MT5Connector
from data_fetcher import DataFetcher
from trader import Trader
from logger import TradeLogger
from notifier import Notifier
from strategy_manager import StrategyManager

# === Cargar credenciales ===
load_dotenv()
MT5_PATH = os.getenv("MT5_PATH")
MT5_LOGIN = int(os.getenv("MT5_LOGIN"))
MT5_PASSWORD = os.getenv("MT5_PASSWORD")
MT5_SERVER = os.getenv("MT5_SERVER")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# === Cierre diario automático a las 17:00 GMT-3 ===
def es_hora_de_cerrar():
    ahora_utc = datetime.now(timezone.utc)
    ahora_local = ahora_utc.astimezone(timezone(timedelta(hours=-3)))
    return ahora_local.hour == 17 and ahora_local.minute < 20

def main():
    # === CONFIGURACIÓN GENERAL ===
    symbol = "USDCAD"
    capital = 1000
    risk_pct = 1
    sl_pips = 30
    tp_pips = 60
    intervalo_segundos = 300  # 5 minutos

    # === INICIALIZACIÓN ===
    connector = MT5Connector(MT5_PATH, MT5_LOGIN, MT5_PASSWORD, MT5_SERVER)
    connector.connect()

    trader = Trader(symbol)
    logger = TradeLogger()
    notifier = Notifier(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)  # 🔕 Descomentar si querés usarlo

    from strategies.ema_crossover import EMACrossoverStrategy
    from strategies.rsi_strategy import RSIStrategy
    from strategies.macd_strategy import MACDStrategy
    from strategies.bollinger_strategy import BollingerStrategy
    from strategies.adx_strategy import ADXStrategy
    from strategies.breakout_strategy import BreakoutStrategy
    from strategies.price_action_strategy import PriceActionStrategy
    from strategies.volume_strategy import VolumeStrategy

    strategies = [
        EMACrossoverStrategy(),
        RSIStrategy(),
        MACDStrategy(),
        BollingerStrategy(),
        ADXStrategy(),
        BreakoutStrategy(),
        PriceActionStrategy(),
        VolumeStrategy()
    ]

    strategy_mgr = StrategyManager(strategies)

    print("🚀 Bot iniciado. Escuchando señales cada 5 minutos...\n")
    notifier.send("🚀 Bot iniciado. Escuchando señales cada 5 minutos...\n")

    while True:
        try:
            if es_hora_de_cerrar():
                print("🕔 Hora de cierre automático. Cerrando posiciones...")
                trader.close_positions()
                notifier.send("🔒 Posiciones cerradas (cierre diario).")
                exit(42)

            # === Obtener datos ===
            fetcher = DataFetcher(symbol)
            df = fetcher.get_ohlcv()
            print("📋 Columnas del dataframe:", df.columns.tolist())

            # === Generar señales ===
            signals = strategy_mgr.generate_signals(df)
            print(f"📊 Señales generadas:")
            for strat, sig in signals.items():
                print(f"  - {strat}: {sig}")

            # === Resolver mejor señal con Decider ===
            current_signal = strategy_mgr.resolve_signal(signals, df)
            print(f"🎯 Señal seleccionada: {current_signal}")

            # === Cerrar posiciones si cambia la señal ===
            strategy_mgr.close_on_signal_change(current_signal)

            # === Ejecutar orden si corresponde ===
            if strategy_mgr.should_trade(current_signal):
                posiciones_abiertas = mt5.positions_get(symbol=symbol)
                if not posiciones_abiertas:
                    vol = trader.calculate_volume(capital, risk_pct, sl_pips)
                    result = trader.send_order(current_signal, vol, sl_pips, tp_pips)
                    if result:
                        logger.log_trade(
                            symbol, current_signal, vol, result.price,
                            result.request.sl, result.request.tp, result.order
                        )
                        notifier.send(
                            f"📥 Orden ejecutada:\n{symbol} {current_signal.upper()} @ {round(result.price, 5)}\n"
                            f"SL: {round(result.request.sl, 5)} | TP: {round(result.request.tp, 5)}"
                        )
                else:
                    print("⏸ Ya hay una posición abierta.")
            else:
                print("⏳ Sin nueva señal. Esperando siguiente ciclo...")

        except Exception as e:
            print(f"⚠️ Error en el ciclo: {e}")
            notifier.send(f"⚠️ Error en el ciclo del bot:\n{e}")

        time.sleep(intervalo_segundos)


if __name__ == "__main__":
    main()
