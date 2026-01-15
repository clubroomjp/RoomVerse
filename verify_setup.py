import sys
import os
import time
from app.core.room_manager import room_manager
from app.core.cloudflared import CloudflaredTunnel
from app.core.discovery import MockDiscoveryClient

def test_sanitization():
    print("Testing Sanitization...")
    unsafe_input = "<script>alert('xss')</script>Hello"
    safe = room_manager.sanitize(unsafe_input)
    assert "<script>" not in safe
    assert "&lt;script&gt;" in safe
    print(f" PASS: {unsafe_input} -> {safe}")

def test_capacity():
    print("Testing Capacity...")
    room_manager._max_capacity = 2
    room_manager.visitors = {}
    
    assert room_manager.can_accept_visitor("v1")
    room_manager.register_visitor("v1", "Alice")
    assert room_manager.can_accept_visitor("v2")
    room_manager.register_visitor("v2", "Bob")
    
    assert not room_manager.can_accept_visitor("v3")
    print(" PASS: Room capacity enforced.")

def test_discovery():
    print("Testing Discovery Mock...")
    client = MockDiscoveryClient()
    assert client.announce("uuid", "url", {})
    rooms = client.list_rooms()
    assert len(rooms) > 0
    print(" PASS: Discovery Mock works.")

def test_cloudflared_binary():
    print("Testing cloudflared binary check...")
    tunnel = CloudflaredTunnel()
    # verify path logic
    path = tunnel.bin_path
    print(f" Binary path: {path}")
    
    # Check if download works (or file exists)
    # We will invoke ensure_cloudflared. 
    # NOTE: This might take time if downloading.
    try:
        tunnel.ensure_cloudflared()
        if os.path.exists(path):
            print(" PASS: cloudflared binary exists.")
        else:
            print(" FAIL: cloudflared binary missing after ensure.")
    except Exception as e:
        print(f" FAIL: ensure_cloudflared raised {e}")

if __name__ == "__main__":
    test_sanitization()
    test_capacity()
    test_discovery()
    test_cloudflared_binary()
