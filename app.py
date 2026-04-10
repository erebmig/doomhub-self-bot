import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Senin Cloudflare Worker linkin (Sonuna /proxy ekledim)
WORKER_URL = "https://long-sound-d421.boorapolat.workers.dev/proxy"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/setup', methods=['POST'])
def setup():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Veri alınamadı"}), 400
            
        token = data.get('token', '').strip().strip('"').strip("'")
        
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }

        # İsteği senin Worker üzerinden Discord'a tünelliyoruz
        target_url = f"{WORKER_URL}/users/@me"
        r = requests.get(target_url, headers=headers, timeout=15)
        
        print(f"[DEBUG] Worker Status: {r.status_code}", flush=True)

        if r.status_code == 200:
            return jsonify({"status": "success"})
        elif r.status_code == 401:
            return jsonify({"status": "error", "message": "Discord Token'ı reddetti (401)"}), 401
        elif r.status_code == 429:
            return jsonify({"status": "error", "message": "Hız sınırı! Biraz bekle."}), 429
        else:
            return jsonify({"status": "error", "message": f"Discord Hatası: {r.status_code}"}), r.status_code

    except Exception as e:
        print(f"[HATA] {str(e)}", flush=True)
        return jsonify({"status": "error", "message": "Sunucu tarafında hata oluştu"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
