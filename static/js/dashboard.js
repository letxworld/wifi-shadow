/**
 * wifi-shadow Dashboard Client
 * Handles SocketIO communication, UI updates, and user interactions
 */

// Socket Connection
const socket = io();
const logOutput = document.getElementById('log-output');

//SocketIO Event Listeners 

socket.on('connect', () => {
    appendLog('info', '🟢 Connected to wifi-shadow server');
});

socket.on('disconnect', () => {
    appendLog('error', '🔴 Disconnected from server');
});

socket.on('log_message', (data) => {
    appendLog(data.level, `[${data.timestamp}] ${data.message}`);
});

socket.on('scan_done', (data) => {
    if (data.status === 'ok') {
        appendLog('info', `✅ Scan complete. Found ${data.count} devices.`);
        data.devices.forEach((dev, i) => {
            const host = dev.hostname || 'unknown';
            appendLog('device', `  ${i+1}. ${dev.ip} - ${dev.mac} (${host})`);
        });
        // Update target IP dropdown or suggest first found IP
        if (data.devices.length > 0) {
            const firstIp = data.devices[0].ip;
            document.getElementById('target-ip').value = firstIp;
            appendLog('info', `🎯 Target IP set to: ${firstIp}`);
        }
    } else if (data.status === 'no_devices') {
        appendLog('warn', '⚠️ No devices found. Check your interface and network.');
    } else {
        appendLog('error', `❌ Scan failed: ${data.message}`);
    }
});

socket.on('settings_saved', (data) => {
    const statusEl = document.getElementById('settings-status');
    if (data.status === 'ok') {
        statusEl.textContent = '✅ Applied';
        statusEl.style.color = '#34d399';
        setTimeout(() => { statusEl.textContent = ''; }, 3000);
    } else {
        statusEl.textContent = '❌ Error: ' + data.message;
        statusEl.style.color = '#f87171';
    }
});

socket.on('attack_result', (data) => {
    if (data.status === 'dry_run') {
        appendLog('warn', `🔒 [SAFE MODE] ${data.message}`);
    } else if (data.status === 'started') {
        appendLog('attack', `⚡ ${data.message}`);
    } else {
        appendLog('error', `❌ Attack failed: ${data.message}`);
    }
});

// ===== UI Helper Functions =====

/**
 * Append a message to the live log
 */
function appendLog(level, message) {
    const entry = document.createElement('div');
    entry.className = `log-${level}`;
    entry.textContent = message;
    logOutput.appendChild(entry);
    logOutput.scrollTop = logOutput.scrollHeight;
}

/**
 * Save settings from the dashboard to the server
 */
function saveSettings() {
    const settings = {
        target_ip: document.getElementById('target-ip').value.trim(),
        interface: document.getElementById('interface').value.trim(),
        gateway_ip: document.getElementById('gateway-ip').value.trim(),
        safe_mode: document.getElementById('safe-mode').checked
    };
    
    // Validate inputs
    if (!settings.target_ip) {
        document.getElementById('settings-status').textContent = '⚠️ Please enter a target IP';
        document.getElementById('settings-status').style.color = '#fbbf24';
        return;
    }
    if (!settings.interface) {
        document.getElementById('settings-status').textContent = '⚠️ Please enter a network interface';
        document.getElementById('settings-status').style.color = '#fbbf24';
        return;
    }
    
    socket.emit('save_settings', settings);
    document.getElementById('settings-status').textContent = '⏳ Saving...';
    document.getElementById('settings-status').style.color = '#fbbf24';
}

/**
 * Trigger network scan
 */
function scanNetwork() {
    appendLog('info', '🔍 Scanning network for devices...');
    socket.emit('scan_network');
}

/**
 * Start an attack demo
 */
function startAttack(type) {
    const target = document.getElementById('target-ip').value.trim() || '192.168.1.100';
    const safe = document.getElementById('safe-mode').checked;
    const labels = {
        passive: '🔵 Passive Spying',
        active: '🟡 Active Attacks',
        high: '🔴 High Risk Exploitation'
    };
    
    appendLog('info', `🚀 Triggering ${labels[type] || type} on ${target}`);
    appendLog('info', `   Safe mode: ${safe ? 'ON (dry-run)' : 'OFF (live)'}`);
    
    socket.emit('start_attack', {
        type: type,
        target_ip: target,
        safe_mode: safe
    });
}

/**
 * Clear the log output
 */
function clearLog() {
    logOutput.innerHTML = '';
    appendLog('info', '🧹 Log cleared');
}

/**
 * Auto-scan on page load (after a short delay)
 */
document.addEventListener('DOMContentLoaded', () => {
    // Show connecting state
    appendLog('info', '⏳ Connecting to server...');
    
    // Auto-scan after 2.5 seconds
    setTimeout(() => {
        scanNetwork();
    }, 2500);
});