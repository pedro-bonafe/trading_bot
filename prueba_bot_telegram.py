import requests

bot_token = "7641663019:AAFLGogNanG8MU111kp7RFyBrEVGp2U9kyM"
chat_id = "7646410082"
mensaje = "✅ Tu bot de trading puede enviar mensajes por Telegram 🎉"

url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
data = {
    "chat_id": chat_id,
    "text": mensaje
}

response = requests.post(url, data=data)
print("Código de estado:", response.status_code)
print("Respuesta:", response.json())
