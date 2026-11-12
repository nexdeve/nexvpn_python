import os
import tempfile
import pytest
from nexvpn import NexVpn, VpnState, VpnStats


def test_vpn_state_enum():
    assert VpnState.DISCONNECTED.value == "disconnected"
    assert VpnState.CONNECTING.value == "connecting"
    assert VpnState.CONNECTED.value == "connected"
    assert VpnState.DISCONNECTING.value == "disconnecting"
    assert VpnState.ERROR.value == "error"


def test_vpn_stats_init_and_repr():
    stats = VpnStats(download_bytes=1024, upload_bytes=2048,
                     download_speed=512, upload_speed=256)
    assert stats.download_bytes == 1024
    assert stats.upload_bytes == 2048
    assert stats.download_speed == 512
    assert stats.upload_speed == 256
    rep = repr(stats)
    assert "VpnStats" in rep
    assert "total=" in rep


def test_vpn_stats_formatting():
    # format_speed
    assert VpnStats.format_speed(500) == "500 B/s"
    assert VpnStats.format_speed(1024 * 2) == "2.0 KB/s"
    assert VpnStats.format_speed(1024 * 1024 * 3) == "3.0 MB/s"
    assert VpnStats.format_speed(1024 * 1024 * 1024 * 2) == "2.0 GB/s"

    # format_bytes
    assert VpnStats.format_bytes(500) == "500 B"
    assert VpnStats.format_bytes(1024 * 2) == "2.0 KB"
    assert VpnStats.format_bytes(1024 * 1024 * 5) == "5.0 MB"
    assert VpnStats.format_bytes(1024 * 1024 * 1024 * 4) == "4.0 GB"


def test_nexvpn_init():
    vpn = NexVpn(openvpn_bin="openvpn")
    assert vpn.state == VpnState.DISCONNECTED
    assert not vpn.is_connected()
    assert vpn.stats.download_bytes == 0
    assert "NexVpn(state=disconnected" in repr(vpn)


def test_nexvpn_attach_from_string():
    vpn = NexVpn()
    dummy_cfg = "client\ndev tun\nproto udp"
    res = vpn.attach_from_string(dummy_cfg, username="usr", password="pwd")
    assert res is vpn
    assert vpn._config == dummy_cfg
    assert vpn._username == "usr"
    assert vpn._password == "pwd"


def test_nexvpn_attach_from_file():
    vpn = NexVpn()
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("client\ndev tun\nremote 1.2.3.4 1194\n")
        temp_path = f.name
    try:
        res = vpn.attach_from_file(temp_path, username="myuser", password="mypassword")
        assert res is vpn
        assert "remote 1.2.3.4" in vpn._config
        assert vpn._username == "myuser"
        assert vpn._password == "mypassword"
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_nexvpn_start_without_config_raises():
    vpn = NexVpn()
    with pytest.raises(ValueError, match="No VPN profile attached"):
        vpn.start()


def test_nexvpn_status_parser():
    vpn = NexVpn()
    assert vpn._parse_status("2026-11-12 Resolving host") == "Resolving hostname..."
    assert vpn._parse_status("2026-11-12 TCP/UDP connecting") == "Opening connection..."
    assert vpn._parse_status("2026-11-12 TLS handshake started") == "TLS handshake..."
    assert vpn._parse_status("2026-11-12 Peer Connection established") == "Peer connected"
    assert vpn._parse_status("2026-11-12 OPTIONS IMPORT done") == "Importing options..."
    assert vpn._parse_status("2026-11-12 route_ipv6_net active") == "Setting up routes..."
    assert vpn._parse_status("random log line") is None


def test_nexvpn_state_callbacks():
    vpn = NexVpn()
    connected_called = False
    stopped_called = False

    def on_conn():
        nonlocal connected_called
        connected_called = True

    def on_stop():
        nonlocal stopped_called
        stopped_called = True

    vpn.on_connected = on_conn
    vpn.on_stopped = on_stop

    vpn._set_state(VpnState.CONNECTED)
    assert connected_called is True
    assert vpn.is_connected()

    vpn._set_state(VpnState.DISCONNECTED)
    assert stopped_called is True
    assert not vpn.is_connected()


def test_nexvpn_context_manager():
    with NexVpn() as vpn:
        assert vpn.state == VpnState.DISCONNECTED
