"""
NexVPN — Python OpenVPN wrapper library
Easy VPN connection management for desktop & server
"""

import subprocess
import threading
import time
import re
import os
import signal
from enum import Enum
from typing import Callable, Optional


class VpnState(Enum):
    DISCONNECTED  = "disconnected"
    CONNECTING    = "connecting"
    CONNECTED     = "connected"
    DISCONNECTING = "disconnecting"
    ERROR         = "error"


class VpnStats:
    def __init__(self, download_bytes=0, upload_bytes=0,
                 download_speed=0, upload_speed=0):
        self.download_bytes = download_bytes
        self.upload_bytes   = upload_bytes
        self.download_speed = download_speed
        self.upload_speed   = upload_speed

    @staticmethod
    def format_speed(bps: int) -> str:
        if bps < 1024:            return f"{bps} B/s"
        if bps < 1024**2:         return f"{bps/1024:.1f} KB/s"
        if bps < 1024**3:         return f"{bps/1024**2:.1f} MB/s"
        return f"{bps/1024**3:.1f} GB/s"

    @staticmethod
    def format_bytes(b: int) -> str:
        if b < 1024:      return f"{b} B"
        if b < 1024**2:   return f"{b/1024:.1f} KB"
        if b < 1024**3:   return f"{b/1024**2:.1f} MB"
        return f"{b/1024**3:.1f} GB"

    def __repr__(self):
        return (f"VpnStats(dl={self.format_speed(self.download_speed)}, "
                f"ul={self.format_speed(self.upload_speed)}, "
                f"total={self.format_bytes(self.download_bytes + self.upload_bytes)})")


