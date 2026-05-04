from flask import Flask, send_from_directory
import os
import threading
import subprocess

app = Flask(__name__)

@app.route('/dashboard.html')
def dashboard():
    return send_from_directory('.', 'dashboard.html')

@app.route('/')
def home():
    return send_from_directory('.', 'dashboard.html')

def run_bot():
    subprocess.run(['python', 'telegram_bot.py'])

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)