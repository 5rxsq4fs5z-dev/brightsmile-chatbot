from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route('/dashboard.html')
def dashboard():
    return send_from_directory('.', 'dashboard.html')

@app.route('/')
def home():
    return send_from_directory('.', 'dashboard.html')

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)