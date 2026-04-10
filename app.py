"""
DoomHub - Production Discord Automation Tool
© 2026 DoomHub and Tader - All Rights Reserved
"""

import os
import json
import random
import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, request, jsonify, render_template
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ============================================================================
# CONFIGURATION & LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - DOOMHUB - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class ProxyState:
    """Track proxy health and cooldown status"""
    url: str
    fail_count: int = 0
    last_fail: Optional[datetime] = None
    cooldown_until: Optional[datetime] = None
    success_count: int = 0
    
    def is_available(self) -> bool:
        if self.cooldown_until and datetime.now() < self.cooldown_until:
            return False
        return True
    
    def mark_failure(self):
        self.fail_count += 1
        self.last_fail = datetime.now()
        if self.fail_count >= 2:
            self.cooldown_until = datetime.now() + timedelta(seconds=30)
    
    def mark_success(self):
        self.success_count += 1
        self.fail_count = max(0, self.fail_count - 1)
    
    def reset(self):
        self.fail_count = 0
        self.cooldown_until = None

@dataclass
class KampTask:
    """Spammer task configuration"""
    id: str
    token: str
    channel_id: str
    message: str
    count: int
    delay: float
    running: bool = False
    sent_count: int = 0
    failed_count: int = 0

# ============================================================================
# PROXY MANAGEMENT
# ============================================================================

class ProxyRotator:
    """Advanced proxy rotation with authentication and health tracking"""
    
    def __init__(self):
        self.proxies: List[ProxyState] = []
        self.lock = threading.RLock()
        self.session = self._create_session()
        self._load_proxies()
    
    def _create_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=0,
            connect=0,
            read=0,
            redirect=0,
            status=0,
            backoff_factor=0.1
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=20)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    def _load_proxies(self):
        """Load premium proxies from environment"""
        proxy_list_str = os.environ.get('PREMIUM_PROXIES', '')
        proxy_user = os.environ.get('PROXY_USER', '')
        proxy_pass = os.environ.get('PROXY_PASS', '')
        
        if proxy_list_str:
            for proxy in proxy_list_str.split(','):
                proxy = proxy.strip()
                if proxy:
                    if proxy_user and proxy_pass and '@' not in proxy:
                        proxy_url = f"http://{proxy_user}:{proxy_pass}@{proxy}"
                    else:
                        proxy_url = f"http://{proxy}"
                    self.proxies.append(ProxyState(url=proxy_url))
        
        if not self.proxies:
            fallback = os.environ.get('FALLBACK_PROXY', '')
            if fallback:
                self.proxies.append(ProxyState(url=f"http://{fallback}"))
    
    def get_random_proxy(self) -> Optional[str]:
        """Get a random healthy proxy"""
        with self.lock:
            available = [p for p in self.proxies if p.is_available()]
            if not available:
                for p in self.proxies:
                    p.reset()
                available = self.proxies
            
            if available:
                proxy = random.choice(available)
                return proxy.url
        
        return None
    
    def mark_failure(self, proxy_url: str):
        with self.lock:
            for p in self.proxies:
                if p.url == proxy_url:
                    p.mark_failure()
                    break
    
    def mark_success(self, proxy_url: str):
        with self.lock:
            for p in self.proxies:
                if p.url == proxy_url:
                    p.mark_success()
                    break
    
    def get_proxies_dict(self, proxy_url: str) -> Dict[str, str]:
        return {'http': proxy_url, 'https': proxy_url}
    
    def get_available_count(self) -> int:
        with self.lock:
            return len([p for p in self.proxies if p.is_available()])

# ============================================================================
# DISCORD API CLIENT
# ============================================================================

