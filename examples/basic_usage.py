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
    time.sleep(30)
finally:
    vpn.stop()
