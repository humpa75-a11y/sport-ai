# 🔥 API SETUP GUIDE - KILLER MACHINE CONFIGURATIE

## 🎯 DOEL: PERFECTE SCORES - MOORD MACHINE DIE ALTIJD RAAK SCHIET!

Om de **BESTE** data te krijgen en **ECHTE** wedstrijden van VANDAAG/MORGEN, hebben we meerdere bronnen:

---

## 📊 DATA BRONNEN (Gerangschikt op kwaliteit)

### 1. 🥇 API-FOOTBALL (BESTE!)

**Waarom het beste:**
- ✅ Meest nauwkeurige data
- ✅ Real-time updates
- ✅ Alle grote competities
- ✅ Team names exact gelijk aan onze database

**Gratis tier:**
- 100 requests per dag
- Perfect voor 10-20 "Genereer Gouden Wedstrijden" clicks per dag

**Setup:**
1. Ga naar: https://www.api-football.com/
2. Klik "Get Your Free API Key"
3. Registreer met email
4. Kopieer je API key (ziet eruit als: `abc123def456...`)
5. Activeer key:
   ```powershell
   # Windows PowerShell (permanent):
   [System.Environment]::SetEnvironmentVariable('API_FOOTBALL_KEY', 'JOUW_KEY_HIER', 'User')
   
   # Of tijdelijk (deze sessie):
   $env:API_FOOTBALL_KEY = "JOUW_KEY_HIER"
   ```

**Test:**
```powershell
echo $env:API_FOOTBALL_KEY
```

---

### 2. 🥈 THE ODDS API (Goed)

**Waarom goed:**
- ✅ Gratis 500 requests/maand
- ✅ Live odds + match data
- ✅ Goede coverage Europa

**Setup:**
1. Ga naar: https://the-odds-api.com/
2. "Get Free API Key"
3. Registreer
4. Activeer:
   ```powershell
   [System.Environment]::SetEnvironmentVariable('ODDS_API_KEY', 'JOUW_KEY_HIER', 'User')
   ```

---

### 3. 🥉 ODDS-PORTAL SCRAPER (Backup)

**Automatisch - geen setup nodig!**
- ✅ Je hebt al de Node.js scraper
- ✅ Werkt zonder API key
- ⚠️ Langzamer (scraping duurt 10-30 sec)
- ⚠️ Kan geblokkeerd worden bij veel gebruik

**Requirements:**
- Node.js geïnstalleerd
- Dependencies: `npm install` in odds-portal-scraper folder

---

### 4. 🔧 INTELLIGENT FALLBACK (Altijd beschikbaar)

**Automatisch actief als alles faalt!**
- ✅ Geen setup nodig
- ✅ Gebruikt typische wedstrijdschema's
- ⚠️ Niet 100% real-time (maar wel realistisch)

---

## 🚀 AANBEVOLEN CONFIGURATIE

### Voor KILLER RESULTATEN:

**Minimaal (werkt altijd):**
```
Geen API keys nodig - gebruikt Intelligent Fallback
```

**Goed (aanbevolen):**
```powershell
# Alleen The Odds API (gratis 500 requests/maand)
$env:ODDS_API_KEY = "jouw_key"
```

**BEST (maximum power):**
```powershell
# Beide APIs voor maximale coverage
$env:API_FOOTBALL_KEY = "jouw_key"
$env:ODDS_API_KEY = "jouw_key"
```

---

## 📊 HOEVEEL API CALLS?

### Scenario: Gebruik gedurende 1 maand

**Met API-Football (100/dag):**
- Elke "Genereer Gouden Wedstrijden" = ~8 API calls
- = **12 generaties per dag**
- = **360 generaties per maand**

**Met The Odds API (500/maand):**
- Elke generatie = ~8 calls
- = **62 generaties per maand**

**Met BEIDE APIs:**
- API-Football als primair
- The Odds API als backup
- = **~400 generaties per maand mogelijk!**

**Zonder API keys:**
- Unlimited! Gebruikt intelligent fallback
- Wedstrijden zijn realistisch maar niet real-time

---

## 🧪 TEST JE SETUP

### 1. Test API Keys:
```powershell
# Check of keys zijn ingesteld
echo $env:API_FOOTBALL_KEY
echo $env:ODDS_API_KEY

# Test de ultimate fetcher
python backend/ultimate_matches_fetcher.py
```

### 2. Test Gouden Wedstrijden:
1. Start server: `python backend/app.py`
2. Open: http://127.0.0.1:5000
3. Klik: "🏆 Genereer Gouden Wedstrijden"
4. Check console output voor bronnen gebruikt

---

## 🔍 TROUBLESHOOTING

### "Geen wedstrijden gevonden"
✅ **Oplossing:**
- Check of je API keys correct zijn
- Kijk in de terminal welke bronnen proberen
- Fallback moet altijd werken

### "API Key invalid"
✅ **Oplossing:**
- Verifieer key is correct gekopieerd
- Check op API website of key actief is
- Herstart terminal na instellen keys

### "Te weinig wedstrijden"
✅ **Oplossing:**
- Dit is normaal! Niet elke dag zijn er veel wedstrijden
- Maandag/Vrijdag hebben vaak minder matches
- Woensdag (Champions League) heeft vaak 5-10 matches

### "Scraper niet werkt"
✅ **Oplossing:**
```powershell
cd odds-portal-scraper
npm install
node index.js next-matches england/premier-league --odds-format decimal --local ./output
```

---

## 💡 PRO TIPS

### 1. Rate Limiting
- Klik niet 50x op "Genereer" in 1 minuut
- Resultaten blijven ~30 min actueel
- Cache wedstrijden in de browser

### 2. Beste tijden om te genereren
- **Dinsdagavond 20:00** = Champions League
- **Woensdagavond 20:00** = Champions League  
- **Zaterdag 14:00** = Weekend voetbal
- **Zondag 14:00** = Weekend voetbal

### 3. Als je serieus bent (betaald)
- **API-Football Pro**: $15/maand = 10,000 calls
- **The Odds API**: $10/maand = 10,000 calls
- Dan heb je UNLIMITED generaties!

---

## ✅ CHECKLIST VOOR KILLER MACHINE

- [ ] API-Football key ingesteld
- [ ] The Odds API key ingesteld (optioneel)
- [ ] Node.js geïnstalleerd voor scraper
- [ ] Test gedaan met `python backend/ultimate_matches_fetcher.py`
- [ ] Server draait en gouden wedstrijden werken
- [ ] Console toont welke bronnen gebruikt worden

---

**Met deze setup heb je een KILLER MACHINE die altijd de beste wedstrijden vindt!** 🔥⚽

**Start server:**
```powershell
python backend/app.py
```

**Test URL:**
```
http://127.0.0.1:5000
```

**Klik de gouden knop en SCHIET RAAK!** 🎯
