import json
from datetime import datetime
from flask_socketio import emit

# Global reference to socketio (set by app.py during initialization)
_socketio = None

def init_socketio(socketio_instance):
    """Initialize the SocketIO instance for broadcasting logs"""
    global _socketio
    _socketio = socketio_instance

def log(level, message, broadcast=True):
    """
    Log a message to console and optionally emit to dashboard via SocketIO.
    
    Levels: 'debug', 'info', 'warn', 'error', 'device', 'attack'
    """
    timestamp = datetime.now().strftime('%H:%M:%S')
    formatted = f"[{timestamp}] [{level.upper()}] {message}"
    
    # Always print to console
    print(formatted)
    
    # Emit to dashboard if SocketIO is available
    if _socketio and broadcast:
        try:
            _socketio.emit('log_message', {
                'level': level,
                'message': message,
                'timestamp': timestamp
            }, broadcast=True)
        except Exception as e:
            print(f"[ERROR] Failed to emit log: {e}")

def debug(msg):
    log('debug', msg)

def info(msg):
    log('info', msg)

def warn(msg):
    log('warn', msg)

def error(msg):
    log('error', msg)

def device(msg):
    log('device', msg)

def attack(msg):
    log('attack', msg)