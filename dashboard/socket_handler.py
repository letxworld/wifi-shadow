from flask_socketio import emit
from dashboard import socketio
from core.logger import info, warn, error, log
from core.network_scanner import scan_network

# Store current session settings (defaults from config)
current_settings = {
    'target_ip': '192.168.1.100',
    'interface': 'eth0',
    'safe_mode': True,
    'gateway_ip': '192.168.1.1',
    'subnet': '192.168.1.0/24'
}

@socketio.on('connect')
def handle_connect():
    """Client connected to dashboard"""
    info('Dashboard client connected')
    emit('log_message', {
        'level': 'info',
        'message': '✅ Connected to wifi-shadow server',
        'timestamp': '--:--:--'
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected from dashboard"""
    info('Dashboard client disconnected')

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
        emit('settings_saved', {
            'status': 'ok',
            'settings': current_settings
        })
        
    except Exception as e:
        error(f"Failed to save settings: {e}")
        emit('settings_saved', {
            'status': 'error',
            'message': str(e)
        })

@socketio.on('scan_network')
def handle_scan_network():
    """Scan network for active devices"""
    info('Scanning network for devices...')
    emit('log_message', {
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
            emit('scan_done', {
                'status': 'ok',
                'devices': devices,
                'count': len(devices)
            })
        else:
            emit('scan_done', {
                'status': 'no_devices',
                'devices': [],
                'count': 0
            })
            warn('No devices found on network')
            
    except Exception as e:
        error(f"Network scan failed: {e}")
        emit('scan_done', {
            'status': 'error',
            'message': str(e)
        })

@socketio.on('start_attack')
def handle_start_attack(data):
    """Start an attack module (passive, active, or high)"""
    attack_type = data.get('type', 'passive')
    target_ip = data.get('target_ip') or current_settings.get('target_ip')
    safe_mode = data.get('safe_mode', current_settings.get('safe_mode', True))
    
    if safe_mode:
        warn(f"⚠️ SAFE MODE: Attack '{attack_type}' on {target_ip} would run (dry-run only)")
        emit('attack_result', {
            'status': 'dry_run',
            'attack_type': attack_type,
            'target': target_ip,
            'message': f'[DRY RUN] {attack_type} attack simulated on {target_ip}'
        })
        return
    
    # Actual attack execution will go here
    # (Modules for each attack type will be added later)
    info(f"🚀 Starting {attack_type} attack on {target_ip} (attack logic coming soon)")
    emit('attack_result', {
        'status': 'started',
        'attack_type': attack_type,
        'target': target_ip,
        'message': f'Started {attack_type} attack on {target_ip}'
    })