#!/usr/bin/env python3
"""
TCP Client
- Connects to the threaded server and exchanges text messages.
- Supports interactive mode and demo mode.
- Displays clear distinction between sent and received messages.
"""

import socket
import threading
import time
import argparse
from datetime import datetime

HOST = "172.31.20.35" # LAN IP ADDRESS
PORT = 5050
CONNECT_TIMEOUT = 5

# Color formatting (optional, works in most terminals)
COLOR_SENT = "\033[92m"
COLOR_RECEIVED = "\033[94m"
COLOR_RESET = "\033[0m"

def timestamp():
    return datetime.now().strftime("%H:%M:%S")

def recv_loop(sock, stop_event):
    """Receive messages from the server in a background thread."""
    sock.settimeout(1.0)
    buffer = b""
    try:
        while not stop_event.is_set():
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    print(f"[{timestamp()}] [client] Server closed connection.")
                    break
                buffer += chunk
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    print(f"{COLOR_RECEIVED}[{timestamp()}] [RECEIVED] {line.decode().rstrip()}{COLOR_RESET}")
            except socket.timeout:
                continue
            except ConnectionResetError:
                print(f"[{timestamp()}] [client] Connection reset by server.")
                break
    finally:
        stop_event.set()

def interactive_send(sock, stop_event):
    """Allow user to type messages manually."""
    try:
        while not stop_event.is_set():
            line = input(f"{COLOR_SENT}[you] {COLOR_RESET}")
            if not line:
                continue
            sock.sendall((line + "\n").encode())
            if line.strip() == "/quit":
                break
    except (BrokenPipeError, ConnectionResetError):
        print("[client] Connection closed.")
    finally:
        stop_event.set()

def demo_send(sock, stop_event):
    """Automatically send demo messages."""
    messages = ["Hello, server!", "/time", "/clients", "Testing 123", "/quit"]
    for msg in messages:
        if stop_event.is_set():
            break
        print(f"{COLOR_SENT}[{timestamp()}] [SENT] {msg}{COLOR_RESET}")
        sock.sendall((msg + "\n").encode())
        time.sleep(0.5)
    stop_event.set()

def main():
    parser = argparse.ArgumentParser(description="TCP Client")
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", type=int, default=PORT)
    parser.add_argument("--demo", action="store_true", help="Run in demo mode")
    args, _ = parser.parse_known_args()

    try:
        sock = socket.create_connection((args.host, args.port), timeout=CONNECT_TIMEOUT)
        print(f"[{timestamp()}] [client] Connected to {args.host}:{args.port}")
    except Exception as e:
        print(f"[{timestamp()}] [client] Connection failed: {e}")
        return

    stop_event = threading.Event()
    threading.Thread(target=recv_loop, args=(sock, stop_event), daemon=True).start()

    if args.demo:
        demo_send(sock, stop_event)
    else:
        print("Type messages and press Enter. Use /quit to exit.\n")
        interactive_send(sock, stop_event)

    sock.close()
    print(f"[{timestamp()}] [client] Disconnected.")

main()