class NexVpn:
    """
    NexVPN — Simple Python OpenVPN client

    Usage:
        vpn = NexVpn()
        vpn.attach_from_file("server.ovpn", username="user", password="pass")
        vpn.on_connected    = lambda:      print("Connected!")
        vpn.on_stopped      = lambda:      print("Stopped.")
        vpn.on_status       = lambda s:    print("Status:", s)
        vpn.on_error        = lambda e:    print("Error:", e)
        vpn.on_speed_update = lambda st:   print(st)
        vpn.start()
        # ... later ...
        vpn.stop()
    """

    def __init__(self, openvpn_bin: str = "openvpn"):
        self.openvpn_bin = openvpn_bin
        self._config:   Optional[str] = None
        self._username: Optional[str] = None
        self._password: Optional[str] = None

        self._process:  Optional[subprocess.Popen] = None
        self._state     = VpnState.DISCONNECTED
        self._stats     = VpnStats()

        self._monitor_thread: Optional[threading.Thread] = None
        self._stats_thread:   Optional[threading.Thread] = None
        self._stop_event    = threading.Event()

        # Callbacks
        self.on_connected:    Optional[Callable]          = None
        self.on_stopped:      Optional[Callable]          = None
        self.on_status:       Optional[Callable[[str], None]]      = None
        self.on_error:        Optional[Callable[[str], None]]      = None
        self.on_speed_update: Optional[Callable[[VpnStats], None]] = None

    # ── Profile ──────────────────────────────────────────────────────────────

    def attach_from_file(self, path: str,
                         username: str = "",
                         password: str = "") -> "NexVpn":
        with open(path, "r") as f:
            self._config = f.read()
        self._username = username
        self._password = password
        return self

    def attach_from_string(self, config: str,
                           username: str = "",
                           password: str = "") -> "NexVpn":
        self._config   = config
        self._username = username
        self._password = password
        return self

    # ── Control ───────────────────────────────────────────────────────────────

    def start(self) -> "NexVpn":
        if not self._config:
            raise ValueError("No VPN profile attached. Call attach_from_file() or attach_from_string() first.")
        if self._state in (VpnState.CONNECTED, VpnState.CONNECTING):
            return self

        self._stop_event.clear()
        self._set_state(VpnState.CONNECTING)

        # Write config to temp file
        import tempfile
        self._tmp_config = tempfile.NamedTemporaryFile(
            suffix=".ovpn", delete=False, mode="w")
        self._tmp_config.write(self._config)
        self._tmp_config.close()

        cmd = ["sudo", self.openvpn_bin, "--config", self._tmp_config.name,
               "--verb", "4"]

        if self._username and self._password:
            self._tmp_auth = tempfile.NamedTemporaryFile(
                suffix=".txt", delete=False, mode="w")
            self._tmp_auth.write(f"{self._username}\n{self._password}\n")
            self._tmp_auth.close()
            os.chmod(self._tmp_auth.name, 0o600)
            cmd += ["--auth-user-pass", self._tmp_auth.name]

        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        self._monitor_thread = threading.Thread(
            target=self._monitor_output, daemon=True)
        self._monitor_thread.start()

        self._stats_thread = threading.Thread(
            target=self._stats_loop, daemon=True)
        self._stats_thread.start()

        return self

    def stop(self) -> "NexVpn":
        self._set_state(VpnState.DISCONNECTING)
        self._stop_event.set()

        if self._process and self._process.poll() is None:
            try:
                self._process.send_signal(signal.SIGTERM)
                self._process.wait(timeout=5)
            except Exception:
                self._process.kill()

        self._cleanup_temp_files()
        self._set_state(VpnState.DISCONNECTED)
        return self

    def is_connected(self) -> bool:
        return self._state == VpnState.CONNECTED

    @property
    def state(self) -> VpnState:
        return self._state

    @property
    def stats(self) -> VpnStats:
        return self._stats

    # ── Internal ─────────────────────────────────────────────────────────────

    def _monitor_output(self):
        try:
            for line in self._process.stdout:
                line = line.strip()
                if not line or self._stop_event.is_set():
                    break

                if "Initialization Sequence Completed" in line:
                    self._set_state(VpnState.CONNECTED)
                elif "AUTH_FAILED" in line:
                    self._set_state(VpnState.ERROR)
                    if self.on_error:
                        self.on_error("Authentication failed. Check username/password.")
                elif "SIGTERM" in line or "process exiting" in line:
                    pass
                elif any(k in line for k in ["TLS Error", "Connection refused", "read UDPv4"]):
                    if self.on_error:
                        self.on_error(line)
                else:
                    status = self._parse_status(line)
                    if status and self.on_status:
                        self.on_status(status)

        except Exception as e:
            if self.on_error:
                self.on_error(str(e))
        finally:
            if self._state not in (VpnState.DISCONNECTED, VpnState.ERROR):
                self._set_state(VpnState.DISCONNECTED)

    def _parse_status(self, line: str) -> Optional[str]:
        keywords = {
            "Resolving":         "Resolving hostname...",
            "TCP/UDP":           "Opening connection...",
            "TLS handshake":     "TLS handshake...",
            "Peer Connection":   "Peer connected",
            "OPTIONS IMPORT":    "Importing options...",
            "route_ipv6_net":    "Setting up routes...",
        }
        for k, v in keywords.items():
            if k in line:
                return v
        return None

    def _stats_loop(self):
        last_dl = last_ul = 0
        while not self._stop_event.is_set():
            time.sleep(1)
            if self._state != VpnState.CONNECTED:
                continue
            # Try to read /proc/net/dev for tun0 stats
            try:
                with open("/proc/net/dev") as f:
                    for ln in f:
                        if "tun" in ln:
                            parts = ln.split()
                            dl = int(parts[1])
                            ul = int(parts[9])
                            self._stats = VpnStats(
                                download_bytes=dl,
                                upload_bytes=ul,
                                download_speed=max(0, dl - last_dl),
                                upload_speed=max(0, ul - last_ul),
                            )
                            last_dl, last_ul = dl, ul
                            if self.on_speed_update:
                                self.on_speed_update(self._stats)
                            break
            except Exception:
                pass

    def _set_state(self, state: VpnState):
        self._state = state
        if state == VpnState.CONNECTED and self.on_connected:
            self.on_connected()
        elif state == VpnState.DISCONNECTED and self.on_stopped:
            self.on_stopped()

    def _cleanup_temp_files(self):
        for attr in ("_tmp_config", "_tmp_auth"):
            f = getattr(self, attr, None)
            if f:
                try:
                    os.unlink(f.name)
                except Exception:
                    pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.stop()

    def __repr__(self):
        return f"NexVpn(state={self._state.value}, stats={self._stats})"
