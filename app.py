<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>DOOMHUB | MOBILE TERMINAL</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Rajdhani:wght@500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --hub-blue: #3b82f6; /* Modern Blue Accent */
            --hub-bg: #ffffff;
            --hub-panel: #f9fafb;
            --hub-text: #1f2937;
            --hub-border: #e5e7eb;
        }
        body { 
            background: var(--hub-bg); 
            color: var(--hub-text); 
            font-family: 'Rajdhani', sans-serif; 
            overflow-x: hidden; 
            -webkit-tap-highlight-color: transparent;
        }
        /* Custom Scrollbar - Light */
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: var(--hub-bg); }
        ::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 2px;}

        .clean-title { font-family: 'Orbitron', sans-serif; letter-spacing: -1px; }
        
        /* Tab System Styles */
        .tab-content { display: none; animation: slideUp 0.3s ease forwards; opacity: 0; transform: translateY(10px); }
        .tab-content.active { display: block; }
        
        @keyframes slideUp {
            to { opacity: 1; transform: translateY(0); }
        }

        .nav-btn { color: #9ca3af; transition: all 0.2s; }
        .nav-btn.active { color: var(--hub-blue); border-top: 2px solid var(--hub-blue); background: linear-gradient(0deg, rgba(59, 130, 246, 0.05) 0%, transparent 100%); }
        
        .hub-input { background: #ffffff; border: 1px solid var(--hub-border); color: var(--hub-text); }
        .hub-input:focus { outline: none; border-color: var(--hub-blue); box-shadow: 0 0 8px rgba(59, 130, 246, 0.2); }
        
        .hub-btn { background: var(--hub-blue); color: white; border: 1px solid #2563eb; text-transform: uppercase; font-weight: bold; letter-spacing: 1px; transition: 0.1s; }
        .hub-btn:hover { background: #2563eb; }
        .hub-btn:active { transform: scale(0.97); }
        
        .panel { background: var(--hub-panel); border: 1px solid var(--hub-border); }
    </style>
</head>
<body class="pb-20 h-screen flex flex-col">

    <div id="setup-screen" class="flex-1 flex flex-col items-center justify-center p-6 h-full z-50 fixed inset-0 bg-white">
        <div class="text-center mb-10">
            <h1 class="clean-title text-5xl mb-2 text-gray-950 uppercase tracking-tighter">DOOMHUB</h1>
            <p class="text-xs text-gray-500 uppercase tracking-[0.3em]">Mobile Deployment Unit</p>
        </div>

        <div class="panel w-full max-w-sm p-8 rounded-xl shadow-lg border border-gray-100">
            <div class="mb-6 flex items-center justify-between border-b border-gray-200 pb-3">
                <span class="text-sm font-bold text-gray-700">AUTHORIZATION REQUIRED</span>
                <span class="w-2.5 h-2.5 bg-green-500 rounded-full animate-pulse shadow-[0_0_5px_#10b981]"></span>
            </div>
            <input type="password" id="token" placeholder="Enter Discord Token..." 
                class="hub-input w-full p-4 rounded-lg mb-4 text-center tracking-widest text-sm shadow-inner">
            <button onclick="setupSystem()" id="login-btn" class="hub-btn w-full py-4 rounded-lg shadow-md transition-all">
                Initialize System
            </button>
        </div>
        <p class="text-[10px] text-gray-400 mt-10">Use responsibly. Internal use only.</p>
    </div>

    <div id="main-app" class="hidden flex-1 flex flex-col h-full">
        
        <header class="panel p-4 sticky top-0 z-40 flex justify-between items-center border-b shadow-sm bg-white/95 backdrop-blur-sm">
            <h1 class="clean-title text-2xl text-gray-950 uppercase">DOOMHUB</h1>
            <div class="flex items-center gap-3">
                <span class="text-[10px] border border-green-300 text-green-700 px-2.5 py-1 rounded-full bg-green-50 font-medium">PROXY ACTIVE</span>
                <div class="w-9 h-9 rounded-full border border-gray-300 bg-gray-100 flex items-center justify-center text-gray-500 font-bold text-sm shadow-inner">ADM</div>
            </div>
        </header>

        <main class="flex-1 overflow-y-auto p-4 pb-28 bg-gray-50">

            <div id="tab-home" class="tab-content active space-y-4">
                <div class="panel p-5 rounded-xl flex justify-between items-center border-l-4 border-l-blue-600 shadow-sm bg-white">
                    <div>
                        <p class="text-xs text-gray-500 uppercase tracking-wider">System Status</p>
                        <p class="font-bold text-xl text-gray-950">SYSTEMS OPERATIONAL</p>
                    </div>
                    <span class="text-3xl opacity-80">💻</span>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div class="panel p-5 rounded-xl text-center bg-white shadow-sm">
                        <p class="text-3xl font-bold text-blue-600">0</p>
                        <p class="text-xs text-gray-600 uppercase mt-1.5 font-medium tracking-wide">Tasks Executed</p>
                    </div>
                    <div class="panel p-5 rounded-xl text-center bg-white shadow-sm">
                        <p class="text-3xl font-bold text-blue-600">0</p>
                        <p class="text-xs text-gray-600 uppercase mt-1.5 font-medium tracking-wide">Requests Sent</p>
                    </div>
                </div>

                <div class="panel p-4 rounded-xl h-40 flex flex-col bg-gray-950 shadow-inner">
                    <p class="text-[11px] text-gray-400 border-b border-gray-800 pb-1.5 mb-2 font-mono uppercase tracking-wider">Terminal Output</p>
                    <div id="console-logs" class="flex-1 overflow-y-auto text-[11px] font-mono text-gray-300 space-y-1.5 scrollbar-thin scrollbar-thumb-gray-700 scrollbar-track-gray-900">
                        <p class="text-blue-400"># System initialized successfully...</p>
                        <p class="text-green-400"># Secure proxy connection established...</p>
                        <p># Awaiting user command input...</p>
                    </div>
                </div>
            </div>

            <div id="tab-spammer" class="tab-content space-y-4">
                <h2 class="font-bold text-gray-900 border-b border-gray-200 pb-2.5 flex items-center gap-2.5 text-lg">
                    <span class="text-2xl text-blue-600">✉️</span> Mass Messenger Tool
                </h2>
                
                <div class="panel p-5 rounded-xl space-y-4 bg-white shadow-sm">
                    <div>
                        <label class="text-xs text-gray-600 uppercase font-medium tracking-wide">Target Channel ID</label>
                        <input type="text" class="hub-input w-full p-3.5 rounded-lg mt-1.5 text-sm" placeholder="Paste Channel ID...">
                    </div>
                    <div>
                        <label class="text-xs text-gray-600 uppercase font-medium tracking-wide">Message Payload</label>
                        <textarea class="hub-input w-full p-3.5 rounded-lg mt-1.5 text-sm h-24 resize-none" placeholder="Enter message content..."></textarea>
                    </div>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label class="text-xs text-gray-600 uppercase font-medium tracking-wide">Iteration Count</label>
                            <input type="number" class="hub-input w-full p-3.5 rounded-lg mt-1.5 text-sm text-center" value="5">
                        </div>
                        <div>
                            <label class="text-xs text-gray-600 uppercase font-medium tracking-wide">Interval (ms)</label>
                            <input type="number" class="hub-input w-full p-3.5 rounded-lg mt-1.5 text-sm text-center" value="1000">
                        </div>
                    </div>
                    <button onclick="logAction('Message task added to queue.')" class="hub-btn w-full py-3.5 rounded-lg mt-3 text-sm shadow">Dispatch Messages</button>
                </div>
            </div>

            <div id="tab-nuke" class="tab-content space-y-4">
                <h2 class="font-bold text-gray-900 border-b border-gray-200 pb-2.5 flex items-center gap-2.5 text-lg">
                    <span class="text-2xl text-gray-700">⚙️</span> Server Management
                </h2>

                <div class="panel p-5 rounded-xl space-y-4 bg-white shadow-sm">
                    <div>
                        <label class="text-xs text-gray-600 uppercase font-medium tracking-wide">Guild (Server) ID</label>
                        <input type="text" class="hub-input w-full p-3.5 rounded-lg mt-1.5 text-sm" placeholder="Enter Server ID...">
                    </div>
                    
                    <div class="space-y-2.5 border-t border-gray-100 pt-4">
                        <label class="flex items-center justify-between bg-gray-50 p-3.5 rounded-lg border border-gray-100">
                            <span class="text-sm font-medium text-gray-800">Clear Channels</span>
                            <input type="checkbox" class="w-5 h-5 accent-blue-600">
                        </label>
                        <label class="flex items-center justify-between bg-gray-50 p-3.5 rounded-lg border border-gray-100">
                            <span class="text-sm font-medium text-gray-800">Manage Members</span>
                            <input type="checkbox" class="w-5 h-5 accent-blue-600">
                        </label>
                        <label class="flex items-center justify-between bg-gray-50 p-3.5 rounded-lg border border-gray-100">
                            <span class="text-sm font-medium text-gray-800">Cleanup Roles</span>
                            <input type="checkbox" class="w-5 h-5 accent-blue-600">
                        </label>
                    </div>

                    <button onclick="logAction('Management task initiated.')" class="w-full bg-gray-800 text-white font-bold py-4 rounded-lg mt-3 border border-gray-900 shadow-md uppercase tracking-widest text-sm transition-all hover:bg-gray-950 active:scale-95">
                        Execute Sequence
                    </button>
                </div>
            </div>

            <div id="tab-settings" class="tab-content space-y-4">
                <h2 class="font-bold text-gray-900 border-b border-gray-200 pb-2.5 flex items-center gap-2.5 text-lg">
                    <span class="text-2xl text-gray-600">🔧</span> Configuration
                </h2>
                
                <div class="panel p-5 rounded-xl space-y-4 bg-white shadow-sm text-sm">
                    <div class="flex justify-between items-center border-b border-gray-100 pb-3">
                        <span class="font-medium text-gray-600">Deployment Route</span>
                        <span class="text-xs bg-gray-100 px-3 py-1 rounded-full text-gray-700 font-mono">Mobile v2.1.0</span>
                    </div>
                    <div class="flex justify-between items-center border-b border-gray-100 pb-3">
                        <span class="font-medium text-gray-600">Proxy Endpoint</span>
                        <span class="text-xs text-blue-700 font-mono">*.boorapolat.workers.dev</span>
                    </div>
                    <div class="border-b border-gray-100 pb-3">
                        <p class="font-medium text-gray-600 mb-1.5">Active Token (Session)</p>
                        <p class="text-xs bg-gray-950 p-3 rounded-lg text-blue-300 font-mono break-all filter blur-[3px] hover:blur-none transition-all select-all shadow-inner">
                            Click to reveal active session token...
                        </p>
                    </div>
                    
                    <button onclick="location.reload()" class="w-full bg-white text-gray-800 font-semibold py-3.5 rounded-lg mt-4 text-xs border border-gray-300 shadow-sm transition-all hover:bg-gray-50 active:bg-gray-100">
                        Log Out & End Session
                    </button>
                </div>
                <div class="text-center text-[10px] text-gray-400 p-4">DOOMHUB Technical Division © 2024</div>
            </div>

        </main>

        <nav class="panel fixed bottom-0 left-0 right-0 flex justify-around p-2 pb-safe z-50 border-t border-gray-200 bg-white shadow-[0_-2px_10px_rgba(0,0,0,0.03)]">
            <button onclick="switchTab('home')" id="nav-home" class="nav-btn active flex-1 flex flex-col items-center py-2.5 rounded-lg">
                <span class="text-2xl mb-1">🏠</span>
                <span class="text-[10px] font-bold tracking-wider uppercase">HOME</span>
            </button>
            <button onclick="switchTab('spammer')" id="nav-spammer" class="nav-btn flex-1 flex flex-col items-center py-2.5 rounded-lg">
                <span class="text-2xl mb-1">✉️</span>
                <span class="text-[10px] font-bold tracking-wider uppercase">SPAM</span>
            </button>
            <button onclick="switchTab('nuke')" id="nav-nuke" class="nav-btn flex-1 flex flex-col items-center py-2.5 rounded-lg">
                <span class="text-2xl mb-1">⚙️</span>
                <span class="text-[10px] font-bold tracking-wider uppercase">MANAGE</span>
            </button>
            <button onclick="switchTab('settings')" id="nav-settings" class="nav-btn flex-1 flex flex-col items-center py-2.5 rounded-lg">
                <span class="text-2xl mb-1">🔧</span>
                <span class="text-[10px] font-bold tracking-wider uppercase">SET</span>
            </button>
        </nav>

    </div>

    <script>
        // Tab Management System
        window.switchTab = function(tabId) {
            // Hide all content areas
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            // Reset all navigation buttons
            document.querySelectorAll('.nav-btn').forEach(button => button.classList.remove('active'));
            
            // Show requested tab and update its nav button
            document.getElementById('tab-' + tabId).classList.add('active');
            document.getElementById('nav-' + tabId).classList.add('active');
            
            logAction(`Switched to: ${tabId.toUpperCase()}`);
        };

        // Terminal Output Logger
        window.logAction = function(msg) {
            const consoleBox = document.getElementById('console-logs');
            const timeStamp = new Date().toLocaleTimeString('en-US', { hour12: false });
            consoleBox.innerHTML += `<p><span class="text-blue-400">[${timeStamp}]</span> > ${msg}</p>`;
            // Auto-scroll to bottom
            consoleBox.scrollTop = consoleBox.scrollHeight;
        };

        // Initialize System Request
        window.setupSystem = async function() {
            const tokenValue = document.getElementById('token').value;
            const actionBtn = document.getElementById('login-btn');
            
            if(!tokenValue) {
                actionBtn.innerHTML = "TOKEN REQUIRED!";
                actionBtn.classList.remove('hub-btn');
                actionBtn.classList.add('bg-gray-300', 'text-gray-700');
                setTimeout(() => { 
                    actionBtn.innerHTML = "Initialize System"; 
                    actionBtn.classList.add('hub-btn');
                    actionBtn.classList.remove('bg-gray-300', 'text-gray-700');
                }, 1500);
                return;
            }

            actionBtn.innerHTML = "AUTHENTICATING...";
            actionBtn.disabled = true;

            try {
                // Sent POST request to Flask backend API
                const response = await fetch('/api/setup', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({token: tokenValue})
                });

                const apiData = await response.json();
                
                if(apiData.status === 'success') {
                    // Switch screens
                    document.getElementById('setup-screen').style.display = 'none';
                    document.getElementById('main-app').classList.remove('hidden');
                    switchTab('home'); // Force open home tab on success
                    logAction("Session authenticated.");
                } else {
                    alert('Authorization Error: ' + apiData.message);
                    actionBtn.innerHTML = "Initialize System";
                    actionBtn.disabled = false;
                }
            } catch (error) {
                // Connection failure fallback
                console.error('Connection error:', error);
                alert("Connection failed. Ensure backend service is running.");
                actionBtn.innerHTML = "Initialize System";
                actionBtn.disabled = false;
            }
        };
    </script>
</body>
</html>