class DiscordClient:
    """High-performance Discord API client with proxy rotation"""
    
    DISCORD_API = "https://discord.com/api/v9"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    def __init__(self, proxy_rotator: ProxyRotator):
        self.proxy_rotator = proxy_rotator
        self.session = self.proxy_rotator.session
    
    def _get_headers(self, token: str) -> Dict[str, str]:
        return {
            'Authorization': token.strip(),
            'Content-Type': 'application/json',
            'User-Agent': self.USER_AGENT,
            'Origin': 'https://discord.com',
            'Referer': 'https://discord.com/channels/@me'
        }
    
    def validate_token(self, token: str, max_attempts: int = 3) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate token with automatic proxy rotation on failure"""
        token = token.strip()
        
        for _ in range(max_attempts):
            proxy_url = self.proxy_rotator.get_random_proxy()
            if not proxy_url:
                return False, None, "No proxies available"
            
            proxies = self.proxy_rotator.get_proxies_dict(proxy_url)
            
            try:
                response = self.session.get(
                    f"{self.DISCORD_API}/users/@me",
                    headers=self._get_headers(token),
                    proxies=proxies,
                    timeout=8
                )
                
                if response.status_code == 200:
                    data = response.json()
                    username = f"{data.get('username')}#{data.get('discriminator', '0')}"
                    self.proxy_rotator.mark_success(proxy_url)
                    return True, username, None
                
                elif response.status_code == 401:
                    return False, None, "Invalid token"
                
                elif response.status_code == 429:
                    retry_after = response.json().get('retry_after', 5)
                    self.proxy_rotator.mark_failure(proxy_url)
                    time.sleep(min(retry_after, 3))
                    continue
                
                else:
                    self.proxy_rotator.mark_failure(proxy_url)
                    continue
                    
            except (requests.exceptions.ConnectTimeout, 
                    requests.exceptions.ReadTimeout,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.ProxyError):
                self.proxy_rotator.mark_failure(proxy_url)
                continue
            except Exception:
                self.proxy_rotator.mark_failure(proxy_url)
                continue
        
        return False, None, "Validation failed after multiple attempts"
    
    def send_message(self, token: str, channel_id: str, message: str, 
                     auto_delete: bool = True) -> Tuple[bool, Optional[str], Optional[str]]:
        """Send message with automatic retry and proxy rotation"""
        token = token.strip()
        channel_id = channel_id.strip()
        
        for _ in range(3):
            proxy_url = self.proxy_rotator.get_random_proxy()
            if not proxy_url:
                continue
            
            proxies = self.proxy_rotator.get_proxies_dict(proxy_url)
            
            try:
                payload = {'content': message}
                response = self.session.post(
                    f"{self.DISCORD_API}/channels/{channel_id}/messages",
                    headers=self._get_headers(token),
                    json=payload,
                    proxies=proxies,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    message_id = data.get('id')
                    self.proxy_rotator.mark_success(proxy_url)
                    
                    if auto_delete and message_id:
                        time.sleep(1.5)
                        self._delete_message(token, channel_id, message_id, proxy_url)
                    
                    return True, message_id, None
                
                elif response.status_code == 429:
                    retry_after = response.json().get('retry_after', 5)
                    self.proxy_rotator.mark_failure(proxy_url)
                    time.sleep(min(retry_after, 2))
                    continue
                
                elif response.status_code == 403:
                    return False, None, "Missing permissions"
                
                elif response.status_code == 401:
                    return False, None, "Invalid token"
                
                else:
                    self.proxy_rotator.mark_failure(proxy_url)
                    continue
                    
            except Exception:
                self.proxy_rotator.mark_failure(proxy_url)
                continue
        
        return False, None, "Failed to send message"
    
    def _delete_message(self, token: str, channel_id: str, message_id: str, proxy_url: str):
        """Silently delete a message"""
        try:
            proxies = self.proxy_rotator.get_proxies_dict(proxy_url)
            self.session.delete(
                f"{self.DISCORD_API}/channels/{channel_id}/messages/{message_id}",
                headers=self._get_headers(token),
                proxies=proxies,
                timeout=5
            )
        except:
            pass

# ============================================================================
# KAMP SPAMMER ENGINE
# ============================================================================

class KampEngine:
    """Multi-instance spammer with anti-ban jitter"""
    
    def __init__(self, discord_client: DiscordClient):
        self.discord_client = discord_client
        self.tasks: Dict[str, KampTask] = {}
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="Kamp")
        self.lock = threading.RLock()
    
    def create_task(self, token: str, channel_id: str, message: str, 
                    count: int, delay: float) -> str:
        """Create and start a new kamp task"""
        task_id = f"kamp_{int(time.time() * 1000)}"
        
        task = KampTask(
            id=task_id,
            token=token,
            channel_id=channel_id,
            message=message,
            count=min(count, 100),
            delay=max(delay, 1.0)
        )
        
        with self.lock:
            self.tasks[task_id] = task
        
        task.running = True
        self.executor.submit(self._run_task, task_id)
        
        return task_id
    
    def _run_task(self, task_id: str):
        """Execute kamp task with jitter"""
        with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                return
        
        for i in range(task.count):
            if not task.running:
                break
            
            jitter = random.uniform(0.1, 1.5)
            sleep_time = task.delay + jitter
            
            success, _, _ = self.discord_client.send_message(
                task.token,
                task.channel_id,
                task.message,
                auto_delete=True
            )
            
            with self.lock:
                if success:
                    task.sent_count += 1
                else:
                    task.failed_count += 1
            
            if i < task.count - 1:
                time.sleep(sleep_time)
        
        with self.lock:
            task.running = False
    
    def stop_task(self, task_id: str) -> bool:
        """Stop a running task"""
        with self.lock:
            task = self.tasks.get(task_id)
            if task:
                task.running = False
                return True
        return False
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get task status"""
        with self.lock:
            task = self.tasks.get(task_id)
            if task:
                return {
                    'id': task.id,
                    'running': task.running,
                    'sent': task.sent_count,
                    'failed': task.failed_count,
                    'total': task.count
                }
        return None
    
    def get_active_count(self) -> int:
        with self.lock:
            return len([t for t in self.tasks.values() if t.running])

