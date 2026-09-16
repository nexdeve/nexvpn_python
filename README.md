<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:172554,100:3b82f6&height=160&section=header&text=nexvpn&fontSize=52&fontColor=ffffff&animation=fadeIn&fontAlignY=42&desc=Python%20OpenVPN%20Wrapper%20Library&descAlignY=62&descColor=93c5fd" />

[![PyPI](https://img.shields.io/pypi/v/nexvpn?style=for-the-badge&color=3776AB&logo=python&logoColor=white)](https://pypi.org/project/nexvpn)
[![Python](https://img.shields.io/badge/Python-3.8+-F7DC6F?style=for-the-badge&logo=python&logoColor=black)](https://python.org)
[![License](https://img.shields.io/badge/License-Apache_2.0-6366f1?style=for-the-badge)](https://opensource.org/licenses/Apache-2.0)
[![Platform](https://img.shields.io/badge/Linux%20%7C%20macOS-lightgrey?style=for-the-badge)](https://github.com/nexdeve/nexvpn_python)
[![Author](https://img.shields.io/badge/By-NexDeve-076AF4?style=for-the-badge)](https://nexdeve.com)

**Python OpenVPN wrapper — easy VPN management for desktop & server**
Made by [nexdeve.com](https://nexdeve.com)

[Installation](#-installation) · [Usage](#-usage) · [API](#-api-reference) · [Android](https://github.com/nexdeve/nexvpn) · [Flutter](https://github.com/nexdeve/nexvpn_flutter)

</div>

---

## ✨ Features

- 🐍 **Pure Python** — zero extra dependencies
- 🔄 **Callback-based** — `on_connected`, `on_error`, `on_speed_update`
- 📡 **Live Stats** — real-time speed via `/proc/net/dev`
- 🔒 **Context Manager** — auto-cleanup with `with NexVpn()`
- 💻 **Desktop & Server** — works anywhere OpenVPN is installed

---

## 📦 Installation

```bash
pip install nexvpn
```

**System requirement — OpenVPN:**
```bash
sudo apt install openvpn      # Ubuntu/Debian
brew install openvpn          # macOS
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
time.sleep(60)
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
# auto-disconnects
```

---

## 📖 API Reference

| Method | Description |
|--------|-------------|
| `attach_from_file(path, username, password)` | Load `.ovpn` from disk |
| `attach_from_string(config, username, password)` | Load from string |
| `start()` | Start VPN (non-blocking) |
| `stop()` | Stop VPN |
| `is_connected()` | `True` if connected |
| `state` | Current `VpnState` |
| `stats` | Current `VpnStats` |

### Callbacks

| Attribute | Triggered |
|-----------|-----------|
| `on_connected` | Tunnel established |
| `on_stopped` | VPN stopped |
| `on_status(str)` | State transitions |
| `on_error(str)` | Errors |
| `on_speed_update(VpnStats)` | Every second |

### VpnStats

```python
VpnStats.format_speed(stats.download_speed)  # "1.5 MB/s"
VpnStats.format_bytes(stats.download_bytes)  # "256 MB"
```

---

## 🌐 NexVPN Ecosystem

| Platform | Repo | Install |
|----------|------|---------|
| 🤖 Android | [nexvpn](https://github.com/nexdeve/nexvpn) | `ai.nextech:nexvpn:1.0.0` |
| 💙 Flutter | [nexvpn_flutter](https://github.com/nexdeve/nexvpn_flutter) | `nexvpn_flutter: ^1.0.0` |
| 🐍 Python (this) | [nexvpn_python](https://github.com/nexdeve/nexvpn_python) | `pip install nexvpn` |

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:3b82f6,100:172554&height=80&section=footer" />

Made with ❤️ by [**NexDeve**](https://nexdeve.com) · [nexdeve.com](https://nexdeve.com) · [Telegram](https://t.me/+c34_uTIBJEpkZGM9)

</div>
