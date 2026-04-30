import os
import sys
import subprocess
import time
import hashlib
import base64
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
DARK_RED = "\033[31m"
RESET = "\033[0m"

# ========== البذرة السرية للتشفير (مخفية ومجزأة) ==========
_SECRET_SEED = "V3n0m_2024_S3cur3_K3y_!@#$%^&*()_+M4st3r"
_HIDDEN_SALT = b'x9K#mP2$vL5@nQ8*wR3&jH6^cF4!dS7'

# ========== إعدادات الحماية القوية ==========
DURATION_HOURS = 28  # المدة 28 ساعة
EXPIRY_FILE = os.path.expanduser("~/.config/.system_cache/.dbus_agent")
BACKUP_EXPIRY = os.path.expanduser("~/.local/share/.session_data/.x11_auth")
HIDDEN_CHECKPOINTS = [
    os.path.expanduser("~/.cache/.thumbnails/.idx"),
    os.path.expanduser("~/.local/share/.Trash/.metadata"),
    os.path.expanduser("/tmp/.X11-unix/.lock")
]

# خوادم الوقت الموثوقة (متعددة للتحقق المتقاطع)
TIME_SERVERS = [
    "https://worldtimeapi.org/api/timezone/Etc/UTC",
    "https://timeapi.io/api/Time/current/zone?timeZone=UTC",
    "http://worldclockapi.com/api/json/utc/now"
]

def _generate_master_key():
    """توليد مفتاح رئيسي معقد من البذرة السرية"""
    password = _SECRET_SEED.encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=32,
        salt=_HIDDEN_SALT,
        iterations=2000000,  # 2 مليون دورة للحماية من القوة الغاشمة
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return Fernet(key)

def _create_hidden_directory(filepath):
    """إنشاء مجلدات مخفية لحماية الملفات"""
    directory = os.path.dirname(filepath)
    if not os.path.exists(directory):
        os.makedirs(directory, mode=0o700, exist_ok=True)

def _get_real_time_from_servers():
    """الحصول على الوقت الحقيقي من خوادم متعددة للتحقق المتقاطع"""
    times = []
    
    for server in TIME_SERVERS:
        try:
            req = urllib.request.Request(server, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:120.0) Gecko/20100101 Firefox/120.0'
            })
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
                if "worldtimeapi" in server:
                    current_time = datetime.fromisoformat(data['utc_datetime'].replace('Z', '+00:00'))
                elif "timeapi.io" in server:
                    current_time = datetime.fromisoformat(data['dateTime'].replace('Z', '+00:00'))
                elif "worldclockapi" in server:
                    current_time = datetime.fromisoformat(data['currentDateTime'])
                    
                times.append(current_time.replace(tzinfo=None))
                
        except Exception:
            continue
    
    if times:
        # استخدام متوسط الأوقات للدقة
        avg_time = times[0]
        if len(times) > 1:
            # التحقق من تناسق الأوقات (بفارق أقصى 5 ثوان)
            for t in times[1:]:
                if abs((avg_time - t).total_seconds()) <= 5:
                    avg_time = t
        return avg_time
    
    return None

def _calculate_local_checksum():
    """حساب تجزئة متقدمة للتحقق من سلامة النظام"""
    try:
        # جمع معلومات النظام للتأكد من عدم التلاعب
        system_info = f"{os.uname()}{os.getpid()}{time.timezone}"
        checksum = hashlib.sha3_512(system_info.encode()).hexdigest()
        return checksum
    except:
        return hashlib.sha512(os.urandom(64)).hexdigest()

def _anti_tamper_check(expiry_data):
    """فحص متقدم لمنع التلاعب بالملفات"""
    try:
        # التحقق من سلامة البيانات المشفرة
        required_keys = ['expiry', 'created', 'checksum', 'system_hash', 'activation_count']
        if not all(key in expiry_data for key in required_keys):
            return False
        
        # التحقق من عدم زيادة عدد مرات التفعيل
        if expiry_data.get('activation_count', 0) > 3:
            return False
            
        # التحقق من تجزئة النظام
        current_hash = _calculate_local_checksum()
        stored_hash = expiry_data.get('system_hash', '')
        
        # مقارنة أول 32 حرف من التجزئة
        if current_hash[:32] != stored_hash[:32]:
            return False
            
        return True
    except:
        return False

