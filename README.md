# MYCHATAPP  
A simple chat system that uses a TCP server, a TCP client, and a WebSocket–to–TCP bridge.  
The bridge allows a web browser to talk to the raw TCP chat server by converting WebSocket messages into TCP messages.

This project includes:

- A multithreaded TCP chat server  
- A TCP client program (interactive or demo mode)  
- A WebSocket bridge  
- A browser Web GUI (index.html)

Everything works together to show how a browser can connect to a normal TCP server that does not support WebSockets.

---

# 1. Project Overview

MYCHATAPP is a basic messaging system designed for learning and demonstration.  
It shows how to:

- Build a TCP server that handles multiple clients  
- Build a TCP client for testing  
- Use a WebSocket bridge to connect a browser to a TCP server  
- Display chat messages in a simple web interface  

The browser sends WebSocket messages to the bridge, and the bridge forwards them to the TCP server as normal TCP lines.  
The server responds, and the bridge sends the responses back to the browser.

---

# 2. File Structure



---

# 3. How Each Component Works

## A. TCP Server (server.py)
- Listens on a TCP port (default 5050)  
- Accepts many clients at the same time  
- Prints all incoming messages  
- Supports the following commands:

| Command | Description |
|---------|-------------|
| `/time` | Returns server time |
| `/clients` | Shows number of connected clients |
| `/quit` | Closes the connection |

All other messages are broadcast to other clients.

## B. TCP Client (client.py)
- Connects to the TCP server  
- Can run in interactive mode or demo mode  
- Shows sent messages in green and received messages in blue  
- Sends text lines and receives line-based responses  
- Commands work the same as in the server

Run with demo mode:


## C. WebSocket Bridge (wsBridge.py)
- Accepts WebSocket connections from browsers  
- Creates a TCP connection to the server for each browser  
- Forwards WebSocket messages → TCP messages  
- Forwards TCP messages → WebSocket messages  
- Uses newline-delimited messages  
- Keeps both sides in sync until either side disconnects  

Browser connects to:
```ws://localhost:8765```


Bridge connects to TCP server at: ```127.0.0.1:5050```


## D. Web GUI (index.html)
- Connects to the WebSocket bridge  
- Shows sent and received messages with colored tags  
- Supports demo mode  
- Sends raw text to the server through the bridge  
- Displays output from server line by line  

---

# 4. How to Run the Whole System
Follow these steps in order.

### Step 1 — Start the TCP Server

```python server.py```

You should see:
```[server] Listening on 0.0.0.0:5050```


### Step 2 — Start the WebSocket Bridge
```python wsBridge.py --tcp-host 127.0.0.1 --tcp-port 5050 --ws-host 0.0.0.0 --ws-port 8765```


Console should show:
 Listening WebSocket on 0.0.0.0:8765 -> TCP 127.0.0.1:5050

 
### Step 3 — Open the Web GUI
Open `index.html` in your browser.

### Step 4 — Connect from the GUI
- Enter `ws://localhost:8765`  
- Press Connect  
- Send messages or run Demo  
- Use `/quit` to disconnect

---

# 5. Example Message Flow

1. Browser sends: `Hello`  
2. Bridge receives it and converts to TCP  
3. Server logs it  
4. Server broadcasts response  
5. Bridge sends response back to browser  
6. Browser displays it in the chat log  

---

# 6. Requirements

- Python 3.8 or above  
- websockets library  

Install with:
```pip install websockets```


You can open `index.html` directly or serve it with a local file server.

---

# 7. Troubleshooting

### Bridge cannot connect to TCP server
Check:
- Server is running  
- Correct IP and port  
- Firewall settings  

### Browser cannot connect to WebSocket
Check:
- Correct WebSocket URL  
- Bridge is running  
- Port 8765 is open  

### Messages do not appear
Make sure every message ends with a newline.  
The bridge and server both depend on newline splitting.

---

# 8. Author

Created by  
**Kemon Bynum**








