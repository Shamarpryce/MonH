from flask import Flask  # type: ignore
from threading import Thread

app = Flask(__name__)  # use __name__ instead of '/'

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True  # optional but good to let thread exit on main exit
    t.start()
