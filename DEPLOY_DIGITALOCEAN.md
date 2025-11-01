# 🚀 DE MEESTER - DigitalOcean Deployment Guide

**Geschatte tijd:** 30-45 minuten  
**Kosten:** €6/maand (maar je krijgt $200 GRATIS credits = 33 maanden gratis!)  
**Resultaat:** 24/7 online AI op je eigen domein!

---

## 📋 STAP 1: DigitalOcean Account Aanmaken (5 min)

### 1.1 Registreer voor $200 Credits
1. Ga naar: **https://m.do.co/c/4d7f4ff9e923** (affiliate link met $200 credits!)
   - Of: https://www.digitalocean.com/
2. Klik op **"Sign Up"**
3. Vul je email in en maak een wachtwoord
4. Verifieer je email

### 1.2 Betalingsmethode Toevoegen
1. Ga naar **Billing** → **Payment Methods**
2. Voeg creditcard of PayPal toe
   - ⚠️ Je wordt NIET direct belast!
   - De $200 credits worden eerst gebruikt
3. Verifieer je account

✅ **Je hebt nu $200 credits!** (Geldig voor 60 dagen)

---

## 📋 STAP 2: Droplet Aanmaken (10 min)

### 2.1 Maak een nieuwe Droplet
1. Klik op **"Create"** → **"Droplets"**
2. Kies de volgende instellingen:

**Regio:**
- ✅ Amsterdam (snelst voor Europa)
- Of: Frankfurt

**Image:**
- ✅ Ubuntu 22.04 LTS x64

**Droplet Size:**
- ✅ Basic Plan
- ✅ Regular CPU
- ✅ **$6/month** - 1 GB RAM, 25 GB SSD, 1000 GB transfer

**Authentication:**
- ✅ Password (makkelijker voor beginners)
- Maak een sterk wachtwoord (noteer dit goed!)

**Hostname:**
- `de-meester-ai` (of een andere naam)

3. Klik op **"Create Droplet"**

⏳ Wacht 1-2 minuten tot de droplet klaar is...

### 2.2 Noteer je Server IP
1. Je ziet nu je droplet in het dashboard
2. **Noteer het IP adres** (bijvoorbeeld: 164.90.123.45)
3. Dit is je server adres!

---

## 📋 STAP 3: Verbind met je Server (5 min)

### 3.1 Open PowerShell op je laptop
1. Druk op `Windows + X`
2. Kies **"Windows PowerShell"** of **"Terminal"**

### 3.2 SSH naar je server
```powershell
ssh root@YOUR_IP_ADDRESS
```
Vervang `YOUR_IP_ADDRESS` met je echte IP (bv. 164.90.123.45)

**Bij eerste keer:**
- Type `yes` en druk Enter
- Voer je wachtwoord in (je ziet de tekst niet, dat is normaal)

✅ **Je bent nu ingelogd op je server!**

---

## 📋 STAP 4: Server Voorbereiden (10 min)

### 4.1 Update het systeem
```bash
apt update && apt upgrade -y
```
⏳ Dit duurt 2-3 minuten...

### 4.2 Installeer Python en dependencies
```bash
apt install -y python3 python3-pip python3-venv git nginx supervisor
```

### 4.3 Maak een gebruiker aan (veiliger dan root)
```bash
adduser demeester
usermod -aG sudo demeester
su - demeester
```

✅ **Server is klaar voor De Meester!**

---

## 📋 STAP 5: Code Uploaden naar Server (10 min)

### 5.1 Clone je Git repository (of upload handmatig)

**Optie A: Via Git (aanbevolen)**
```bash
cd /home/demeester
git clone https://github.com/humpa75-a11y/sport-ai.git
cd sport-ai
```

**Optie B: Upload vanaf je laptop**
Op je LAPTOP in PowerShell:
```powershell
scp -r C:\Users\makem\Desktop\sport_ai_sync demeester@YOUR_IP:/home/demeester/sport-ai
```

### 5.2 Maak Virtual Environment
```bash
cd /home/demeester/sport-ai
python3 -m venv venv
source venv/bin/activate
```

### 5.3 Installeer dependencies
```bash
pip install flask flask-cors pandas numpy scikit-learn xgboost scipy apscheduler requests gunicorn
```
⏳ Dit duurt 5-10 minuten...

---

## 📋 STAP 6: Configureer de App (5 min)

### 6.1 Pas app.py aan voor productie
```bash
nano backend/app.py
```

**Zoek de laatste regel en verander:**
```python
# VAN:
app.run(debug=False, host='0.0.0.0', port=5000)

# NAAR:
if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
```

Druk `CTRL+X`, dan `Y`, dan `ENTER` om op te slaan.

### 6.2 Test of het werkt
```bash
cd /home/demeester/sport-ai
source venv/bin/activate
python backend/app.py
```

