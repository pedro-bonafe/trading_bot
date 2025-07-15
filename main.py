import time
from datetime import datetime, timedelta, timezone, UTC
import os
from dotenv import load_dotenv
import MetaTrader5 as mt5

from mt5_connector import MT5Connector
from data_fetcher import DataFetcher
from trader import Trader

from strategies.ema_crossover import EMACrossoverStrategy
from strategies.rsi_strategy import RSIStrategy
from strategies.macd_strategy import MACDStrategy
from strategies.bollinger_strategy import BollingerStrategy
from strategies.breakout_strategy import BreakoutStrategy
from strategies.adx_strategy import ADXStrategy
from strategies.price_action_strategy import PriceActionStrategy
from strategies.volume_strategy import VolumeStrategy

from strategy_manager import StrategyManager
from logger import TradeLogger
from notifier import Notifier
from signal_manager import SignalManager

# === Cargar variables del archivo .env ===
load_dotenv()

MT5_PATH = os.getenv("MT5_PATH")
MT5_LOGIN = int(os.getenv("MT5_LOGIN"))
MT5_PASSWORD = os.getenv("MT5_PASSWORD")
MT5_SERVER = os.getenv("MT5_SERVER")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# === Función para detectar si es hora de cierre automático (18:00 GMT-3) ===
def es_hora_de_cerrar():
    #ahora_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
    ahora_utc = datetime.now(UTC)
    ahora_local = ahora_utc.astimezone(timezone(timedelta(hours=-3)))
    return ahora_local.hour == 11 and ahora_local.minute < 20


def main():
    # === CONFIGURACIÓN ===
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
    notifier = Notifier(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    signal_mgr = SignalManager(symbol)

    # === Cargar estrategias ===
    strategies = [
        EMACrossoverStrategy(),
        RSIStrategy(),
        MACDStrategy(),
        BollingerStrategy(),
        BreakoutStrategy(),
        ADXStrategy(),
        PriceActionStrategy(),
        VolumeStrategy()
    ]
    strategy_mgr = StrategyManager(strategies)

    print("🚀 Bot iniciado. Escuchando señales cada 5 minutos...\n")
    notifier.send("🚀 Bot iniciado. Escuchando señales cada 5 minutos...")

    while True:
        try:
            # === CIERRE AUTOMÁTICO DIARIO ===
            if es_hora_de_cerrar():
                print("🕔 Hora de cierre automático. Cerrando todas las posiciones...")
                trader.close_positions()
                notifier.send("🔒 Todas las posiciones han sido cerradas (cierre diario).")
                exit(42)

            # === OBTENER DATOS ===
            fetcher = DataFetcher(symbol)
            df = fetcher.get_ohlcv()

            # === EVALUAR ESTRATEGIAS ===
            signals = strategy_mgr.evaluate_signals(df)
            current_signal = strategy_mgr.resolve_signal(signals)

            print("📊 Señales generadas:")
            for name, signal in signals.items():
                print(f"  - {name}: {signal}")
            print(f"🎯 Señal seleccionada: {current_signal}")

            # === CIERRE SI CAMBIA LA SEÑAL ===
            signal_mgr.close_on_signal_change(current_signal)

            # === EJECUTAR ORDEN ===
            if signal_mgr.should_trade(current_signal):
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
                            f"📥 Orden ejecutada:\n{symbol} {current_signal} @ {round(result.price, 5)}\n"
                            f"SL: {round(result.request.sl, 5)} | TP: {round(result.request.tp, 5)}"
                        )
                else:
                    print("⏸ Ya existe una posición abierta.")
            else:
                print("⏳ Sin nueva señal. Esperando siguiente ciclo...")

        except Exception as e:
            print(f"⚠️ Error en el ciclo: {e}")
            notifier.send(f"⚠️ Error en el ciclo del bot:\n{e}")

        time.sleep(intervalo_segundos)


if __name__ == "__main__":
    main()
