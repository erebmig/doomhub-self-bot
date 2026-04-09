from flask import Flask, render_template, request, jsonify
import requests
import threading
import time
import random

app = Flask(__name__)

# DoomHub Engine - İşlemleri yöneten beyin
class DoomHubEngine:
    def __init__(self):
        self.current_token = None
        self.user_name = "User"
        self.active_threads = []

    def validate_token(self, token):
        # Token doğruluğunu Discord API üzerinden kontrol eder
        headers = {"Authorization": token}
        r = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
        if r.status_code == 200:
            self.current_token = token
            return True
        return False

    def spam_task(self, url, message, count):
        # Webhook spam işlemini arka planda yapar
        for _ in range(int(count)):
            try:
                requests.post(url, json={"content": message})
                time.sleep(0.1) # Çok hızlı spam için düşük delay
            except:
                break

    def nuke_task(self, guild_id):
        # Sunucudaki kanalları siler (Selfbot yetkisine bağlı)
        headers = {"Authorization": self.current_token}
        r = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/channels", headers=headers)
        if r.status_code == 200:
            for channel in r.json():
                requests.delete(f"https://discord.com/api/v9/channels/{channel['id']}", headers=headers)
                time.sleep(0.5)

engine = DoomHubEngine()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/setup', methods=['POST'])
def setup():
    data = request.json
    name = data.get('name')
    token = data.get('token')

    if engine.validate_token(token):
        engine.user_name = name
        return jsonify({"status": "success", "message": f"Welcome {name}"})
    else:
        return jsonify({"status": "error", "message": "Invalid Token!"}), 401

@app.route('/api/action', methods=['POST'])
def action():
    data = request.json
    action_type = data.get('type')
    
    if action_type == "webhook_spam":
        t = threading.Thread(target=engine.spam_task, args=(data['url'], data['msg'], data['count']))
        t.start()
    
    elif action_type == "nuke":
        t = threading.Thread(target=engine.nuke_task, args=(data['guild_id'],))
        t.start()

    return jsonify({"status": "executed"})

if __name__ == "__main__":
    # Localhost üzerinde 5000 portunda çalışır
    app.run(debug=True, host='0.0.0.0', port=5000)
