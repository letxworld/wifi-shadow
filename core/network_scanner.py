import socket
from scapy.all import ARP, Ether, srp
from core.logger import info, device, warn, error

def scan_network(interface=None, timeout=2):
    """
    Scan the local network for active devices using ARP requests.
    
    Returns:
        list of dict: [{'ip': '192.168.1.1', 'mac': 'aa:bb:cc:dd:ee:ff', 'hostname': 'router'}]
    
    This is a passive, safe operation — no packet injection or routing changes.
    """
    devices = []
    
    try:
        # Get local IP and subnet
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        subnet = '.'.join(local_ip.split('.')[:-1]) + '.0/24'
        info(f"Scanning network: {subnet} on interface {interface or 'default'}")
        
        # Build ARP request
        arp = ARP(pdst=subnet)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp
        
        # Send packet and receive responses
        result = srp(packet, timeout=timeout, iface=interface, verbose=False)[0]
        
        # Parse responses
        for sent, received in result:
            ip = received.psrc
            mac = received.hwsrc
            
            # Try to get hostname via reverse DNS
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except:
                hostname = None
            
            devices.append({
                'ip': ip,
                'mac': mac,
                'hostname': hostname
            })
            
            device(f"Found {ip} - {mac} ({hostname or 'unknown'})")
        
        info(f"Scan complete. Found {len(devices)} active devices.")
        return devices
        
    except PermissionError:
        error("Permission denied. Try running with sudo/administrator privileges.")
        return []
    except Exception as e:
        error(f"Network scan failed: {e}")
        return []