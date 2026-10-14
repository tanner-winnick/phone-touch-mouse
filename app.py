import io
import os
import secrets
import socket
import threading
import webbrowser
from urllib.parse import quote

import pyautogui
import qrcode
from flask import Flask, abort, jsonify, render_template, request, send_file
from flask_socketio import SocketIO, emit

# Safety defaults: the app is intended for your own trusted home/local network.
# Keep the pairing token private and stop the server when you're finished.
PAIR_TOKEN = secrets.token_urlsafe(18)
PORT = int(os.environ.get("PORT", "8765"))
HOST = "0.0.0.0"

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_urlsafe(32)
socketio = SocketIO(app, async_mode="threading", cors_allowed_origins=[])

pyautogui.FAILSAFE = True  # Move the physical mouse to the top-left to trigger PyAutoGUI failsafe.
pyautogui.PAUSE = 0.005

def get_lan_ip():
    """Best-effort local IPv4 address; does not send data over the test connection."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("192.0.2.1", 80))
        return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()

LAN_IP = get_lan_ip()
PHONE_URL = f"http://{LAN_IP}:{PORT}/?token={quote(PAIR_TOKEN)}"

def valid_token():
    return secrets.compare_digest(
        request.args.get("token", ""),
        PAIR_TOKEN
    )

@app.get("/")
def index():
    if not valid_token():
        return render_template("pairing_error.html"), 403
    return render_template("index.html", token=PAIR_TOKEN, phone_url=PHONE_URL)

@app.get("/qr.png")
def qr_image():
    if not valid_token():
        abort(403)
    image = qrcode.make(PHONE_URL)
    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return send_file(output, mimetype="image/png")

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

@socketio.on("connect")
def on_connect(auth=None):
    token = (auth or {}).get("token", "")
    if not secrets.compare_digest(token, PAIR_TOKEN):
        return False
    emit("connection_status", {"connected": True})

@socketio.on("move")
def on_move(data):
    if not isinstance(data, dict):
        return
    try:
        dx = max(-300, min(300, float(data.get("dx", 0))))
        dy = max(-300, min(300, float(data.get("dy", 0))))
        speed = max(0.2, min(3.0, float(data.get("speed", 1.0))))
        x, y = pyautogui.position()
        pyautogui.moveTo(
            max(0, min(pyautogui.size().width - 1, x + dx * speed)),
            max(0, min(pyautogui.size().height - 1, y + dy * speed)),
            _pause=False
        )
    except (ValueError, TypeError, OSError):
        pass

@socketio.on("click")
def on_click(data=None):
    button = (data or {}).get("button", "left")
    if button not in ("left", "right", "middle"):
        button = "left"
    pyautogui.click(button=button)

@socketio.on("scroll")
def on_scroll(data):
    try:
        amount = max(-10, min(10, int(data.get("amount", 0))))
        pyautogui.scroll(amount)
    except (ValueError, TypeError, AttributeError):
        pass

@socketio.on("key")
def on_key(data):
    # Small allowlist: phone can only trigger these convenience keys.
    key = (data or {}).get("key", "")
    allowed = {"enter", "escape", "backspace", "space", "tab", "up", "down", "left", "right"}
    if key in allowed:
        pyautogui.press(key)

def open_desktop_page():
    # Open the status/QR page locally; token is only shown in this local window/terminal.
    webbrowser.open(f"http://127.0.0.1:{PORT}/?token={quote(PAIR_TOKEN)}")

if __name__ == "__main__":
    print("\nPhone Touch Mouse")
    print("-----------------")
    print(f"Open on your computer: http://127.0.0.1:{PORT}/?token={PAIR_TOKEN}")
    print(f"On your phone (same Wi-Fi): {PHONE_URL}")
    print("If the phone cannot connect, allow Python through your computer's private-network firewall.")
    print("Stop the server with Ctrl+C when finished.\n")
    threading.Timer(1.0, open_desktop_page).start()
    socketio.run(app, host=HOST, port=PORT, debug=False, allow_unsafe_werkzeug=True)
