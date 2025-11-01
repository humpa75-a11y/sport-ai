# 🔧 De Meester - Server Management Commando's

## Snelle Referentie voor je DigitalOcean Server

### 🔌 Verbinden met Server
```bash
ssh root@YOUR_IP_ADDRESS
# Of als gebruiker:
ssh demeester@YOUR_IP_ADDRESS
```

---

## 📊 STATUS CHECKEN

### Check of De Meester draait:
```bash
sudo supervisorctl status
```
Output: `demeester RUNNING` = ✅ Goed!

### Check Nginx status:
```bash
sudo systemctl status nginx
```

### Check alle services:
```bash
sudo supervisorctl status
sudo systemctl status nginx
sudo ufw status
```

---

## 🔄 APP BEHEREN

### Herstart De Meester:
```bash
sudo supervisorctl restart demeester
```

### Stop De Meester:
```bash
sudo supervisorctl stop demeester
```

### Start De Meester:
```bash
sudo supervisorctl start demeester
```

### Check logs (real-time):
```bash
sudo tail -f /var/log/demeester/out.log
```

### Check error logs:
```bash
sudo tail -f /var/log/demeester/err.log
```

---

## 📦 CODE UPDATEN

### Als je Git gebruikt:
```bash
cd /home/demeester/sport-ai
git pull
sudo supervisorctl restart demeester
```

### Als je handmatig uploadt:
Op je LAPTOP (PowerShell):
```powershell
scp -r C:\Users\makem\Desktop\sport_ai_sync\backend demeester@YOUR_IP:/home/demeester/sport-ai/
scp -r C:\Users\makem\Desktop\sport_ai_sync\frontend demeester@YOUR_IP:/home/demeester/sport-ai/
scp -r C:\Users\makem\Desktop\sport_ai_sync\scripts demeester@YOUR_IP:/home/demeester/sport-ai/
scp -r C:\Users\makem\Desktop\sport_ai_sync\data demeester@YOUR_IP:/home/demeester/sport-ai/
```

Dan op de SERVER:
```bash
sudo supervisorctl restart demeester
```

---

## 🧠 AI TRAINEN

### Eenmalige training:
```bash
cd /home/demeester/sport-ai
source venv/bin/activate
python scripts/train_model.py
```

### Automatische dagelijkse training instellen:
```bash
crontab -e
```
Voeg toe (dagelijks om 03:00):
```
0 3 * * * cd /home/demeester/sport-ai && /home/demeester/sport-ai/venv/bin/python scripts/train_model.py >> /var/log/demeester/training.log 2>&1
```

### Check training logs:
```bash
tail -f /var/log/demeester/training.log
```

---

## 🔥 FIREWALL

### Check firewall status:
```bash
sudo ufw status
```

### Open extra poorten (indien nodig):
```bash
sudo ufw allow 8000/tcp
```

### Herlaad firewall:
```bash
sudo ufw reload
```

---

## 🌐 NGINX

### Test Nginx configuratie:
```bash
sudo nginx -t
```

### Herlaad Nginx:
```bash
sudo systemctl reload nginx
```

### Herstart Nginx:
```bash
sudo systemctl restart nginx
```

### Bekijk Nginx logs:
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🔒 SSL CERTIFICAAT (HTTPS)

### Installeer Certbot:
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Vraag SSL certificaat aan:
```bash
sudo certbot --nginx -d jouwdomein.nl -d www.jouwdomein.nl
```

### Auto-renew SSL (gebeurt automatisch, maar check:
```bash
sudo certbot renew --dry-run
```

---

## 📈 SERVER MONITORING

### Check CPU & RAM gebruik:
```bash
htop
# Of:
top
```

### Check disk ruimte:
```bash
df -h
```

### Check memory gebruik:
```bash
free -h
```

### Check actieve processen:
```bash
ps aux | grep python
```

---

## 🆘 TROUBLESHOOTING

### Server reageert niet:
```bash
# Check alle services
sudo supervisorctl status
sudo systemctl status nginx

# Herstart alles
sudo supervisorctl restart demeester
sudo systemctl restart nginx
```

### App crashed:
```bash
# Bekijk error logs
sudo tail -n 100 /var/log/demeester/err.log

# Herstart app
sudo supervisorctl restart demeester
```

### Out of memory:
```bash
# Check memory
free -h

# Maak swap file (eenmalig):
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Kan niet verbinden:
```bash
# Check of SSH draait
sudo systemctl status ssh

# Check firewall
sudo ufw status

# Herstart SSH
sudo systemctl restart ssh
```

---

## 🔄 BACKUP & RESTORE

### Backup maken:
```bash
# Backup code + data
cd /home/demeester
tar -czf sport-ai-backup-$(date +%Y%m%d).tar.gz sport-ai/

# Download naar laptop (op LAPTOP in PowerShell):
scp demeester@YOUR_IP:/home/demeester/sport-ai-backup-*.tar.gz C:\Users\makem\Desktop\
```

### Restore from backup:
```bash
cd /home/demeester
tar -xzf sport-ai-backup-YYYYMMDD.tar.gz
sudo supervisorctl restart demeester
```

---

## 📊 SYSTEM INFO

### Server info:
```bash
# OS versie
lsb_release -a

# CPU info
lscpu

# Memory info
free -h

# Disk info
df -h

# Network info
ip addr show
```

---

## 🎯 SNELKOPPELINGEN

Maak aliases voor snelle toegang:
```bash
nano ~/.bashrc
```

Voeg toe:
```bash
# De Meester shortcuts
alias dm-status='sudo supervisorctl status'
alias dm-restart='sudo supervisorctl restart demeester'
alias dm-logs='sudo tail -f /var/log/demeester/out.log'
alias dm-errors='sudo tail -f /var/log/demeester/err.log'
alias dm-train='cd /home/demeester/sport-ai && source venv/bin/activate && python scripts/train_model.py'
```

Herlaad:
```bash
source ~/.bashrc
```

Nu kun je gewoon typen: `dm-status`, `dm-restart`, etc!

---

## 📞 BELANGRIJKE LOCATIES

| Item | Locatie |
|------|---------|
| **App Code** | `/home/demeester/sport-ai/` |
| **Virtual Env** | `/home/demeester/sport-ai/venv/` |
| **Logs** | `/var/log/demeester/` |
| **Nginx Config** | `/etc/nginx/sites-available/demeester` |
| **Supervisor Config** | `/etc/supervisor/conf.d/demeester.conf` |
| **Data/Models** | `/home/demeester/sport-ai/data/` |

---

**💡 TIP: Bookmark deze pagina voor snelle referentie!**