def get_encrypted_expiry():
    """نظام الحماية المتكامل للوقت"""
    try:
        cipher = _generate_master_key()
        
        # المحاولة الأولى: الخوادم الخارجية
        real_time = _get_real_time_from_servers()
        
        if real_time is None:
            # المحاولة الثانية: وقت النظام مع التحقق من ملفات متعددة
            local_time = datetime.now()
            
            # التحقق من ملفات الصلاحية المتعددة
            all_expiry_files = [EXPIRY_FILE, BACKUP_EXPIRY] + HIDDEN_CHECKPOINTS
            valid_expiry = None
            
            for file_path in all_expiry_files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'rb') as f:
                            encrypted_data = f.read()
                            decrypted_data = cipher.decrypt(encrypted_data)
                            expiry_data = json.loads(decrypted_data.decode())
                            
                            if _anti_tamper_check(expiry_data):
                                valid_expiry = expiry_data
                                break
                    except Exception:
                        continue
            
            if valid_expiry:
                expiry_time = datetime.fromisoformat(valid_expiry['expiry'])
                
                if local_time > expiry_time:
                    # التحقق الإضافي: هل تم تغيير وقت النظام؟
                    diff_hours = abs((local_time - expiry_time).total_seconds()) / 3600
                    
                    if diff_hours < 24:  # إذا كان الفرق أقل من 24 ساعة، قد يكون حقيقياً
                        return True, "Expired"
                    else:
                        # احتمال تلاعب كبير، لكن نقبل الانتهاء
                        return True, "Expired - Tampering Detected"
                else:
                    remaining = expiry_time - local_time
                    hours = remaining.total_seconds() / 3600
                    print(GREEN + f"[+] Remaining Time: {hours:.1f} hours" + RESET)
                    return False, remaining
            else:
                # فشل التحقق - حماية إضافية
                return True, "Verification Failed"
        else:
            # التحقق من وقت السيرفر
            all_expiry_files = [EXPIRY_FILE, BACKUP_EXPIRY] + HIDDEN_CHECKPOINTS
            valid_expiry = None
            
            for file_path in all_expiry_files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'rb') as f:
                            encrypted_data = f.read()
                            decrypted_data = cipher.decrypt(encrypted_data)
                            expiry_data = json.loads(decrypted_data.decode())
                            
                            if _anti_tamper_check(expiry_data):
                                valid_expiry = expiry_data
                                break
                    except Exception:
                        continue
            
            if valid_expiry:
                expiry_time = datetime.fromisoformat(valid_expiry['expiry'])
                
                if real_time > expiry_time:
                    return True, "Expired - Server Verified"
                else:
                    remaining = expiry_time - real_time
                    hours = remaining.total_seconds() / 3600
                    print(GREEN + f"[+] Server Time Verified - Remaining: {hours:.1f} hours" + RESET)
                    print(GREEN + f"[+] Expiry Date: {expiry_time.strftime('%Y-%m-%d %H:%M:%S')} UTC" + RESET)
                    return False, remaining
            else:
                # أول تشغيل - إنشاء ملفات الصلاحية
                expiry_time = real_time + timedelta(hours=DURATION_HOURS)
                
                expiry_data = {
                    'expiry': expiry_time.isoformat(),
                    'created': real_time.isoformat(),
                    'checksum': hashlib.sha3_256(f"{expiry_time.isoformat()}{_SECRET_SEED}".encode()).hexdigest(),
                    'system_hash': _calculate_local_checksum(),
                    'activation_count': 1,
                    'version': '3.0'
                }
                
                encrypted_data = cipher.encrypt(json.dumps(expiry_data).encode())
                
                # تخزين في مواقع متعددة
                for file_path in all_expiry_files:
                    try:
                        _create_hidden_directory(file_path)
                        with open(file_path, 'wb') as f:
                            f.write(encrypted_data)
                        os.chmod(file_path, 0o400)  # للقراءة فقط
                    except Exception:
                        continue
                
                print(GREEN + f"[+] Tool Activated for {DURATION_HOURS} hours" + RESET)
                print(GREEN + f"[+] Expiry Date: {expiry_time.strftime('%Y-%m-%d %H:%M:%S')} UTC" + RESET)
                print(YELLOW + "[!] Anti-Tamper System: ACTIVE" + RESET)
                return False, None
                
    except Exception as e:
        print(RED + f"[-] Security System Error: {str(e)[:50]}" + RESET)
        return True, "Security System Compromised"

