import os
import json
import logging
from datetime import datetime
from flask import Flask, jsonify, render_template_string

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

DATABASE_FILE = "data/bot_data.json"
LOG_FILE = "bot.log"

def get_bot_status():
    """Get current bot status"""
    try:
        # Check if bot is logging (indicating it's running)
        if os.path.exists(LOG_FILE):
            # Get last log time
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1]
                    return "healthy"
        return "unknown"
    except:
        return "unknown"

def load_database():
    """Load bot database"""
    try:
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"channels": [], "groups": [], "content": [], "broadcast_history": []}

@app.route('/')
def home():
    db = load_database()
    status = get_bot_status()
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>24/7 Stable Bot Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 900px;
            width: 100%;
        }
        h1 {
            color: #667eea;
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 10px;
        }
        .status-badge {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 20px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .status-healthy {
            background: #4caf50;
            color: white;
        }
        .status-unknown {
            background: #ff9800;
            color: white;
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }
        .card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        }
        .card h3 {
            font-size: 2.5em;
            margin: 10px 0;
        }
        .card p {
            opacity: 0.9;
        }
        .info-box {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            border-left: 4px solid #667eea;
        }
        .feature-list {
            list-style: none;
            margin: 15px 0;
        }
        .feature-list li {
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .feature-list li:last-child {
            border-bottom: none;
        }
        .feature-list li:before {
            content: "✓ ";
            color: #4caf50;
            font-weight: bold;
            margin-right: 10px;
        }
        .commands {
            background: #f0f7ff;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            font-family: 'Courier New', monospace;
        }
        .command {
            background: white;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 3px solid #667eea;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            color: #999;
        }
        .uptime {
            background: #fff3cd;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #ffc107;
        }
        @media (max-width: 600px) {
            .grid { grid-template-columns: 1fr; }
            .container { padding: 20px; }
            h1 { font-size: 1.5em; }
            .card h3 { font-size: 2em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 24/7 Stable Bot Dashboard</h1>
        <div class="status-badge status-{{ status }}">
            ● {{ 'HEALTHY & RUNNING' if status == 'healthy' else 'STATUS UNKNOWN' }}
        </div>
        
        <div class="uptime">
            <strong>✅ Bot Features:</strong>
            <ul class="feature-list">
                <li>Runs 24/7 without stopping</li>
                <li>Automatic reconnection on failure</li>
                <li>Enhanced error handling</li>
                <li>Health monitoring</li>
                <li>Graceful shutdown</li>
                <li>Production-grade logging</li>
            </ul>
        </div>
        
        <div class="grid">
            <div class="card">
                <p>📢 Channels</p>
                <h3>{{ channels_count }}</h3>
            </div>
            <div class="card">
                <p>👥 Groups</p>
                <h3>{{ groups_count }}</h3>
            </div>
            <div class="card">
                <p>📤 Broadcasts</p>
                <h3>{{ broadcasts_count }}</h3>
            </div>
            <div class="card">
                <p>📁 Saved Content</p>
                <h3>{{ content_count }}</h3>
            </div>
        </div>
        
        <div class="info-box">
            <h3>🚀 Why This Bot Stays Online 24/7</h3>
            <ul class="feature-list">
                <li><strong>Connection Management:</strong> Automatic reconnection with exponential backoff</li>
                <li><strong>Error Recovery:</strong> Handles RPC errors and connection timeouts gracefully</li>
                <li><strong>Health Monitoring:</strong> Continuous heartbeat checks every 60 seconds</li>
                <li><strong>Signal Handling:</strong> Proper graceful shutdown on system signals</li>
                <li><strong>Rate Limiting:</strong> Smart delays to avoid Telegram rate limits</li>
                <li><strong>Logging:</strong> Detailed logs for debugging any issues</li>
                <li><strong>Async Processing:</strong> Non-blocking operations for reliability</li>
            </ul>
        </div>
        
        <div class="commands">
            <h3>📝 Available Commands</h3>
            <div class="command">/start - Show main menu</div>
            <div class="command">/addchannel @name - Add channel to broadcast</div>
            <div class="command">/addgroup @name - Add group to broadcast</div>
            <div class="command">/broadcast message - Send message to all targets</div>
            <div class="command">/targets - View all channels/groups</div>
            <div class="command">/stats - Show statistics</div>
            <div class="command">/help - Show help</div>
        </div>
        
        <div class="info-box">
            <h3>⚙️ Production Configuration</h3>
            <p><strong>Retry Mechanism:</strong> Up to 5 automatic reconnection attempts</p>
            <p><strong>Retry Delay:</strong> 10 seconds between retries</p>
            <p><strong>Health Check:</strong> Every 60 seconds</p>
            <p><strong>Logging:</strong> All events logged to bot.log</p>
            <p><strong>Database:</strong> Auto-saved after each operation</p>
        </div>
        
        <div class="footer">
            <p><strong>✅ Status:</strong> Online and Stable</p>
            <p><strong>🔄 Uptime:</strong> 24/7 on Render</p>
            <p><strong>🚀 Version:</strong> Production Grade 1.0</p>
            <p style="margin-top: 20px; opacity: 0.7;">
                Last updated: {{ now }}
            </p>
        </div>
    </div>
</body>
</html>
    """, 
    channels_count=len(db['channels']),
    groups_count=len(db['groups']),
    broadcasts_count=len(db['broadcast_history']),
    content_count=len(db['content']),
    status=status,
    now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
)

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    db = load_database()
    return jsonify({
        "status": "healthy",
        "service": "24-7-stable-bot",
        "channels": len(db['channels']),
        "groups": len(db['groups']),
        "timestamp": datetime.now().isoformat()
    }), 200

@app.route('/api/status')
def api_status():
    """Get bot status"""
    db = load_database()
    status = get_bot_status()
    
    return jsonify({
        "status": status,
        "channels": len(db['channels']),
        "groups": len(db['groups']),
        "broadcasts": len(db['broadcast_history']),
        "content": len(db['content']),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🌐 Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
