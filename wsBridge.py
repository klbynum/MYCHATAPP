# Bridges a browser WebSocket to your newline-delimited TCP chat server.
# One WebSocket connection ↔ one TCP connection.

import asyncio
import argparse
import socket
import websockets

CONNECT_TIMEOUT = 5

async def handle_client(websocket, path, tcp_host, tcp_port):
    # Open TCP connection to the chat server for each WS client
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(tcp_host, tcp_port),
            timeout=CONNECT_TIMEOUT,
        )
    except Exception as e:
        await websocket.send(f"[bridge] TCP connect failed: {e}")
        await websocket.close()
        return

    async def tcp_to_ws():
        try:
            buf = b""
            while True:
                chunk = await reader.read(4096)
                if not chunk:
                    # Server closed
                    await websocket.send("[bridge] TCP server closed connection.")
                    await websocket.close()
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    await websocket.send(line.decode(errors="replace"))
        except (asyncio.CancelledError, ConnectionError):
            pass
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    async def ws_to_tcp():
        try:
            async for msg in websocket:
                # Forward any text from the browser to TCP with newline
                if isinstance(msg, bytes):
                    data = msg
                else:
                    data = msg.encode()
                writer.write(data + b"\n")
                await writer.drain()
        except (asyncio.CancelledError, ConnectionError):
            pass
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    # Pump both directions concurrently
    t1 = asyncio.create_task(tcp_to_ws())
    t2 = asyncio.create_task(ws_to_tcp())
    done, pending = await asyncio.wait({t1, t2}, return_when=asyncio.FIRST_COMPLETED)
    for t in pending:
        t.cancel()

async def main():

    parser = argparse.ArgumentParser(description="WebSocket ↔ TCP bridge")
    parser.add_argument("--tcp-host", default="127.0.0.1")
    parser.add_argument("--tcp-port", type=int, default=5050)
    parser.add_argument("--ws-host", default="127.0.0.1")
    parser.add_argument("--ws-port", type=int, default=8765)
    args = parser.parse_args()

    async def ws_handler(websocket, path):
        await handle_client(websocket, path, args.tcp_host, args.tcp_port)

    print(f"[bridge] Listening WebSocket on {args.ws_host}:{args.ws_port} → TCP {args.tcp_host}:{args.tcp_port}")
    async with websockets.serve(ws_handler, args.ws_host, args.ws_port, ping_interval=20, ping_timeout=20):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[bridge] Shutting down.")