**Als je ziet:**
```
* Running on http://127.0.0.1:5000
```
✅ Het werkt! Druk `CTRL+C` om te stoppen.

---

## 📋 STAP 7: Maak het Permanent met Supervisor (10 min)

### 7.1 Maak Supervisor configuratie
```bash
sudo nano /etc/supervisor/conf.d/demeester.conf
```

**Plak deze configuratie:**
```ini
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
```

Druk `CTRL+X`, dan `Y`, dan `ENTER`.

### 7.2 Maak log directory
```bash
sudo mkdir -p /var/log/demeester
sudo chown -R demeester:demeester /var/log/demeester
```

### 7.3 Start Supervisor
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start demeester
```

**Check status:**
```bash
sudo supervisorctl status
```

Je moet zien: `demeester RUNNING`

✅ **De Meester draait nu permanent!**

---

## 📋 STAP 8: Configureer Nginx (Web Server) (5 min)

### 8.1 Maak Nginx configuratie
```bash
sudo nano /etc/nginx/sites-available/demeester
```

**Plak deze configuratie:**
```nginx
server {
    listen 80;
    server_name YOUR_IP_ADDRESS;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Vervang `YOUR_IP_ADDRESS` met je echte IP!**

Druk `CTRL+X`, dan `Y`, dan `ENTER`.

### 8.2 Activeer de configuratie
```bash
sudo ln -s /etc/nginx/sites-available/demeester /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

✅ **Nginx is geconfigureerd!**

---

## 📋 STAP 9: Firewall Configureren (2 min)

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

Type `y` en druk Enter.

✅ **Firewall is actief!**

---

## 🎉 STAP 10: TEST JE LIVE SERVER!

### Open je browser en ga naar:
```
http://YOUR_IP_ADDRESS
```
(Vervang met je echte IP)

**Je zou nu De Meester moeten zien! 🎉**

Test een voorspelling:
- Manchester City vs Arsenal
- Real Madrid vs Barcelona

---

## 🌐 OPTIONEEL: Custom Domein (bv. demeester.nl)

### Als je een eigen domein wilt:

1. Koop een domein bij Namecheap, GoDaddy, etc.
2. Voeg een **A Record** toe:
   - Host: `@` (of `www`)
   - Points to: `YOUR_IP_ADDRESS`
   - TTL: 3600

3. Update Nginx config:
```bash
sudo nano /etc/nginx/sites-available/demeester
```

Verander `server_name YOUR_IP_ADDRESS;` naar:
```nginx
server_name demeester.nl www.demeester.nl;
```

4. Installeer gratis SSL (HTTPS):
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d demeester.nl -d www.demeester.nl
```

✅ **Nu heb je een echte website met HTTPS!**

---

## 🔧 HANDIGE COMMANDO'S

### Check of server draait:
```bash
sudo supervisorctl status
```

### Herstart de app:
```bash
sudo supervisorctl restart demeester
```

### Bekijk logs:
```bash
sudo tail -f /var/log/demeester/out.log
```

### Stop de app:
```bash
sudo supervisorctl stop demeester
```

### Update de code:
```bash
cd /home/demeester/sport-ai
git pull
sudo supervisorctl restart demeester
```

---

## 💰 KOSTEN OVERZICHT

| Item | Kosten |
|------|--------|
| **Eerste 33 maanden** | **GRATIS** ($200 credits) |
| **Daarna per maand** | €6 |
| **Domein (optioneel)** | €10/jaar |
| **SSL Certificaat** | GRATIS (Let's Encrypt) |

---

## 🆘 PROBLEMEN OPLOSSEN

### Server reageert niet:
```bash
sudo supervisorctl status
sudo systemctl status nginx
```

### App crashed:
```bash
sudo tail -f /var/log/demeester/err.log
```

### Kan niet verbinden via SSH:
- Check of IP adres klopt
- Check of wachtwoord correct is
- Probeer droplet opnieuw op te starten in DigitalOcean dashboard

---

## 🎯 VOLGENDE STAPPEN

1. ✅ Train de AI op de server:
```bash
cd /home/demeester/sport-ai
source venv/bin/activate
python scripts/train_model.py
```

2. ✅ Stel automatische daily retraining in (cron job):
```bash
crontab -e
```
Voeg toe:
```
0 3 * * * cd /home/demeester/sport-ai && /home/demeester/sport-ai/venv/bin/python scripts/train_model.py
```

3. ✅ Monitor je server met DigitalOcean Monitoring (gratis)

---

## 📞 HULP NODIG?

Als je ergens vastloopt, laat het me weten! Ik kan je door elk onderdeel helpen.

**De Meester draait nu 24/7 op jouw eigen server! 🚀⚽**

---

*Laatst bijgewerkt: 15 oktober 2025*
