# Phone Touch Mouse

Turn your phone into a wireless touchpad for your computer. Run a small Python server on the computer, open the pairing URL on your phone, then use the phone screen to move and click the computer's mouse.

## Features

- Local-network connection (phone and computer on the same Wi-Fi)
- Pairing token in the URL, generated each time the server starts
- One-finger cursor movement and tap-to-left-click
- Two-finger scrolling
- Dedicated left-click and right-click buttons
- Adjustable pointer speed and a few keyboard shortcut buttons
- QR code displayed on the local page

## Requirements

- Python 3.10+
- Computer and phone connected to the same trusted Wi-Fi network
- Windows, macOS, or Linux desktop session where PyAutoGUI can control the mouse

## Run it

### Windows

1. Install Python 3.10 or newer from [python.org](https://www.python.org/downloads/). On Windows, enable **Add Python to PATH**.
2. Extract this project folder.
3. Open PowerShell in the project folder and run:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   python app.py
   ```

4. The server prints a phone URL and attempts to open a local status page in your default browser.
5. On your phone, scan the QR code on the computer's local page, or type the phone URL printed in the terminal. Keep both devices on the same Wi-Fi network.
6. If Windows Firewall asks, allow Python on **Private networks only**. Do not expose this port to public networks or forward it from your router.

If PowerShell blocks activation, you can skip activation and run:
`.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
then
`.\.venv\Scripts\python.exe app.py`

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

On macOS, you may need to grant your terminal/Python process **Accessibility** permission in System Settings → Privacy & Security → Accessibility. On Linux, this generally requires a graphical desktop session; Wayland desktop environments may restrict simulated mouse input.

## How to use

- Drag one finger across the large touchpad area to move the cursor.
- Tap the pad to left-click.
- Use the Left click / Right click buttons for explicit clicks.
- Drag two fingers vertically to scroll.
- Adjust pointer speed with the slider.
- Move the physical mouse to the top-left corner to trigger PyAutoGUI's failsafe if you need to stop mouse actions quickly.
- Press `Ctrl+C` in the terminal to shut down the server.

## Security notes

This is a small personal-use tool, not a hardened remote-access product.

- The pairing token is randomly generated at startup. Treat the URL and QR code like a password.
- Only run it on a trusted private network. Do not port-forward the server or expose it to the public internet.
- The server binds to all local interfaces so your phone can reach it, but socket connections require the pairing token.
- The URL uses plain HTTP on your local network, so use trusted Wi-Fi and stop the app when finished.
- The token changes each time the app restarts.
- `pyautogui.FAILSAFE` is enabled. Move the physical mouse to the upper-left corner to trigger it.

## Troubleshooting

**Phone cannot open the URL**
- Check that both devices are on the same Wi-Fi.
- Use the LAN URL printed in the terminal, not `127.0.0.1` or `localhost`.
- Guest Wi-Fi, client isolation, VPNs, and some mesh/router settings can block device-to-device traffic.
- Allow Python through the computer's private-network firewall for port `8765`.

**Page opens but the cursor does not move**
- Check macOS Accessibility permissions.
- Make sure the computer has an active desktop session.
- On Linux/Wayland, try an X11 session if PyAutoGUI cannot control the pointer.

**QR code not visible**
- Open the computer's local page with the token URL printed in the terminal. The QR code is served from `/qr.png?token=...`.

## Project structure

```text
phone-touch-mouse/
├── app.py
├── requirements.txt
├── templates/
│   ├── index.html
│   └── pairing_error.html
├── static/
│   ├── app.js
│   └── style.css
├── .gitignore
└── README.md
```

## License

MIT — see `LICENSE`.
