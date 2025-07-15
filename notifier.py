import requests

class Notifier:
    def __init__(self, bot_token, chat_id):
        self.token = bot_token
        self.chat_id = chat_id

    def send(self, message):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {"chat_id": self.chat_id, "text": message}
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                print("✅ Notificación enviada")
            else:
                print("❌ Error al enviar notificación")
        except Exception as e:
            print("⚠️ Fallo al notificar:", e)
