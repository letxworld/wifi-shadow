# 📡 wifi-shadow

Understand what an attacker can see and do on your network — in real time.

## 🎯 What is wifi-shadow?

wifi-shadow
is an interactive cybersecurity education platform that demonstrates
real attack techniques
used by hackers on shared networks (like public WiFi, office LANs, or home networks).

## 🚀 Features

### 🔵 Passive Spying

What an attacker can see without touching your device

### 🟡 Active Attacks

What an attacker can intercept and manipulate

### 🔴 High Risk Exploitation

What an attacker can do if your device is vulnerable

## 🖥️ Dashboard Preview

```
┌─────────────────────────────────────────────────────────┐
│  📡 wifi-shadow                                         │
│  Understand what an attacker can see on your network    │
├─────────────────────────────────────────────────────────┤
│  🎯 Target Settings                                     │
│  Victim IP: [192.168.1.100]  Interface: [wlan0]        │
│  Safe Mode: [✓] (ON = dry-run, no packets sent)        │
│  [💾 Apply Settings]                                    │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ 🔵 Passive   │  │ 🟡 Active   │  │ 🔴 High Risk │ │
│  │ Spying       │  │ Attacks     │  │ Exploitation │ │
│  │ [▶ Run Demo] │  │ [▶ Run Demo] │  │ [▶ Run Demo] │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────┤
│  📜 Live Log                                            │
│  [14:32:05] 🌐 DNS Query: facebook.com                  │
│  [14:32:10] 🔓 Plaintext password: "password123"       │
│  [14:32:15] 💀 SYSTEM COMPROMISED!                     │
└─────────────────────────────────────────────────────────┘
```

## 📦 Installation

#### Prerequisites

- Python 3.8+
(
Download
)
- pip
(Python package manager)
- Linux/macOS/Windows
(with administrative/root privileges for packet operations)
#### Step 1: Clone the Repository

```
git clone https://github.com/letxworld/wifi-shadow.git
cd wifi-shadow
```

#### Step 2: Create a Virtual Environment

```
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 3: Install Dependencies

```
pip install -r requirements.txt
```

#### Step 4: Configure Settings

Edit
config/lab_config.yaml
with your network details:

```
defaults:
  interface: "wlan0"           # Your network interface (run `ip link show` to find)
  target_ip: "192.168.1.100"   # Victim IP (auto-detected on scan)
  gateway_ip: "192.168.1.1"    # Your router IP
  subnet: "192.168.1.0/24"     # Your network range
```

#### Step 5: Run the Application

```
sudo venv/bin/python app.py
```

Note:
sudo
is required for packet capture and network operations.

#### Step 6: Open Your Browser

```
http://127.0.0.1:5000
```

## 🎮 How to Use

#### 1. Discover Devices

Click
📋 Discover Devices
— it scans your network and lists all connected devices.

#### 2. Set Target

- Select a victim IP from the list (or enter manually)
- Choose your network interface
- Toggle
Safe Mode
(ON = dry-run, OFF = live attacks)
#### 3. Run Attacks

Click
▶ Run Demo
on any attack card:

#### 4. Watch the Live Log

All activity appears in real-time in the
Live Log
panel.

## 🔬 Attack Techniques Explained

#### DNS Sniffing

When you type
facebook.com
, your device asks the DNS server for its IP address. This query is
broadcast
to everyone on the network — attackers can see every site you visit.

#### HTTP Plaintext Capture

If a website uses HTTP (not HTTPS), all data is sent in
plain text
. Attackers can read your passwords, emails, and form submissions in real time.

#### ARP Spoofing (Man-in-the-Middle)

The attacker tricks your device into thinking they are the router. All your internet traffic passes through them first, allowing them to intercept and modify everything.

#### Port Scanning

Attackers scan your device for
open ports
— like open doors. If they find port 445 (SMB) open, they can attempt exploits like EternalBlue (used by WannaCry ransomware).

#### Rogue DHCP Server

The attacker sets up a fake DHCP server that hands out malicious IP addresses. Victims are redirected to fake websites that look identical to real ones (phishing).

#### SMB Relay

Attackers intercept Windows login hashes and relay them to other devices on the network, gaining access without needing a password.

## 🛡️ Defensive Measures You'll Learn

- Use HTTPS everywhere
— encrypts your traffic, even on public WiFi
- Enable Client Isolation
— prevents devices on public networks from talking to each other
- Keep devices patched
— most exploits target unpatched vulnerabilities
- Use a VPN
— encrypts all traffic from your device to the VPN server
- Turn off file sharing
— SMB/NetBIOS are common attack vectors
## 📊 Example Output

```
[14:32:05] 🔍 Scanning network...
[14:32:08] 📋 Found 5 devices:
  - 192.168.1.1 (Router)
  - 192.168.1.100 (iPhone)
  - 192.168.1.101 (MacBook)
  - 192.168.1.102 (Windows PC)  ← Target
  - 192.168.1.103 (Android)

