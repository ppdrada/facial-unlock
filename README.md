# <img src="assets/icon/icon.svg" alt="Facial Unlock icon" height="32" align="top"> Facial Unlock

🇺🇸 **English** | 🇧🇷 [Português](README.pt-BR.md)

Unlocks your computer using a regular webcam at login.

![Status](https://img.shields.io/badge/status-in%20development-orange)
![Python](https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white)
![macOS](https://img.shields.io/badge/macOS-supported-black?logo=apple)
![Windows](https://img.shields.io/badge/Windows-supported-0078D6?logo=windows)

## 🚀 How to run

**macOS**

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python facial.py
```

**Windows**

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python facial.py
```

The home screen shows whether a face is already registered and lets you:

- **Register face** — records your face through the webcam
- **Add samples** — records more samples (e.g. with headphones, glasses, different lighting)
- **Test recognition** — recognizes your face and, for now, opens the calculator

To register, the app asks for your computer password (Touch ID/password on Mac, Windows Hello on Windows).

## 🔐 Security and privacy

- Your face data stays **only on your computer** and is never sent to the internet.
- Your **password still works** as an alternative — face recognition is a shortcut, not a replacement.
- 📸 Against photos: after recognizing your face, the app asks you to **stay still and then smile**. A photo can't change its expression.

## Project

Just testing to see if it works :P
