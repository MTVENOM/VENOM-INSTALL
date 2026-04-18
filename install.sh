#!/data/data/com.termux/files/usr/bin/bash

clear
echo "🔥 INSTALLING VENOM SYSTEM 🔥"

# تحديث النظام
pkg install netcat-openbsd -y
pkg update -y && pkg upgrade -y

# تثبيت الحزم
pkg install python git curl tor tmux netcat-openbsd -y

# حذف النسخة القديمة
rm -rf $HOME/VENOM

# تحميل أداتك
git clone https://github.com/MTVENOM/VENOM-INSTALL.git $HOME/VENOM

# إعطاء صلاحيات
chmod +x $HOME/VENOM/*.so 2>/dev/null

# ---------------------------
# 🔥 إنشاء venom-tor
# ---------------------------
cat > $PREFIX/bin/venom-tor << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

if ! pgrep -x "tor" > /dev/null
then
    tor > /dev/null 2>&1 &
    sleep 10
fi

while true
do
    echo -e 'AUTHENTICATE\r\nSIGNAL NEWNYM\r\nQUIT' | nc 127.0.0.1 9051 > /dev/null
    sleep 5

    IP=$(curl --socks5 127.0.0.1:9050 -s https://api.ipify.org)
    DATA=$(curl --socks5 127.0.0.1:9050 -s ipinfo.io/$IP/json)

    COUNTRY=$(echo $DATA | grep -o '"country": *"[^"]*' | cut -d'"' -f4)
    CITY=$(echo $DATA | grep -o '"city": *"[^"]*' | cut -d'"' -f4)
    ORG=$(echo $DATA | grep -o '"org": *"[^"]*' | cut -d'"' -f4)

    SPEED=$(curl --socks5 127.0.0.1:9050 -o /dev/null -s -w '%{speed_download}' https://speed.hetzner.de/100MB.bin)

    clear
    echo "🔥 VENOM TOR PANEL 🔥"
    echo "------------------------"
    echo "🌐 IP        : $IP"
    echo "🌍 COUNTRY   : $COUNTRY"
    echo "🏙 CITY      : $CITY"
    echo "🏢 NETWORK   : $ORG"
    echo "⚡ SPEED     : $SPEED B/s"
    echo "------------------------"
    echo "🔄 CHANGING EVERY 60s"

    sleep 55
done
EOF

chmod +x $PREFIX/bin/venom-tor

# ---------------------------
# 🔥 إنشاء أمر venom
# ---------------------------
cat > $PREFIX/bin/venom << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

tmux kill-session -t venom-tool 2>/dev/null
tmux kill-session -t venom-tor 2>/dev/null

tmux new-session -d -s venom-tool "cd $HOME/VENOM && python M4.py"
tmux new-session -d -s venom-tor "venom-tor"

tmux attach -t venom-tool
EOF

chmod +x $PREFIX/bin/venom

# ---------------------------
# 🔥 إعداد Tor
# ---------------------------
echo "ControlPort 9051" >> $PREFIX/etc/tor/torrc
echo "CookieAuthentication 0" >> $PREFIX/etc/tor/torrc
echo "MaxCircuitDirtiness 60" >> $PREFIX/etc/tor/torrc

clear
echo "✅ INSTALLED SUCCESSFULLY"
echo "🚀 RUN: venom"
