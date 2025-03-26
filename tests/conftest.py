# tests/conftest.py
import socket

def get_free_port():
    """Get a free port from the OS."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]
