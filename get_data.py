import MetaTrader5 as mt5

class MT5Connector:
    def __init__(self, path, login, password, server):
        self.path = path
        self.login = login
        self.password = password
        self.server = server

    def connect(self):
        if not mt5.initialize(path=self.path, login=self.login, password=self.password, server=self.server):
            raise ConnectionError("❌ Error conectando a MetaTrader 5")
        print("✅ Conexión establecida con MT5")

    def shutdown(self):
        mt5.shutdown()
        print("🔌 Conexión cerrada")
