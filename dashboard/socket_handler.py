from core.logger import info, warn, error, log
from core.network_scanner import scan_network
import yaml
import os

# Load config defaults
config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'lab_config.yaml')
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Store current session settings (defaults from config)
current_settings = {
    'target_ip': config['defaults']['target_ip'],
    'interface': config['defaults']['interface'],
    'safe_mode': config['safe_mode']['default'],
    'gateway_ip': config['defaults']['gateway_ip'],
    'subnet': config['defaults']['subnet']
}

def register_socket_handlers(socketio):
    """Register all SocketIO event handlers with the given socketio instance"""
    
    @socketio.on('connect')
    def handle_connect():
        """Client connected to dashboard"""
        info('Dashboard client connected')
        # Emit directly to the connected client
        socketio.emit('log_message', {
            'level': 'info',
            'message': '✅ Connected to wifi-shadow server',
            'timestamp': '--:--:--'
        })

    @socketio.on('disconnect')
    def handle_disconnect():
        """Client disconnected from dashboard"""
        info('Dashboard client disconnected')

    @socketio.on('get_settings')
    def handle_get_settings():
        """Send current settings to the client"""
        info('Sending settings to client')
        socketio.emit('settings_loaded', current_settings)
        # Also log to dashboard
        socketio.emit('log_message', {
            'level': 'info',
            'message': f'⚙️ Settings loaded: interface={current_settings["interface"]}, target={current_settings["target_ip"]}',
            'timestamp': '--:--:--'
        })

    @socketio.on('save_settings')
    def handle_save_settings(data):
        """Save attack settings from dashboard"""
        global current_settings
        
        try:
            if 'target_ip' in data:
                current_settings['target_ip'] = data['target_ip']
            if 'interface' in data:
                current_settings['interface'] = data['interface']
            if 'safe_mode' in data:
                current_settings['safe_mode'] = data['safe_mode']
            if 'gateway_ip' in data:
                current_settings['gateway_ip'] = data['gateway_ip']
                
            info(f"Settings updated: {current_settings}")
            socketio.emit('settings_saved', {
                'status': 'ok',
                'settings': current_settings
            })
            socketio.emit('log_message', {
                'level': 'info',
                'message': f'✅ Settings applied: {current_settings["interface"]} -> {current_settings["target_ip"]}',
                'timestamp': '--:--:--'
            })
            
        except Exception as e:
            error(f"Failed to save settings: {e}")
            socketio.emit('settings_saved', {
                'status': 'error',
                'message': str(e)
            })

    @socketio.on('scan_network')
    def handle_scan_network():
        """Scan network for active devices"""
        info('Scanning network for devices...')
        socketio.emit('log_message', {
            'level': 'info',
            'message': '🔍 Scanning network... (this may take a few seconds)',
            'timestamp': '--:--:--'
        })
        
        try:
            devices = scan_network(
                interface=current_settings.get('interface'),
                timeout=2
            )
            
            if devices:
                socketio.emit('scan_done', {
                    'status': 'ok',
                    'devices': devices,
                    'count': len(devices)
                })
                socketio.emit('log_message', {
                    'level': 'info',
                    'message': f'✅ Scan complete. Found {len(devices)} devices.',
                    'timestamp': '--:--:--'
                })
            else:
                socketio.emit('scan_done', {
                    'status': 'no_devices',
                    'devices': [],
                    'count': 0
                })
                warn('No devices found on network')
                socketio.emit('log_message', {
                    'level': 'warn',
                    'message': '⚠️ No devices found. Check your interface and network.',
                    'timestamp': '--:--:--'
                })
                
        except Exception as e:
            error(f"Network scan failed: {e}")
            socketio.emit('scan_done', {
                'status': 'error',
                'message': str(e)
            })
            socketio.emit('log_message', {
                'level': 'error',
                'message': f'❌ Scan failed: {e}',
                'timestamp': '--:--:--'
            })

    @socketio.on('start_attack')
    def handle_start_attack(data):
        """Start an attack module (passive, active, or high)"""
        attack_type = data.get('type', 'passive')
        target_ip = data.get('target_ip') or current_settings.get('target_ip')
        safe_mode = data.get('safe_mode', current_settings.get('safe_mode', True))
        
        socketio.emit('log_message', {
            'level': 'info',
            'message': f'🚀 Starting {attack_type} attack on {target_ip}',
            'timestamp': '--:--:--'
        })
        
        if safe_mode:
            warn(f"⚠️ SAFE MODE: Attack '{attack_type}' on {target_ip} would run (dry-run only)")
            socketio.emit('attack_result', {
                'status': 'dry_run',
                'attack_type': attack_type,
                'target': target_ip,
                'message': f'[DRY RUN] {attack_type} attack simulated on {target_ip}'
            })
            socketio.emit('log_message', {
                'level': 'warn',
                'message': f'🔒 [SAFE MODE] {attack_type} attack on {target_ip} (dry-run)',
                'timestamp': '--:--:--'
            })
            return
        
        # Actual attack execution will go here
        info(f"🚀 Starting {attack_type} attack on {target_ip} (attack logic coming soon)")
        socketio.emit('attack_result', {
            'status': 'started',
            'attack_type': attack_type,
            'target': target_ip,
            'message': f'Started {attack_type} attack on {target_ip}'
        })
        socketio.emit('log_message', {
            'level': 'attack',
            'message': f'⚡ {attack_type} attack started on {target_ip}',
            'timestamp': '--:--:--'
        })