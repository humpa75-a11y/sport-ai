# 🚀 DIGITALOCEAN DEPLOYMENT GUIDE - SPORT AI SYNC
**Datum:** 1 November 2025

---

## 📋 STAP 1: DIGITALOCEAN DROPLET MAKEN

### 1.1 Login naar DigitalOcean
Je bent al ingelogd op: https://cloud.digitalocean.com/

### 1.2 Create een nieuwe Droplet
1. Ga naar: **Create → Droplets**
2. Kies de volgende opties:

#### **A. Choose Region (Regio)**
```
✅ Amsterdam (AMS3) - Dichtsbij Nederland!
   Of: Frankfurt (FRA1) - Ook dichtbij
```

#### **B. Choose Image (Operating System)**
```
✅ Ubuntu 22.04 (LTS) x64
   (Meest stabiele keuze voor Python apps)
```

#### **C. Choose Size (Droplet grootte)**
```
Basis optie (voor testing):
💰 $6/maand - 1 GB RAM, 1 vCPU, 25 GB SSD
   ⚠️ Werkt, maar kan langzaam zijn

Aanbevolen optie:
💰 $12/maand - 2 GB RAM, 1 vCPU, 50 GB SSD
   ✅ Goed voor meeste AI workloads

Pro optie (als je meer bets analyseert):
💰 $24/maand - 4 GB RAM, 2 vCPU, 80 GB SSD
   ✅ Beste voor machine learning
```

#### **D. Choose Authentication**
```
✅ SSH Key (VEILIGER!)
   - Klik "New SSH Key"
   - Volg stappen hieronder om key te maken

Of:
⚠️ Password (Makkelijker maar minder veilig)
   - Kies een sterk wachtwoord (min. 12 karakters)
```

#### **E. Finalize Details**
```
Hostname: sport-ai-server
Tags: production, betting, ai
Backups: ✅ Enable (extra $1.20-2.40/maand)
Monitoring: ✅ Enable (gratis!)
```

---

## 🔑 STAP 2: SSH KEY MAKEN (WINDOWS)

### 2.1 Open PowerShell als Administrator
```powershell
# Check of je al een SSH key hebt
Test-Path ~\.ssh\id_rsa.pub
```

### 2.2 Als je GEEN key hebt, maak er één:
```powershell
# Genereer nieuwe SSH key
ssh-keygen -t rsa -b 4096 -C "jouw@email.com"

# Druk 3x Enter (accepteer defaults)
# - File location: C:\Users\makem\.ssh\id_rsa
# - Passphrase: (optioneel, druk Enter voor geen)
```

### 2.3 Kopieer de public key:
```powershell
# Laat public key zien
Get-Content ~\.ssh\id_rsa.pub | clip

# Dit kopieert automatisch naar clipboard!
```

### 2.4 Plak in DigitalOcean:
1. Ga terug naar DigitalOcean "Create Droplet"
2. Bij "Authentication" → "New SSH Key"
3. Plak de key (Ctrl+V)
4. Geef naam: "My Windows PC"
5. Klik "Add SSH Key"

---

## 🌐 STAP 3: VERBIND MET JE SERVER

### 3.1 Zodra Droplet klaar is (2-3 minuten):
Je krijgt een **IP adres**, bijvoorbeeld: `157.245.xxx.xxx`

### 3.2 Verbind via SSH:
```powershell
# Vervang IP_ADDRESS met jouw server IP
ssh root@IP_ADDRESS

# Eerste keer vraagt het om fingerprint te accepteren
# Type: yes
```

### 3.3 Je bent nu ingelogd op je server! 🎉

---

## ⚙️ STAP 4: SERVER CONFIGUREREN

### 4.1 Update systeem:
```bash
# Update package lijst
apt update

# Upgrade alle packages
apt upgrade -y

# Install essentials
apt install -y python3.11 python3-pip git nginx supervisor postgresql redis-server

# Check Python versie
python3 --version
```

### 4.2 Maak deployment user (veiliger dan root):
```bash
# Maak nieuwe user
adduser sportai

# Geef sudo rechten
usermod -aG sudo sportai

# Wissel naar nieuwe user
su - sportai
```

