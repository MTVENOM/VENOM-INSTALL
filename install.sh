#!/data/data/com.termux/files/usr/bin/bash

pkg update -y
pkg install python git curl -y

rm -rf $HOME/VENOM
git clone https://github.com/MTVENOM/VENOM-INSTALL.git $HOME/VENOM

chmod +x $HOME/VENOM/*.so

echo '#!/data/data/com.termux/files/usr/bin/bash
cd $HOME/VENOM
python M4.py' > $PREFIX/bin/venom

chmod +x $PREFIX/bin/venom

echo "It was installed  ✅"
echo "Type the run command : venom"
