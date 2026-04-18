import os
import sys
import subprocess
RED = "\033[91m"
GREEN = "\033[92m"
DARK_RED = "\033[31m"
RESET = "\033[0m"
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
    __import__("ST7")._____Exception()
except Exception as e:
    exit(RED + str(e) + RESET)
