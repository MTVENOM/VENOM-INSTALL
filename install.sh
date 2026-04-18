#!/data/data/com.termux/files/usr/bin/bash

clear
echo "🔥 INSTALLING VENOM SYSTEM 🔥"

# تحديث
pkg update -y
pkg upgrade -y

# تثبيت الحزم
pkg install python git curl tor tmux netcat-openbsd -y

# حذف القديم
rm -rf $HOME/VENOM

# تحميل أداتك (صححت الرابط)
git clone https://github.com/MTVENOM/VENOM-INSTALL.git $HOME/VENOM

# صلاحيات
chmod +x $HOME/VENOM/*.so 2>/dev/null

# إنشاء سكربت VENOM-TOR
cat > $PREFIX/bin/venom-tor << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

# تشغيل Tor
if ! pgrep -x "tor" > /dev/null
then
    tor > /dev/null 2>&1 &
    sleep 8
fi

OLD_IP=""

while true
do
    printf 'AUTHENTICATE\r\nSIGNAL NEWNYM\r\nQUIT\r\n' | nc 127.0.0.1 9051 > /dev/null
    sleep 5

    IP=$(curl --socks5 127.0.0.1:9050 -s https://api.ipify.org)
    INFO=$(curl --socks5 127.0.0.1:9050 -s ipinfo.io/$IP)

    clear
    echo "🔥 VENOM TOR PANEL 🔥"
    echo "----------------------"
    echo "🌐 IP: $IP"
    echo "$INFO"
    echo "----------------------"
    echo "⏱ CHANGING EVERY 30s"

    sleep 25
done
EOF

chmod +x $PREFIX/bin/venom-tor

# إنشاء أمر venom (يشغل الاثنين مع بعض)
cat > $PREFIX/bin/venom << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

tmux new-session -d -s venom

# أداتك
tmux send-keys -t venom "cd $HOME/VENOM && python M4.py" C-m

# شاشة TOR
tmux split-window -h
tmux send-keys "venom-tor" C-m

tmux select-layout even-horizontal
tmux attach
EOF

chmod +x $PREFIX/bin/venom

# إعداد Tor
TORRC="$PREFIX/etc/tor/torrc"

if ! grep -q "ControlPort" $TORRC; then
echo "ControlPort 9051" >> $TORRC
echo "CookieAuthentication 0" >> $TORRC
echo "MaxCircuitDirtiness 30" >> $TORRC
fi

clear
echo "✅ INSTALLED SUCCESSFULLY"
echo "🚀 RUN: venom"
