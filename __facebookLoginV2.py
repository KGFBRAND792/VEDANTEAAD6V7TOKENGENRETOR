import requests
import re
import string
import random
import json
import pyotp

"""
Written by Nguyen Minh Huy (RainTee)
Facebook Login V2 - Fixed with Multiple Mobile APIs
Dstetime: 28/12/2022
Last Update: 04/08/2023 
Enhanced with multiple mobile profiles for better success rate
"""

MOBILE_PROFILES = [
    {
        "name": "Android_India_Jio",
        "user_agent": "Dalvik/2.1.0 (Linux; U; Android 12; SM-A525F Build/SP1A.210812.016) [FBAN/FB4A;FBAV/406.0.0.26.90;FBPN/com.facebook.katana;FBLC/en_IN;FBBV/489830053;FBCR/Jio 4G;FBMF/samsung;FBBD/samsung;FBDV/SM-A525F;FBSV/12;FBCA/arm64-v8a;FBDM/{density=2.0,width=1080,height=2340};FB_FW/1;FBRV/0;]",
        "locale": "en_IN",
        "country": "IN",
        "host": "b-graph.facebook.com"
    },
    {
        "name": "Android_India_Airtel",
        "user_agent": "Dalvik/2.1.0 (Linux; U; Android 13; SM-M346B Build/TP1A.220624.014) [FBAN/FB4A;FBAV/438.0.0.33.118;FBPN/com.facebook.katana;FBLC/hi_IN;FBBV/523847291;FBCR/Airtel;FBMF/samsung;FBBD/samsung;FBDV/SM-M346B;FBSV/13;FBCA/arm64-v8a;FBDM/{density=2.0,width=1080,height=2400};FB_FW/1;FBRV/0;]",
        "locale": "hi_IN",
        "country": "IN",
        "host": "b-graph.facebook.com"
    },
    {
        "name": "Android_India_VI",
        "user_agent": "Dalvik/2.1.0 (Linux; U; Android 11; Redmi Note 10 Pro Build/RKQ1.200826.002) [FBAN/FB4A;FBAV/420.0.0.32.97;FBPN/com.facebook.katana;FBLC/en_IN;FBBV/502938471;FBCR/Vi;FBMF/Xiaomi;FBBD/xiaomi;FBDV/Redmi Note 10 Pro;FBSV/11;FBCA/arm64-v8a;FBDM/{density=2.75,width=1080,height=2400};FB_FW/1;FBRV/0;]",
        "locale": "en_IN",
        "country": "IN",
        "host": "b-graph.facebook.com"
    },
    {
        "name": "Android_India_BSNL",
        "user_agent": "Dalvik/2.1.0 (Linux; U; Android 10; POCO X3 Build/QKQ1.200614.002) [FBAN/FB4A;FBAV/395.0.0.32.114;FBPN/com.facebook.katana;FBLC/en_IN;FBBV/472839182;FBCR/BSNL MOBILE;FBMF/Xiaomi;FBBD/xiaomi;FBDV/POCO X3;FBSV/10;FBCA/arm64-v8a;FBDM/{density=2.75,width=1080,height=2400};FB_FW/1;FBRV/0;]",
        "locale": "en_IN",
        "country": "IN",
        "host": "b-graph.facebook.com"
    },
    {
        "name": "Android_India_OnePlus",
        "user_agent": "Dalvik/2.1.0 (Linux; U; Android 14; CPH2449 Build/UKQ1.230924.001) [FBAN/FB4A;FBAV/445.0.0.34.118;FBPN/com.facebook.katana;FBLC/en_IN;FBBV/538291847;FBCR/Jio 4G;FBMF/OnePlus;FBBD/OnePlus;FBDV/CPH2449;FBSV/14;FBCA/arm64-v8a;FBDM/{density=2.75,width=1080,height=2412};FB_FW/1;FBRV/0;]",
        "locale": "en_IN",
        "country": "IN",
        "host": "b-graph.facebook.com"
    },
    {
        "name": "Android_India_Realme",
        "user_agent": "Dalvik/2.1.0 (Linux; U; Android 12; RMX3393 Build/SP1A.210812.016) [FBAN/FB4A;FBAV/410.0.0.33.106;FBPN/com.facebook.katana;FBLC/en_IN;FBBV/498372615;FBCR/Airtel;FBMF/realme;FBBD/realme;FBDV/RMX3393;FBSV/12;FBCA/arm64-v8a;FBDM={density=2.0,width=1080,height=2400};FB_FW/1;FBRV/0;]",
        "locale": "en_IN",
        "country": "IN",
        "host": "b-graph.facebook.com"
    },
    {
        "name": "Android_India_Vivo",
        "user_agent": "Dalvik/2.1.0 (Linux; U; Android 13; V2227 Build/TP1A.220624.014) [FBAN/FB4A;FBAV/425.0.0.28.109;FBPN/com.facebook.katana;FBLC/hi_IN;FBBV/512938472;FBCR/Jio 4G;FBMF/vivo;FBBD/vivo;FBDV/V2227;FBSV/13;FBCA/arm64-v8a;FBDM={density=2.0,width=1080,height=2408};FB_FW/1;FBRV/0;]",
        "locale": "hi_IN",
        "country": "IN",
        "host": "b-graph.facebook.com"
    },
    {
        "name": "Android_India_Oppo",
        "user_agent": "Dalvik/2.1.0 (Linux; U; Android 12; CPH2185 Build/RKQ1.211119.001) [FBAN/FB4A;FBAV/415.0.0.35.108;FBPN/com.facebook.katana;FBLC/en_IN;FBBV/503847291;FBCR/Vi;FBMF/OPPO;FBBD/OPPO;FBDV/CPH2185;FBSV/12;FBCA/arm64-v8a;FBDM={density=2.0,width=720,height=1600};FB_FW/1;FBRV/0;]",
        "locale": "en_IN",
        "country": "IN",
        "host": "b-graph.facebook.com"
    },
    {
        "name": "iOS_India_iPhone13",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) [FBAN/FBIOS;FBAV/425.0.0.45.116;FBBV/518392847;FBDV/iPhone14,2;FBMD/iPhone;FBSN/iOS;FBSV/16.6;FBSS/3;FBID/phone;FBLC/en_IN;FBOP/5]",
        "locale": "en_IN",
        "country": "IN",
        "host": "b-graph.facebook.com"
    },
    {
        "name": "iOS_India_iPhone12",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) [FBAN/FBIOS;FBAV/438.0.0.48.103;FBBV/529384712;FBDV/iPhone13,2;FBMD/iPhone;FBSN/iOS;FBSV/17.1;FBSS/3;FBID/phone;FBLC/en_IN;FBOP/5]",
        "locale": "en_IN",
        "country": "IN",
        "host": "b-graph.facebook.com"
    },
    {
        "name": "FBLite_India",
        "user_agent": "Dalvik/2.1.0 (Linux; U; Android 11; M2101K7BI Build/RKQ1.200826.002) [FBAN/FBLite;FBAV/350.0.0.5.89;FBBV/442738291;FBDM={density=2.75,width=1080,height=2340};FBLC/en_IN;FBCR/Jio 4G;FBMF/Xiaomi;FBBD/Xiaomi;FBPN/com.facebook.lite;FBDV/M2101K7BI;FBSV/11;FBOP/1;FBCA/arm64-v8a:armeabi-v7a:armeabi;]",
        "locale": "en_IN",
        "country": "IN",
        "host": "b-graph.facebook.com"
    },
    {
        "name": "Messenger_India",
        "user_agent": "Dalvik/2.1.0 (Linux; U; Android 12; SM-A127F Build/SP1A.210812.016) [FBAN/Orca-Android;FBAV/388.0.0.26.107;FBPN/com.facebook.orca;FBLC/en_IN;FBBV/463829174;FBCR/Airtel;FBMF/samsung;FBBD/samsung;FBDV/SM-A127F;FBSV/12;FBCA/arm64-v8a;FBDM={density=1.5,width=720,height=1600};FB_FW/1;]",
        "locale": "en_IN",
        "country": "IN",
        "host": "b-graph.facebook.com"
    }
]