[14:32:15] 🔵 Starting passive sniffing...
[14:32:18] 🌐 DNS Query: facebook.com
[14:32:20] 🌐 DNS Query: netflix.com
[14:32:25] 🔓 Plaintext password: "password123" on http://test.com/login

[14:32:30] 🟡 Starting active attacks on 192.168.1.102...
[14:32:32] 🔍 Port scan: Found 3 open ports
  - Port 22 (SSH)
  - Port 80 (HTTP)
  - Port 445 (SMB) ← VULNERABLE

[14:32:40] 🔴 Starting high risk exploitation...
[14:32:42] 💀 EternalBlue vulnerability detected!
[14:32:45] 💀 SYSTEM COMPROMISED! Remote shell acquired.
```

## ⚠️ Legal & Ethical Disclaimer

```
THIS TOOL IS FOR EDUCATIONAL PURPOSES ONLY.

By using this software, you agree to:
1. Only test networks you OWN or have EXPLICIT WRITTEN PERMISSION to test
2. NOT use this tool for illegal, malicious, or unauthorized activities
3. Accept full responsibility for your actions

Unauthorized use is illegal under:
- CFAA (US Computer Fraud and Abuse Act)
- EU Cybersecurity Act
- Similar laws worldwide

The authors are not responsible for any misuse or damage caused by this tool.
```

## 🧠 Why I Built This

I created
wifi-shadow
because
most people don't understand how vulnerable they are on public WiFi
. This tool visualizes what an attacker can do — turning abstract cybersecurity concepts into
real, observable demonstrations
.

It's designed for:

- 🎓
Students
learning cybersecurity
- 🛡️
IT Administrators
testing network security
- 👨‍💻
Developers
understanding network protocols
- 🔬
Researchers
demonstrating attack vectors
## 📚 Resources

- OWASP Top 10
— Common web vulnerabilities
- MITRE ATT&CK
— Adversarial tactics and techniques
- Wireshark Documentation
— Packet analysis
- Scapy Documentation
— Packet manipulation
## 🤝 Contributing

Contributions are welcome! Here's how:

- Fork the repository
- Create a new branch (
git checkout -b feature/amazing-feature
)
- Commit your changes (
git commit -m 'Add amazing feature'
)
- Push to the branch (
git push origin feature/amazing-feature
)
- Open a Pull Request

## 🌟 Show Your Support

If you found this project useful or educational:

- ⭐ Star this repository
- 📢 Share it with others
- 🐛 Report issues or suggest features
## 📬 Contact

- Author:
Dipesh Pokhrel
- GitHub:
letxworld
- Email:
letxworld@gmail.com
Remember:
With great power comes great responsibility. Use this tool to
learn
,
educate
, and
protect
— not to harm. 🛡️

Made with ❤️ for cybersecurity education