### 4.3 Setup SSH voor nieuwe user:
```bash
# Maak .ssh folder
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Kopieer SSH key van root
sudo cp /root/.ssh/authorized_keys ~/.ssh/
sudo chown sportai:sportai ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

---

## 📦 STAP 5: UPLOAD JE CODE

### 5.1 Op je Windows PC - Maak GitHub repo:
```powershell
cd C:\Users\makem\Desktop\sport_ai_sync

# Initialize git (als nog niet gedaan)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Sport AI Sync with 6 data sources"

# Push naar GitHub (je hebt al een repo: humpa75-a11y/sport-ai)
git remote add origin https://github.com/humpa75-a11y/sport-ai.git
git branch -M main
git push -u origin main
```

### 5.2 Op DigitalOcean server - Clone repo:
```bash
# Clone je repository
cd ~
git clone https://github.com/humpa75-a11y/sport-ai.git sport_ai_sync

# Ga naar project folder
cd sport_ai_sync
```

---

## 🐍 STAP 6: PYTHON ENVIRONMENT OPZETTEN

### 6.1 Maak virtual environment:
```bash
# Install venv als niet aanwezig
sudo apt install -y python3.11-venv

# Maak venv
python3 -m venv venv

# Activeer venv
source venv/bin/activate
```

### 6.2 Install dependencies:
```bash
# Upgrade pip
pip install --upgrade pip

# Install packages
pip install flask flask-cors flask-socketio requests pandas numpy scipy scikit-learn xgboost beautifulsoup4 lxml python-dateutil

# Als je een requirements.txt hebt:
pip install -r requirements.txt
```

---

## 🔐 STAP 7: ENVIRONMENT VARIABELEN (API KEYS)

### 7.1 Maak .env file:
```bash
cd ~/sport_ai_sync

# Maak .env file
nano .env
```

### 7.2 Voeg toe:
```env
# API Keys
API_FOOTBALL_KEY=eec52f29ffbc24effa9bc0e7963a8cd9
FOOTBALL_DATA_ORG_KEY=d5513a02070e4dbba002d3f5c9a78942

# Flask settings
FLASK_ENV=production
SECRET_KEY=jouw-super-geheime-key-hier-veranderen

