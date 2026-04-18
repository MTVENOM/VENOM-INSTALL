#!/data/data/com.termux/files/usr/bin/bash

clear
echo "🔥 INSTALLING VENOM SYSTEM 🔥"

pkg update -y && pkg upgrade -y
pkg install python git curl tor tmux netcat-openbsd net-tools -y

rm -rf $HOME/VENOM

git clone https://github.com/MTVENOM/VENOM-INSTALL.git $HOME/VENOM

chmod +x $HOME/VENOM/*.so 2>/dev/null

# ----------------------
# إنشاء venom-tor
# ----------------------
cat > $PREFIX/bin/venom-tor << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

killall tor 2>/dev/null
tor > /dev/null 2>&1 &
sleep 15

while true
do
    IP=$(curl --socks5-hostname 127.0.0.1:9050 -s https://api.ipify.org)

    if [ -z "$IP" ]; then
        echo "❌ WAITING FOR TOR..."
        sleep 5
        continue
    fi

    DATA=$(curl --socks5-hostname 127.0.0.1:9050 -s ipinfo.io/$IP/json)

    COUNTRY=$(echo $DATA | grep -o '"country": *"[^"]*' | cut -d'"' -f4)
    CITY=$(echo $DATA | grep -o '"city": *"[^"]*' | cut -d'"' -f4)

    clear
    echo "🔥 TOR PANEL"
    echo "IP: $IP"
    echo "COUNTRY: $COUNTRY"
    echo "CITY: $CITY"

    echo -e 'AUTHENTICATE\r\nSIGNAL NEWNYM\r\nQUIT' | nc 127.0.0.1 9051 2>/dev/null

    sleep 60
done
EOF

chmod +x $PREFIX/bin/venom-tor

# ----------------------
# إنشاء venom
# ----------------------
cat > $PREFIX/bin/venom << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash

tmux start-server

tmux kill-session -t venom-tool 2>/dev/null
tmux kill-session -t venom-tor 2>/dev/null

tmux new-session -d -s venom-tool "cd $HOME/VENOM && python M4.py"
tmux new-session -d -s venom-tor "venom-tor"

echo "🔥 VENOM STARTED"
echo "CTRL+B ثم S للتبديل"

sleep 2

tmux attach -t venom-tool
EOF

chmod +x $PREFIX/bin/venom

echo "ControlPort 9051" >> $PREFIX/etc/tor/torrc
echo "CookieAuthentication 0" >> $PREFIX/etc/tor/torrc

clear
echo "✅ DONE"
echo "RUN: venom"
