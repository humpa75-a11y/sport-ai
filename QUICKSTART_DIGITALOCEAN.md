# 🎯 DE MEESTER - DIGITALOCEAN QUICK START

## ⚡ SUPER SNELLE START (10 minuten!)

### 1️⃣ Maak DigitalOcean Account
- Ga naar: https://m.do.co/c/4d7f4ff9e923
- Krijg $200 GRATIS credits! (33 maanden gratis hosting!)
- Maak account + voeg betaalmethode toe

### 2️⃣ Maak Droplet
- Create → Droplets
- **Ubuntu 22.04 LTS**
- **$6/month** (1 GB RAM)
- **Amsterdam** datacenter
- Noteer je **IP adres**

### 3️⃣ Verbind met Server
```powershell
ssh root@YOUR_IP_ADDRESS
```

### 4️⃣ Run Auto-Install Script
```bash
wget https://raw.githubusercontent.com/humpa75-a11y/sport-ai/main/deploy_server.sh
bash deploy_server.sh
```

### 5️⃣ Upload Code
Op je LAPTOP:
```powershell
.\upload_to_server.bat YOUR_IP_ADDRESS
```

### 6️⃣ Installeer Python Packages
Op de SERVER:
```bash
su - demeester
cd sport-ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 7️⃣ Start De Meester
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start demeester
```

### 8️⃣ Bezoek je Website!
```
http://YOUR_IP_ADDRESS
```

🎉 **KLAAR! De Meester draait 24/7!**

---

## 📚 VOLLEDIGE DOCUMENTATIE

- **Complete Guide:** `DEPLOY_DIGITALOCEAN.md`
- **Server Commando's:** `SERVER_COMMANDS.md`
- **Server Status:** `SERVER_STATUS.md`

---

## 🆘 HULP NODIG?

### Veelvoorkomende Problemen:

**❌ "Connection refused"**
```bash
sudo supervisorctl status
sudo systemctl status nginx
```

**❌ "Permission denied"**
```bash
sudo chown -R demeester:demeester /home/demeester/sport-ai
```

**❌ App crashed**
```bash
sudo tail -f /var/log/demeester/err.log
```

---

## 🔧 HANDIGE COMMANDO'S

### Check Status:
```bash
sudo supervisorctl status
```

### Herstart:
```bash
sudo supervisorctl restart demeester
```

### Bekijk Logs:
```bash
sudo tail -f /var/log/demeester/out.log
```

### Update Code:
```bash
cd /home/demeester/sport-ai
git pull
sudo supervisorctl restart demeester
```

---

## 💰 KOSTEN

| Periode | Kosten |
|---------|--------|
| **Eerste 33 maanden** | **€0** (gratis credits!) |
| **Daarna per maand** | **€6** |

---

## ✅ CHECKLIST

- [ ] DigitalOcean account aangemaakt
- [ ] $200 credits ontvangen
- [ ] Droplet aangemaakt (Ubuntu 22.04, €6/maand)
- [ ] IP adres genoteerd
- [ ] SSH verbinding getest
- [ ] Auto-install script uitgevoerd
- [ ] Code geüpload
- [ ] Python packages geïnstalleerd
- [ ] Supervisor geconfigureerd
- [ ] Nginx geconfigureerd
- [ ] Firewall geconfigureerd
- [ ] Website bereikbaar via browser
- [ ] Test voorspelling succesvol

---

## 🚀 VOLGENDE STAPPEN

1. **Train de AI:**
```bash
cd /home/demeester/sport-ai
source venv/bin/activate
python scripts/train_model.py
```

2. **Stel automatische training in:**
```bash
crontab -e
```
Voeg toe:
```
0 3 * * * cd /home/demeester/sport-ai && /home/demeester/sport-ai/venv/bin/python scripts/train_model.py
```

3. **Optioneel: Koop domein en installeer SSL:**
   - Zie `DEPLOY_DIGITALOCEAN.md` sectie "Custom Domein"

---

## 📞 SUPPORT

Heb je vragen of loop je vast? Laat het me weten!

**De Meester is klaar om de wereld te veroveren! 🏆⚽**
