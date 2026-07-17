from core.logger import info, warn, error, log
from core.network_scanner import scan_network
import yaml
import os
import threading

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
        
        # ---- PASSIVE ATTACK ----
        if attack_type == 'passive':
            try:
                from core.passive_sniffer import start_passive_sniff
                socketio.emit('log_message', {
                    'level': 'info',
                    'message': '🔵 Starting passive sniffing... (capturing 50 packets)',
                    'timestamp': '--:--:--'
                })
                
                def run_sniff():
                    result = start_passive_sniff(
                        interface=current_settings.get('interface'),
                        packet_count=50,
                        timeout=30
                    )
                    if result:
                        socketio.emit('log_message', {
                            'level': 'info',
                            'message': f'✅ Passive sniffing complete. Captured {result.get("packet_count", 0)} packets.',
                            'timestamp': '--:--:--'
                        })
                        if result.get('plaintext_passwords'):
                            for pwd in result['plaintext_passwords']:
                                socketio.emit('log_message', {
                                    'level': 'attack',
                                    'message': f'🔓 Plaintext password: {pwd["password"]} on {pwd["host"]}',
                                    'timestamp': '--:--:--'
                                })
                
                thread = threading.Thread(target=run_sniff)
                thread.start()
                
                socketio.emit('attack_result', {
                    'status': 'started',
                    'attack_type': 'passive',
                    'target': target_ip,
                    'message': f'Started passive sniffing on {current_settings.get("interface")}'
                })
                
            except ImportError as e:
                error(f"Failed to import passive_sniffer: {e}")
                socketio.emit('log_message', {
                    'level': 'error',
                    'message': f'❌ Passive sniffer not ready: {e}',
                    'timestamp': '--:--:--'
                })
            except Exception as e:
                error(f"Passive attack failed: {e}")
                socketio.emit('log_message', {
                    'level': 'error',
                    'message': f'❌ Passive attack failed: {e}',
                    'timestamp': '--:--:--'
                })
        
        # ---- ACTIVE ATTACK ----
        elif attack_type == 'active':
            try:
                from core.active_scanner import port_scan, arp_spoof
                
                socketio.emit('log_message', {
                    'level': 'info',
                    'message': f'🟡 Starting active attacks on {target_ip}...',
                    'timestamp': '--:--:--'
                })
                
                # Step 1: Port scan
                socketio.emit('log_message', {
                    'level': 'info',
                    'message': '🔍 Running port scan...',
                    'timestamp': '--:--:--'
                })
                
                open_ports = port_scan(target_ip)
                
                if open_ports:
                    socketio.emit('log_message', {
                        'level': 'attack',
                        'message': f'🟡 Found {len(open_ports)} open ports on {target_ip}',
                        'timestamp': '--:--:--'
                    })
                    for port, service in open_ports.items():
                        socketio.emit('log_message', {
                            'level': 'attack',
                            'message': f'   Port {port}: {service} (OPEN)',
                            'timestamp': '--:--:--'
                        })
                else:
                    socketio.emit('log_message', {
                        'level': 'info',
                        'message': f'ℹ️ No open ports found on {target_ip}',
                        'timestamp': '--:--:--'
                    })
                
                # Step 2: ARP Spoofing (if gateway is set)
                gateway = current_settings.get('gateway_ip')
                if gateway:
                    socketio.emit('log_message', {
                        'level': 'info',
                        'message': f'🔄 Starting ARP spoofing against {target_ip} via {gateway}...',
                        'timestamp': '--:--:--'
                    })
                    
                    def run_arp_spoof():
                        result = arp_spoof(target_ip, gateway, current_settings.get('interface'))
                        if result:
                            socketio.emit('log_message', {
                                'level': 'attack',
                                'message': f'✅ ARP spoofing complete. We are now MITM!',
                                'timestamp': '--:--:--'
                            })
                        else:
                            socketio.emit('log_message', {
                                'level': 'error',
                                'message': f'❌ ARP spoofing failed',
                                'timestamp': '--:--:--'
                            })
                    
                    thread = threading.Thread(target=run_arp_spoof)
                    thread.start()
                else:
                    socketio.emit('log_message', {
                        'level': 'warn',
                        'message': '⚠️ No gateway IP set. Skipping ARP spoofing.',
                        'timestamp': '--:--:--'
                    })
                
                socketio.emit('attack_result', {
                    'status': 'started',
                    'attack_type': 'active',
                    'target': target_ip,
                    'message': f'Active attacks started on {target_ip}'
                })
                
            except ImportError as e:
                error(f"Failed to import active_scanner: {e}")
                socketio.emit('log_message', {
                    'level': 'error',
                    'message': f'❌ Active scanner not ready: {e}',
                    'timestamp': '--:--:--'
                })
            except Exception as e:
                error(f"Active attack failed: {e}")
                socketio.emit('log_message', {
                    'level': 'error',
                    'message': f'❌ Active attack failed: {e}',
                    'timestamp': '--:--:--'
                })
        
        # ---- HIGH RISK ----
               
        elif attack_type == 'high':
            try:
                from core.high_risk import run_high_risk_attack
                
                socketio.emit('log_message', {
                    'level': 'attack',
                    'message': f'🔴 STARTING HIGH RISK EXPLOITATION on {target_ip}',
                    'timestamp': '--:--:--'
                })
                socketio.emit('log_message', {
                    'level': 'warn',
                    'message': '⚠️ THIS IS A SIMULATION - No real exploits are executed',
                    'timestamp': '--:--:--'
                })
                
                gateway = current_settings.get('gateway_ip', '192.168.1.1')
                interface = current_settings.get('interface')
                
                # Run in background thread
                def run_high_risk():
                    try:
                        results = run_high_risk_attack(target_ip, gateway, interface)
                        
                        # Emit results with safe checks
                        vuln_check = results.get('vulnerability_check', {})
                        if vuln_check and vuln_check.get('vulnerable'):
                            socketio.emit('log_message', {
                                'level': 'attack',
                                'message': f'🔴 TARGET IS VULNERABLE! {target_ip} has unpatched vulnerabilities!',
                                'timestamp': '--:--:--'
                            })
                        
                        exploit_attempt = results.get('exploit_attempt')
                        if exploit_attempt and exploit_attempt.get('success'):
                            socketio.emit('log_message', {
                                'level': 'attack',
                                'message': f'💀 SYSTEM COMPROMISED! Remote shell acquired on {target_ip}',
                                'timestamp': '--:--:--'
                            })
                        
                        smb_relay = results.get('smb_relay')
                        if smb_relay and smb_relay.get('success'):
                            socketio.emit('log_message', {
                                'level': 'attack',
                                'message': f'💀 SMB RELAY SUCCESS! Captured credentials from {target_ip}',
                                'timestamp': '--:--:--'
                            })
                        
                        socketio.emit('log_message', {
                            'level': 'info',
                            'message': '✅ High risk attack sequence complete',
                            'timestamp': '--:--:--'
                        })
                        
                    except Exception as e:
                        error(f"High risk attack failed: {e}")
                        socketio.emit('log_message', {
                            'level': 'error',
                            'message': f'❌ High risk attack failed: {e}',
                            'timestamp': '--:--:--'
                        })
                
                thread = threading.Thread(target=run_high_risk)
                thread.start()
                
                socketio.emit('attack_result', {
                    'status': 'started',
                    'attack_type': 'high',
                    'target': target_ip,
                    'message': f'High risk exploitation started on {target_ip}'
                })
                
            except ImportError as e:
                error(f"Failed to import high_risk: {e}")
                socketio.emit('log_message', {
                    'level': 'error',
                    'message': f'❌ High risk module not ready: {e}',
                    'timestamp': '--:--:--'
                })
            except Exception as e:
                error(f"High risk attack failed: {e}")
                socketio.emit('log_message', {
                    'level': 'error',
                    'message': f'❌ High risk attack failed: {e}',
                    'timestamp': '--:--:--'
                })