def jsonResults(dataJson, statusLogin, listExportCookies=None):
     if (statusLogin == 1):
          return {
               "success": {
                    "setCookies": "".join(listExportCookies),
                    "accessTokenFB": dataJson["access_token"],
                    "cookiesKey-ValueList": dataJson["session_cookies"]
               }
          }
     else:
          error_data = dataJson.get("error", {})
          return {
               "error": {
                    "title": error_data.get("error_user_title", "Login Failed"),
                    "description": error_data.get("error_user_msg", error_data.get("message", "Unknown error")),
                    "error_subcode": error_data.get("error_subcode", 0),
                    "error_code": error_data.get("code", 0),
                    "fbtrace_id": error_data.get("fbtrace_id", ""),
               }
          }
               
def randStr(length):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
         
def GetToken2FA(key2Fa):
     if key2Fa is None:
          return random.randint(100000, 999999)
     
     key2Fa = str(key2Fa).replace(" ", "").strip()
     
     if key2Fa.isdigit() and len(key2Fa) == 6:
          return key2Fa
     
     try:
          totp = pyotp.TOTP(key2Fa)
          return totp.now()
     except:
          return key2Fa

class loginFB:


     def __init__(self, username, password, AuthenticationGoogleCode=None):
          
          self.deviceID = self.adID = self.secureFamilyDeviceID = f"{randStr(8)}-{randStr(4)}-{randStr(4)}-{randStr(4)}-{randStr(12)}"
          self.manchineID = randStr(24)
          self.usernameFacebook = username
          self.passwordFacebook = password
          self.twoTokenAccess = AuthenticationGoogleCode
          
     def try_login_with_profile(self, profile):
          """Try login with a specific mobile profile"""
          headers = {}
          headers["Host"] = profile["host"]
          headers["Content-Type"] = "application/x-www-form-urlencoded"
          headers["X-Fb-Connection-Type"] = "unknown"
          headers["User-Agent"] = profile["user_agent"]
          headers["X-Fb-Connection-Quality"] = "EXCELLENT"
          headers["Authorization"] = "OAuth null"
          headers["X-Fb-Friendly-Name"] = "authenticate"
          headers["Accept-Encoding"] = "gzip, deflate"
          headers["X-Fb-Server-Cluster"] = "True"

          dataForm = {}
          dataForm["adid"] = self.adID
          dataForm["format"] = "json"
          dataForm["device_id"] = self.deviceID
          dataForm["email"] = self.usernameFacebook
          dataForm["password"] = self.passwordFacebook
          dataForm["generate_analytics_claim"] = "1"
          dataForm["community_id"] = ""
          dataForm["cpl"] = "true"
          dataForm["try_num"] = "1"
          dataForm["family_device_id"] = self.deviceID
          dataForm["secure_family_device_id"] = self.secureFamilyDeviceID
          dataForm["credentials_type"] = "password"
          dataForm["fb4a_shared_phone_cpl_experiment"] = "fb4a_shared_phone_nonce_cpl_at_risk_v3"
          dataForm["fb4a_shared_phone_cpl_group"] = "enable_v3_at_risk"
          dataForm["enroll_misauth"] = "false"
          dataForm["generate_session_cookies"] = "1"
          dataForm["error_detail_type"] = "button_with_disabled"
          dataForm["source"] = "login"
          dataForm["machine_id"] = self.manchineID
          dataForm["jazoest"] = "22421"
          dataForm["meta_inf_fbmeta"] = ""
          dataForm["advertiser_id"] = self.adID
          dataForm["encrypted_msisdn"] = ""
          dataForm["currently_logged_in_userid"] = "0"
          dataForm["locale"] = profile["locale"]
          dataForm["client_country_code"] = profile["country"]
          dataForm["fb_api_req_friendly_name"] = "authenticate"
          dataForm["fb_api_caller_class"] = "Fb4aAuthHandler"
          dataForm["api_key"] = "882a8490361da98702bf97a021ddc14d"
          dataForm["access_token"] = "350685531728|62f8ce9f74b12f84c123cc23437a4a32"

          try:
               response = requests.post(f"https://{profile['host']}/auth/login", data=dataForm, headers=headers, timeout=(5, 10))
               return json.loads(response.text), headers, dataForm
          except requests.exceptions.Timeout:
               return {"error": {"title": "Timeout", "description": "Facebook server is not responding. Try again later."}}, None, None
          except requests.exceptions.RequestException as e:
               return {"error": {"title": "Connection Error", "description": str(e)}}, None, None
          
     def handle_2fa(self, dataJson, headers, profile):
          """Handle 2FA authentication"""
          Get2FA = GetToken2FA(self.twoTokenAccess)
          dataForm2Fa = {}
          dataForm2Fa["adid"] = self.adID
          dataForm2Fa["format"] = "json"
          dataForm2Fa["device_id"] = self.deviceID
          dataForm2Fa["email"] = self.usernameFacebook
          dataForm2Fa["password"] = Get2FA
          dataForm2Fa["generate_analytics_claim"] = "1"
          dataForm2Fa["community_id"] = ""
          dataForm2Fa["cpl"] = "true"
          dataForm2Fa["try_num"] = "2"
          dataForm2Fa["family_device_id"] = self.deviceID
          dataForm2Fa["secure_family_device_id"] = self.secureFamilyDeviceID
          dataForm2Fa["sim_serials"] = "[]"
          dataForm2Fa["credentials_type"] = "two_factor"
          dataForm2Fa["fb4a_shared_phone_cpl_experiment"] = "fb4a_shared_phone_nonce_cpl_at_risk_v3"
          dataForm2Fa["fb4a_shared_phone_cpl_group"] = "enable_v3_at_risk"
          dataForm2Fa["enroll_misauth"] = "false"
          dataForm2Fa["generate_session_cookies"] = "1"
          dataForm2Fa["error_detail_type"] = "button_with_disabled"
          dataForm2Fa["source"] = "login"
          dataForm2Fa["machine_id"] = self.manchineID
          dataForm2Fa["jazoest"] = "22327"
          dataForm2Fa["meta_inf_fbmeta"] = ""
          dataForm2Fa["twofactor_code"] = Get2FA
          dataForm2Fa["userid"] = dataJson["error"]["error_data"]["uid"]
          dataForm2Fa["first_factor"] = dataJson["error"]["error_data"]["login_first_factor"]
          dataForm2Fa["advertiser_id"] = self.adID
          dataForm2Fa["encrypted_msisdn"] = ""
          dataForm2Fa["currently_logged_in_userid"] = "0"
          dataForm2Fa["locale"] = profile["locale"]
          dataForm2Fa["client_country_code"] = profile["country"]
          dataForm2Fa["fb_api_req_friendly_name"] = "authenticate"
          dataForm2Fa["fb_api_caller_class"] = "Fb4aAuthHandler"
          dataForm2Fa["api_key"] = "882a8490361da98702bf97a021ddc14d"
          dataForm2Fa["access_token"] = "350685531728|62f8ce9f74b12f84c123cc23437a4a32"
          
          try:
               response2Fa = requests.post(f"https://{profile['host']}/auth/login", data=dataForm2Fa, headers=headers, timeout=(5, 10))
               pass2Fa = json.loads(response2Fa.text)
          except requests.exceptions.Timeout:
               return {"error": {"title": "Timeout", "description": "Facebook 2FA server not responding. Try again."}}
          except requests.exceptions.RequestException as e:
               return {"error": {"title": "Connection Error", "description": str(e)}}
          
          if pass2Fa.get("error") is None:
               try:
                    listExportCookies = []
                    for cookie in pass2Fa.get("session_cookies", []):
                         try:
                              listExportCookies.append(f"{cookie['name']}={cookie['value']}; ")
                         except KeyError:
                              break
                    return jsonResults(pass2Fa, 1, listExportCookies)
               except Exception as errLog:
                    return {"error": {"description": str(errLog)}}
          else:
               return jsonResults(pass2Fa, 0)

     def main(self):
          last_error = None
          
          for profile in MOBILE_PROFILES:
               print(f"[DEBUG] Trying profile: {profile['name']}")
               
               self.deviceID = self.adID = self.secureFamilyDeviceID = f"{randStr(8)}-{randStr(4)}-{randStr(4)}-{randStr(4)}-{randStr(12)}"
               self.manchineID = randStr(24)
               
               dataJson, headers, dataForm = self.try_login_with_profile(profile)
               
               if headers is None:
                    last_error = dataJson
                    continue
               
               if dataJson.get("error") is not None:
                    error_subcode = dataJson["error"].get("error_subcode", 0)
                    
                    if error_subcode == 1348162:
                         return self.handle_2fa(dataJson, headers, profile)
                    
                    if error_subcode in [1348023, 405]:
                         last_error = jsonResults(dataJson, 0)
                         continue
                    
                    last_error = jsonResults(dataJson, 0)
                    continue
               else:
                    try:
                         listExportCookies = []
                         for cookie in dataJson.get("session_cookies", []):
                              try:
                                   listExportCookies.append(f"{cookie['name']}={cookie['value']}; ")
                              except KeyError:
                                   break
                         print(f"[DEBUG] Login successful with profile: {profile['name']}")
                         return jsonResults(dataJson, 1, listExportCookies)
                    except Exception as errLog:
                         return {"error": {"description": str(errLog)}}
          
          if last_error:
               return last_error
          return {"error": {"title": "Login Failed", "description": "All login attempts failed. Try again later."}}


"""
✓Remake by Nguyễn Minh Huy
✓Sửa đổi mới nhất vào thứ vào lúc 7:56 05/08/2023
✓Tôn trọng tác giả ❤️
"""
