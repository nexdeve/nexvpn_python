<div align="center">

<img src="https://img.shields.io/badge/nexvpn-1.0.0-blue?style=for-the-badge&logo=python&logoColor=white" />

# nexvpn

**Python OpenVPN wrapper — easy VPN connection management for desktop & server**

[![PyPI](https://img.shields.io/pypi/v/nexvpn?style=flat-square&color=blue)](https://pypi.org/project/nexvpn)
[![Python](https://img.shields.io/badge/Python-3.8+-yellow?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue?style=flat-square)](https://opensource.org/licenses/Apache-2.0)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS-lightgrey?style=flat-square)](https://github.com/nexdeve/nexvpn_python)

[Installation](#-installation) · [Usage](#-usage) · [API](#-api-reference) · [Android](https://github.com/nexdeve/nexvpn) · [Flutter](https://github.com/nexdeve/nexvpn_flutter)

</div>

---

## ✨ Features

- 🐍 **Pure Python** — zero dependencies beyond the standard library
- 🔄 **Callback-based** — `on_connected`, `on_stopped`, `on_error`, `on_speed_update`
- 📡 **Live stats** — real-time download/upload speed via `/proc/net/dev`
- 🔒 **Context manager** — use with `with NexVpn() as vpn:` for auto-cleanup
- 💻 **Desktop & server** — works anywhere OpenVPN is installed

---

## 📦 Installation

```bash
pip install nexvpn
```

**Requires:** OpenVPN installed on the system
```bash
# Ubuntu / Debian
sudo apt install openvpn

# macOS
brew install openvpn
```

---

## 💡 Usage

### Basic

```python
from nexvpn import NexVpn, VpnStats
import time

vpn = NexVpn()
vpn.attach_from_file("server.ovpn", username="user", password="pass")

vpn.on_connected    = lambda:   print("Connected!")
vpn.on_stopped      = lambda:   print("Disconnected.")
vpn.on_status       = lambda s: print(f"Status: {s}")
vpn.on_error        = lambda e: print(f"Error: {e}")
vpn.on_speed_update = lambda s: print(
    f"DL: {VpnStats.format_speed(s.download_speed)}  "
    f"UL: {VpnStats.format_speed(s.upload_speed)}"
)

vpn.start()

try:
    time.sleep(60)
finally:
    vpn.stop()
```

### Context manager

```python
from nexvpn import NexVpn
import time

with NexVpn() as vpn:
    vpn.attach_from_file("server.ovpn", username="user", password="pass")
    vpn.on_connected = lambda: print("Connected!")
    vpn.start()
    time.sleep(60)
# auto-disconnects here
```

### From string config

```python
from nexvpn import NexVpn

config = """
client
dev tun
proto udp
remote vpn.example.com 1194
...
"""

vpn = NexVpn()
vpn.attach_from_string(config, username="user", password="pass")
vpn.start()
```

---

## 📖 API Reference

### Profile

| Method | Description |
|--------|-------------|
| `attach_from_file(path, username, password)` | Load `.ovpn` file from disk |
| `attach_from_string(config, username, password)` | Load `.ovpn` from string |

### Control

| Method | Description |
|--------|-------------|
| `start()` | Start VPN connection (non-blocking) |
| `stop()` | Stop VPN connection |
| `is_connected()` | Returns `True` if connected |
| `state` | Current `VpnState` enum value |
| `stats` | Current `VpnStats` object |

### Callbacks

| Attribute | Signature | Triggered |
|-----------|-----------|-----------|
| `on_connected` | `() -> None` | Tunnel established |
| `on_stopped` | `() -> None` | VPN stopped |
| `on_status` | `(str) -> None` | State transitions |
| `on_error` | `(str) -> None` | Errors |
| `on_speed_update` | `(VpnStats) -> None` | Every second |

### VpnStats

```python
stats.download_bytes   # Total bytes downloaded (int)
stats.upload_bytes     # Total bytes uploaded (int)
stats.download_speed   # Bytes/sec download (int)
stats.upload_speed     # Bytes/sec upload (int)

VpnStats.format_speed(stats.download_speed)  # "1.5 MB/s"
VpnStats.format_bytes(stats.download_bytes)  # "256 MB"
```

### VpnState enum

```python
from nexvpn import VpnState

VpnState.DISCONNECTED
VpnState.CONNECTING
VpnState.CONNECTED
VpnState.DISCONNECTING
VpnState.ERROR
```

---

## 🌐 Also Available

| Platform | Package |
|----------|---------|
| 🤖 Android | [nexvpn](https://github.com/nexdeve/nexvpn) — `ai.nextech:nexvpn:1.0.0` |
| 💙 Flutter | [nexvpn_flutter](https://github.com/nexdeve/nexvpn_flutter) — pub.dev |
| 🐍 Python (this) | `pip install nexvpn` |

---

## 📄 License

```
Copyright 2026 NexTech — Apache License 2.0
http://www.apache.org/licenses/LICENSE-2.0
```

<div align="center">
Made with ❤️ by <a href="https://github.com/nexdeve">NexDeve</a>
</div>
