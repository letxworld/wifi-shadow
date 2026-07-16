from flask import Flask
from flask_socketio import SocketIO
from core.logger import init_socketio, info

# ===== Initialize Flask App =====
app = Flask(__name__)
app.config['SECRET_KEY'] = 'wifi-shadow-lab-key'

# ===== Initialize SocketIO =====
socketio = SocketIO(app, cors_allowed_origins="*")

init_socketio(socketio)


from dashboard import routes
from dashboard import socket_handler

# ===== Startup Message =====
info("🚀 wifi-shadow server starting...")
info(f"📍 Dashboard available at: http://127.0.0.1:5000")
info(f"🔒 Safe mode: ON by default (enable in dashboard settings)")

# ===== Run the Application =====
if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        allow_unsafe_werkzeug=True
    )