# ============================================================================
# INITIALIZATION
# ============================================================================

proxy_rotator = ProxyRotator()
discord_client = DiscordClient(proxy_rotator)
kamp_engine = KampEngine(discord_client)

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    """Dashboard"""
    return render_template('index.html')

@app.route('/api/validate', methods=['POST'])
def validate_token():
    """Validate Discord token with proxy rotation"""
    data = request.get_json()
    token = data.get('token', '').strip()
    
    if not token:
        return jsonify({'valid': False, 'message': 'Token required'})
    
    valid, username, error = discord_client.validate_token(token)
    
    return jsonify({
        'valid': valid,
        'username': username,
        'message': error or ('Valid token' if valid else 'Validation failed')
    })

@app.route('/api/kamp/start', methods=['POST'])
def start_kamp():
    """Start a new kamp spammer task"""
    data = request.get_json()
    
    token = data.get('token', '').strip()
    channel_id = data.get('channelId', '').strip()
    message = data.get('message', '').strip()
    count = int(data.get('count', 10))
    delay = float(data.get('delay', 2.0))
    
    if not all([token, channel_id, message]):
        return jsonify({'success': False, 'message': 'Missing required fields'})
    
    task_id = kamp_engine.create_task(token, channel_id, message, count, delay)
    
    return jsonify({
        'success': True,
        'taskId': task_id,
        'message': 'Kamp started'
    })

@app.route('/api/kamp/stop', methods=['POST'])
def stop_kamp():
    """Stop a running kamp task"""
    data = request.get_json()
    task_id = data.get('taskId', '')
    
    stopped = kamp_engine.stop_task(task_id)
    
    return jsonify({
        'success': stopped,
        'message': 'Task stopped' if stopped else 'Task not found'
    })

@app.route('/api/kamp/status/<task_id>', methods=['GET'])
def kamp_status(task_id):
    """Get kamp task status"""
    status = kamp_engine.get_task_status(task_id)
    
    if status:
        return jsonify(status)
    
    return jsonify({'running': False, 'sent': 0, 'failed': 0, 'total': 0})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'proxies': proxy_rotator.get_available_count(),
        'active_tasks': kamp_engine.get_active_count()
    })

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)

# © 2026 DoomHub and Tader - All Rights Reserved