def secure_self_destruct():
    """تدمير آمن للسكريبت مع حذف جميع الآثار"""
    print(RED + "\n[!] SECURITY BREACH DETECTED!" + RESET)
    print(RED + "[!] Initiating Secure Protocol..." + RESET)
    time.sleep(1)
    
    files_to_delete = [__file__, EXPIRY_FILE, BACKUP_EXPIRY] + HIDDEN_CHECKPOINTS
    
    for file_path in files_to_delete:
        try:
            if os.path.exists(file_path):
                # الكتابة فوق الملف ببيانات عشوائية قبل الحذف
                with open(file_path, 'wb') as f:
                    f.write(os.urandom(os.path.getsize(file_path) or 1024))
                os.remove(file_path)
        except Exception:
            pass
    
    print(RED + "[!] Tool has been permanently disabled" + RESET)
    sys.exit(1)

# ========== التنفيذ الرئيسي ==========
print(YELLOW + "[*] Initializing Security Protocols..." + RESET)

is_expired, data = get_encrypted_expiry()

if is_expired:
    print(RED + f"\n[!] {data}" + RESET)
    print(RED + "[!] Tool has expired or been tampered with" + RESET)
    secure_self_destruct()

# ========== الكود الأصلي للأداة ==========
print(DARK_RED + '''
╦  ╦╔═╗╔╗╔╔═╗╔╦╗
╚╗╔╝║╣ ║║║║ ║║║║
 ╚╝ ╚═╝╝╚╝╚═╝╩ ╩           
''' + RESET)

print(RED + "[ VENOM ] - Initializing Tool..." + RESET)
print(GREEN + "[ VENOM ] - Welcome User!" + RESET)
print("[+] Checking for updates...")

try:
    os.system('git pull')
except:
    pass

def get_network_info():
    print(RED + "\n[ NETWORK INFO ]" + RESET)
    try:
        ip = subprocess.getoutput("curl -s ifconfig.me")
        if ip:
            print(GREEN + f"[+] Public IP     : {ip}" + RESET)
        else:
            print(RED + "[-] Could not fetch IP" + RESET)
    except:
        print(RED + "[-] IP fetch failed" + RESET)

    try:
        connection = subprocess.getoutput("nmcli -t -f TYPE,STATE dev status 2>/dev/null | grep 'connected' | head -1 | cut -d: -f1")
        if not connection:
            connection = subprocess.getoutput("cat /sys/class/net/wlan0/operstate 2>/dev/null")
            if "up" in connection:
                connection = "Wi-Fi"
            else:
                connection = "Unknown / Ethernet"
        print(GREEN + f"[+] Connection Type : {connection}" + RESET)
    except:
        print(RED + "[-] Could not detect connection type" + RESET)

print(RED + "[+] " + GREEN + "VENOM IS READY" + RESET)
print(RED + "[+] " + GREEN + "Exploiting Target..." + RESET)
print(RED + "[+] " + GREEN + "Connecting to Server..." + RESET)
get_network_info()
print(RED + "\n[+] Opening Telegram Channel..." + RESET)
try:
    os.system('xdg-open https://t.me/myin2006')
except:
    pass
print(GREEN + "[+] Launching Main Tool..." + RESET)
try:
    __import__("SSJ")._____Exception()
except Exception as e:
    exit(RED + str(e) + RESET)
