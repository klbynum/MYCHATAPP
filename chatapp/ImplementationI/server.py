"""
TCP Server
- Accepts multiple clients concurrently using threading.
- Handles text messages, including simple commands.
- Demonstrates bidirectional communication.
"""

import socket
import threading
import time

HOST = "0.0.0.0"   # Localhost
PORT = 5050          # change this if needed
clients = []         # Track connected clients

def handle_client(conn, addr):
    # Handles one connected client
    print(f"[server] New connection from {addr}")
    conn.settimeout(60)
    clients.append(conn)

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                print(f"[server] {addr} disconnected.")
                break

            msg = data.decode().strip()
            print(f"[from {addr}] {msg}")

            # Simple commands
            if msg == "/time":
                response = time.strftime("%Y-%m-%d %H:%M:%S")
            elif msg == "/clients":
                response = f"Connected clients: {len(clients)}"
            elif msg == "/quit":
                response = "Goodbye!"
                conn.sendall((response + "\n").encode())
                break
            else:
                response = f"[{addr}] {msg}"
                # broadcast to all connected clients
                for c in clients:
                    if c != conn:
                        try:
                            c.sendall((response + "\n").encode())
                        except:
                            pass
            conn.sendall((response + "\n").encode())

    except ConnectionResetError:
        print(f"[server] Connection lost with {addr}")
    except Exception as e:
        print(f"[server] Error with {addr}: {e}")
    finally:
        if conn in clients:
            clients.remove(conn)
        conn.close()
        print(f"[server] Closed connection with {addr}")

def start_server():
    # Starts the TCP server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"[server] Listening on {HOST}:{PORT}")

        while True:
            try:
                conn, addr = s.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                thread.start()
            except Exception as e:
                print("[server] Accept error:", e)


start_server()