# Server settings
HOST=0.0.0.0
PORT=5000
```

### 7.3 Opslaan:
```
Ctrl+O (opslaan)
Enter (bevestig)
Ctrl+X (sluiten)
```

### 7.4 Beveilig .env file:
```bash
chmod 600 .env
```

---

## 🚀 STAP 8: NGINX REVERSE PROXY (Voor HTTPS)

### 8.1 Configureer Nginx:
```bash
sudo nano /etc/nginx/sites-available/sportai
```

### 8.2 Plak deze configuratie:
```nginx
server {
    listen 80;
    server_name JOW_IP_ADRES_HIER;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:5000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 8.3 Activeer site:
```bash
# Maak symlink
sudo ln -s /etc/nginx/sites-available/sportai /etc/nginx/sites-enabled/

# Test configuratie
sudo nginx -t

# Herstart Nginx
sudo systemctl restart nginx
```

---

## 👁️ STAP 9: SUPERVISOR (KEEP APP RUNNING)

### 9.1 Maak Supervisor config:
```bash
sudo nano /etc/supervisor/conf.d/sportai.conf
```

### 9.2 Plak configuratie:
```ini
[program:sportai]
directory=/home/sportai/sport_ai_sync
command=/home/sportai/sport_ai_sync/venv/bin/python backend/api_server.py
user=sportai
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/sportai/sportai.err.log
stdout_logfile=/var/log/sportai/sportai.out.log
environment=PATH="/home/sportai/sport_ai_sync/venv/bin"
```

### 9.3 Maak log directory:
```bash
sudo mkdir -p /var/log/sportai
sudo chown sportai:sportai /var/log/sportai
```

### 9.4 Start Supervisor:
```bash
# Reload config
sudo supervisorctl reread
sudo supervisorctl update

# Start app
sudo supervisorctl start sportai

# Check status
sudo supervisorctl status sportai
```

---

## ⏰ STAP 10: DAGELIJKSE AI UPDATES (CRON)

### 10.1 Open crontab:
```bash
crontab -e

# Kies nano als editor (optie 1)
```

### 10.2 Voeg toe:
```cron
# Daily AI training at 3:00 AM
0 3 * * * /home/sportai/sport_ai_sync/venv/bin/python /home/sportai/sport_ai_sync/scripts/ultimate_ai_trainer.py >> /var/log/sportai/cron.log 2>&1

# Fetch new matches every 6 hours
0 */6 * * * /home/sportai/sport_ai_sync/venv/bin/python /home/sportai/sport_ai_sync/backend/multi_source_aggregator.py >> /var/log/sportai/matches.log 2>&1
```

### 10.3 Opslaan en sluiten (Ctrl+O, Enter, Ctrl+X)

---

## 🔥 STAP 11: FIREWALL CONFIGUREREN

### 11.1 Setup UFW (Uncomplicated Firewall):
```bash
# Enable UFW
sudo ufw enable

# Allow SSH (BELANGRIJK!)
sudo ufw allow OpenSSH

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS (voor later met SSL)
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

---

## 🎯 STAP 12: TESTEN!

### 12.1 Check of app draait:
```bash
# Check Supervisor status
sudo supervisorctl status sportai

# Check logs
tail -f /var/log/sportai/sportai.out.log
```

### 12.2 Test van je Windows PC:
```powershell
# Test API endpoint (vervang IP!)
Invoke-WebRequest -Uri "http://JOW_IP_HIER/api/predictions?league=bundesliga"
```

### 12.3 Open in browser:
```
http://JOW_IP_HIER
```

---

## 🔒 STAP 13: SSL/HTTPS TOEVOEGEN (OPTIONEEL MAAR AANBEVOLEN)

### 13.1 Install Certbot:
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 13.2 Verkrijg SSL certificaat:
```bash
# Als je een domeinnaam hebt (bijv. sportai.nl)
sudo certbot --nginx -d jouw-domein.nl

# Volg de prompts
# Certbot configureert automatisch Nginx voor HTTPS!
```

---

## 📊 STAP 14: MONITORING & MAINTENANCE

### 14.1 Check logs:
```bash
# App logs
tail -f /var/log/sportai/sportai.out.log

# Error logs
tail -f /var/log/sportai/sportai.err.log

# Cron logs
tail -f /var/log/sportai/cron.log

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 14.2 App management:
```bash
# Restart app
sudo supervisorctl restart sportai

# Stop app
sudo supervisorctl stop sportai

# Check status
sudo supervisorctl status sportai
```

### 14.3 Update code:
```bash
cd ~/sport_ai_sync

# Pull latest changes
git pull origin main

# Restart app
sudo supervisorctl restart sportai
```

---

## 💰 KOSTEN OVERZICHT

```
DigitalOcean Droplet (2GB RAM):    $12.00/maand
Backups (optioneel):               $ 2.40/maand
---------------------------------------------------
TOTAAL:                            $14.40/maand (~€13/maand)
```

**Eerste maand vaak met $200 credit!** 🎁

---

## 🆘 TROUBLESHOOTING

### App start niet:
```bash
# Check logs
sudo supervisorctl tail sportai stderr

# Check Python errors
cd ~/sport_ai_sync
source venv/bin/activate
python backend/api_server.py
```

### Kan niet verbinden:
```bash
# Check firewall
sudo ufw status

# Check Nginx
sudo systemctl status nginx
sudo nginx -t
```

### API keys werken niet:
```bash
# Check .env file
cat ~/sport_ai_sync/.env

# Restart app na wijzigingen
sudo supervisorctl restart sportai
```

---

## ✅ CHECKLIST

- [ ] DigitalOcean account aangemaakt
- [ ] Droplet gemaakt (Ubuntu 22.04, 2GB RAM)
- [ ] SSH verbinding werkt
- [ ] Code geüpload via Git
- [ ] Python environment opgezet
- [ ] Dependencies geïnstalleerd
- [ ] .env file met API keys
- [ ] Nginx geconfigureerd
- [ ] Supervisor draait app
- [ ] Cron jobs voor dagelijkse updates
- [ ] Firewall ingesteld
- [ ] App werkt in browser
- [ ] SSL certificaat (optioneel)

---

## 🚀 NA DEPLOYMENT

Je app is nu 24/7 online op: `http://JE_IP_ADRES`

**Dagelijkse automatische taken:**
- ✅ 03:00 - AI model training
- ✅ Elke 6 uur - Nieuwe matches ophalen
- ✅ Real-time updates via 6 data sources

**Kosten:** ~€13/maand voor een altijd-online AI betting systeem! 🎯

---

Wil je dat ik je stap-voor-stap door dit proces leid? Zeg maar waar je bent! 🚀
