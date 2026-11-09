A sample website for our solar-powered e-bike charging and lock station. Riders can create an account, register a bike by serial number, connect to the station, start and stop charging, and lock or unlock the bike and charger.

Status: prototype. The hardware is simulated in hardware.py (fake battery, fake locks). Later, the inside of that file gets replaced with real Raspberry Pi code, and the website stays the same.

What you need
- Python 3.10 or newer (python.org/downloads; on Windows, check "Add python.exe to PATH" during install)
- Git (git-scm.com)
- VS Code (code.visualstudio.com)
- A GitHub account that has been added to this repo (accept the invite email first)

Get the code
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO

Then open that folder in VS Code (File > Open Folder).

Set up and run

Run these in the VS Code terminal (Terminal > New Terminal), from the folder that contains app.py.

Windows (PowerShell)

py -m venv .venv
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.venv\Scripts\activate
pip install -r requirements.txt
python app.py

Mac

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py

When the terminal says "Running on http://127.0.0.1:5000", open that address in your browser. Stop the site with Ctrl+C.

You only need to create the virtual environment (.venv) once. Next time, just activate it and run python app.py.

Try it out
1. Click Create an account, then log in.
2. Click Register new bike and enter a serial number like ABC123.
3. Connect with a wrong number first to see the "Bike not found" error, then connect with ABC123.
4. Press Start charging. The battery fills fast on purpose (about 1% per second) so demos are quick.
5. At 100%, charging stops and a "fully charged" message appears.
6. Try the lock and unlock buttons, then Disconnect.

Files
File	    What it does
app.py	The website's logic: pages, login, bike registry
hardware.py	Pretend hardware (swap for real Pi code later)
templates/	The pages (HTML)
static/style.css	Colors and layout
requirements.txt	Python packages to install
stationapp.db	Created automatically on first run (accounts and bikes). Not uploaded to GitHub.
Opening the site on another device

The 127.0.0.1 address only works on the computer running the site. To open it from a phone or another laptop:

Put both devices on the same WiFi. Campus WiFi often blocks this, so a phone hotspot works better.
On the computer running the site, run ipconfig (Windows) or ifconfig (Mac) and find the IPv4 address.
On the other device, open http://THAT-ADDRESS:5000.

If it still won't load, allow Python through Windows Firewall on Private networks.

Do not share the site over the public internet with debug=True on (last line of app.py). Debug mode is only safe on your own machine or a trusted network.
