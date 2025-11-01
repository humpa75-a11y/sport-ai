#!/bin/bash
# 🚀 SPORT AI SYNC - AUTOMATED DEPLOYMENT SCRIPT
# Run this on your DigitalOcean Ubuntu server

set -e  # Exit on error

echo "=================================="
echo "🚀 SPORT AI SYNC DEPLOYMENT"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
PROJECT_DIR="$HOME/sport_ai_sync"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="/var/log/sportai"

echo -e "${YELLOW}Step 1/10: Updating system...${NC}"
sudo apt update
sudo apt upgrade -y

echo -e "${YELLOW}Step 2/10: Installing dependencies...${NC}"
sudo apt install -y python3.11 python3-pip python3.11-venv git nginx supervisor postgresql redis-server

echo -e "${YELLOW}Step 3/10: Cloning repository...${NC}"
if [ -d "$PROJECT_DIR" ]; then
    echo "Project directory exists, pulling latest changes..."
    cd "$PROJECT_DIR"
    git pull origin main
else
    echo "Cloning repository..."
    git clone https://github.com/humpa75-a11y/sport-ai.git "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

echo -e "${YELLOW}Step 4/10: Setting up Python virtual environment...${NC}"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo -e "${YELLOW}Step 5/10: Installing Python packages...${NC}"
pip install --upgrade pip
pip install flask flask-cors flask-socketio requests pandas numpy scipy scikit-learn xgboost beautifulsoup4 lxml python-dateutil gunicorn

echo -e "${YELLOW}Step 6/10: Creating .env file...${NC}"
if [ ! -f "$PROJECT_DIR/.env" ]; then
    cat > "$PROJECT_DIR/.env" << 'EOF'
# API Keys
API_FOOTBALL_KEY=eec52f29ffbc24effa9bc0e7963a8cd9
FOOTBALL_DATA_ORG_KEY=d5513a02070e4dbba002d3f5c9a78942

# Flask settings
FLASK_ENV=production
SECRET_KEY=change-this-to-random-secret-key

# Server settings
HOST=0.0.0.0
PORT=5000
EOF
    chmod 600 "$PROJECT_DIR/.env"
    echo -e "${GREEN}✅ .env file created${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

echo -e "${YELLOW}Step 7/10: Configuring Nginx...${NC}"
sudo bash -c "cat > /etc/nginx/sites-available/sportai << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:5000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \"upgrade\";
    }
}
EOF"

# Remove default site and enable sportai
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/sportai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
echo -e "${GREEN}✅ Nginx configured${NC}"

echo -e "${YELLOW}Step 8/10: Setting up Supervisor...${NC}"
sudo mkdir -p "$LOG_DIR"
sudo chown $USER:$USER "$LOG_DIR"

sudo bash -c "cat > /etc/supervisor/conf.d/sportai.conf << EOF
[program:sportai]
directory=$PROJECT_DIR
command=$VENV_DIR/bin/python backend/api_server.py
user=$USER
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=$LOG_DIR/sportai.err.log
stdout_logfile=$LOG_DIR/sportai.out.log
environment=PATH=\"$VENV_DIR/bin\"
EOF"

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start sportai
echo -e "${GREEN}✅ Supervisor configured and app started${NC}"

echo -e "${YELLOW}Step 9/10: Configuring firewall...${NC}"
sudo ufw --force enable
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
echo -e "${GREEN}✅ Firewall configured${NC}"

echo -e "${YELLOW}Step 10/10: Setting up cron jobs...${NC}"
(crontab -l 2>/dev/null || echo "") | grep -v "sport_ai_sync" | crontab -
(crontab -l 2>/dev/null; echo "0 3 * * * $VENV_DIR/bin/python $PROJECT_DIR/scripts/ultimate_ai_trainer.py >> $LOG_DIR/cron.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "0 */6 * * * $VENV_DIR/bin/python $PROJECT_DIR/backend/multi_source_aggregator.py >> $LOG_DIR/matches.log 2>&1") | crontab -
echo -e "${GREEN}✅ Cron jobs configured${NC}"

echo ""
echo "=================================="
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo "=================================="
echo ""
echo "🎯 Your app is now running at:"
echo "   http://$(curl -s ifconfig.me)"
echo ""
echo "📊 Check status:"
echo "   sudo supervisorctl status sportai"
echo ""
echo "📝 View logs:"
echo "   tail -f $LOG_DIR/sportai.out.log"
echo ""
echo "🔄 Restart app:"
echo "   sudo supervisorctl restart sportai"
echo ""
echo "=================================="
