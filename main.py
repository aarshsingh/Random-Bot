import telebot
import os
import requests
import time
from flask import Flask

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN", "7692429836:AAHyUFP6os1A3Hirisl5TV1O5kArGAlAEuQ")
CHAT = os.environ.get("CHATID", "your_default_chat_id_here")
bot = telebot.TeleBot(TOKEN)

headersList = {
    "authority": "pr0gramm.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "dnt": "1",
    "pragma": "no-cache",
    "referer": "https://pr0gramm.com/",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Linux",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
}

def check_valid_id(id):
    resp = requests.get(f"https://pr0gramm.com/api/items/get?id={id}", headers=headersList).json()
    return "error" not in resp

def get_latest_id():
    resp = requests.get("https://pr0gramm.com/api/items/get", headers=headersList).json()
    return resp["items"][0]["id"]

def get_file(id):
    maintxt = "https://img.pr0gramm.com/"
    resp = requests.get(f"https://pr0gramm.com/api/items/get?id={id}", headers=headersList).json()
    try:
        imgname = resp["items"][0]["image"]
    except (IndexError, KeyError):
        return None, None
    url = maintxt + imgname
    filename = url.split("/")[-1]
    result = requests.get(url)
    return result.content, filename

@app.route('/')
def index():
    return "Bot is running."

def main():
    id = get_latest_id()
    while True:
        content, file = get_file(id)
        if file:
            print(f"Processing ID: {id}")
            with open(file, "wb") as temp:
                temp.write(content)
            if file.endswith((".jpg", ".png")):
                bot.send_photo(CHAT, open(file, "rb"))
            else:
                bot.send_video(CHAT, open(file, "rb"))
            os.remove(file)
        time.sleep(5)
        id = str(int(id) + 1)
        while not check_valid_id(id):
            time.sleep(5)

if __name__ == "__main__":
    from threading import Thread
    # Start the bot's polling method in a separate thread
    bot_thread = Thread(target=bot.infinity_polling, kwargs={'timeout': 10, 'long_polling_timeout': 5})
    bot_thread.start()
    # Start the Flask app to expose port 8080
    app.run(host='0.0.0.0', port=8080)
