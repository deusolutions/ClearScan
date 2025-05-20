class Notifier:
    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}/"

    def send_notification(self, chat_id, message):
        url = f"{self.base_url}sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message
        }
        response = requests.post(url, json=payload)
        return response.json()

    def handle_commands(self, update):
        command = update.get('message', {}).get('text', '')
        chat_id = update.get('message', {}).get('chat', {}).get('id', '')
        
        if command == "/start":
            self.send_notification(chat_id, "Welcome to the Hourly Subnet Scanner Bot!")
        elif command == "/status":
            self.send_notification(chat_id, "The scanner is running and will notify you of results.")