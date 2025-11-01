#!/bin/bash
# 🚀 De Meester - Quick Deploy Script voor DigitalOcean
# Voer dit uit op je server om alles automatisch te installeren

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║           🏆 DE MEESTER - AUTO DEPLOYMENT SCRIPT 🏆                  ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check of we root zijn
if [ "$EUID" -ne 0 ]; then 
   echo "❌ Run dit script als root: sudo bash deploy.sh"
   exit 1
fi

echo "📦 STAP 1: Systeem updaten..."
apt update && apt upgrade -y

echo "🐍 STAP 2: Python en dependencies installeren..."
apt install -y python3 python3-pip python3-venv git nginx supervisor

echo "👤 STAP 3: Gebruiker aanmaken..."
if id "demeester" &>/dev/null; then
    echo "   ✅ Gebruiker 'demeester' bestaat al"
else
    adduser --disabled-password --gecos "" demeester
    usermod -aG sudo demeester
    echo "   ✅ Gebruiker 'demeester' aangemaakt"
fi

echo "📁 STAP 4: Project directory aanmaken..."
mkdir -p /home/demeester/sport-ai
chown -R demeester:demeester /home/demeester/sport-ai

echo "📝 STAP 5: Supervisor configureren..."
cat > /etc/supervisor/conf.d/demeester.conf << 'EOF'
[program:demeester]
directory=/home/demeester/sport-ai
command=/home/demeester/sport-ai/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 backend.app:app
user=demeester
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/demeester/err.log
stdout_logfile=/var/log/demeester/out.log
EOF

mkdir -p /var/log/demeester
chown -R demeester:demeester /var/log/demeester

echo "🌐 STAP 6: Nginx configureren..."
SERVER_IP=$(hostname -I | awk '{print $1}')
cat > /etc/nginx/sites-available/demeester << EOF
server {
    listen 80;
    server_name $SERVER_IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/demeester /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

echo "🔥 STAP 7: Firewall configureren..."
ufw --force enable
ufw allow 'Nginx Full'
ufw allow OpenSSH

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ SERVER SETUP COMPLEET! ✅                       ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 VOLGENDE STAPPEN:"
echo ""
echo "1. Switch naar demeester gebruiker:"
echo "   sudo su - demeester"
echo ""
echo "2. Upload je code naar: /home/demeester/sport-ai"
echo ""
echo "3. Installeer Python packages:"
echo "   cd /home/demeester/sport-ai"
echo "   python3 -m venv venv"
echo "   source venv/bin/activate"
echo "   pip install flask flask-cors pandas numpy scikit-learn xgboost scipy apscheduler requests gunicorn"
echo ""
echo "4. Start de service:"
echo "   sudo supervisorctl reread"
echo "   sudo supervisorctl update"
echo "   sudo supervisorctl start demeester"
echo ""
echo "🌐 Je server is bereikbaar op: http://$SERVER_IP"
echo ""
