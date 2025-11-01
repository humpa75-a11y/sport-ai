# 🏆 The Odds API Setup - Voor LIVE Wedstrijden

## Wat is dit?

De **Gouden Wedstrijden** functie haalt nu **ECHTE wedstrijden** op van vandaag/morgen via **The Odds API** en analyseert ze met de AI om de 2 beste kansen te vinden!

## 🆓 Gratis API Key Krijgen

### Optie 1: The Odds API (AANBEVOLEN - 500 gratis requests/maand)

1. **Ga naar:** https://the-odds-api.com/
2. **Klik op:** "Get Started" of "Free API Key"
3. **Vul je email in** en maak een account
4. **Kopieer je API key** (bijvoorbeeld: `abc123def456...`)

### Optie 2: Gebruik DEMO mode (beperkt)

Zonder API key gebruikt het systeem een **fallback** met realistische wedstrijden.

---

## ⚙️ API Key Instellen

### Windows (PowerShell):

```powershell
# Tijdelijk (voor deze sessie):
$env:ODDS_API_KEY = "JOU_API_KEY_HIER"

# Permanent (blijft na herstarten):
[System.Environment]::SetEnvironmentVariable('ODDS_API_KEY', 'JOU_API_KEY_HIER', 'User')
```

### Test of het werkt:

```powershell
echo $env:ODDS_API_KEY
```

---

## 🚀 Nu Gebruiken

1. **Start de server:**
   ```powershell
   python backend\app.py
   ```

2. **Open browser:** http://127.0.0.1:5000

3. **Klik op:** "🏆 Genereer Gouden Wedstrijden"

4. **Zie ECHTE wedstrijden** van vandaag/morgen met:
   - ⏰ Kickoff tijd (Vandaag/Morgen)
   - 🏆 Competitie naam
   - 📊 AI voorspelling + confidence
   - ⚽ Top 3 exacte scores

---

## 📊 Welke Competities?

De API haalt wedstrijden op van:

- ⚽ **Premier League** (Engeland)
- ⚽ **La Liga** (Spanje)  
- ⚽ **Bundesliga** (Duitsland)
- ⚽ **Serie A** (Italië)
- ⚽ **Ligue 1** (Frankrijk)
- ⚽ **Eredivisie** (Nederland)
- 🏆 **Champions League**
- 🏆 **Europa League**

---

## 🔢 API Limits

### Gratis Tier:
- **500 requests per maand**
- Elke klik op "Genereer Gouden Wedstrijden" = **~8 requests** (1 per competitie)
- **= ~60 generaties per maand gratis!**

### Tips om requests te besparen:
- Klik niet te vaak op "Genereer" (resultaten blijven actueel voor ~1 uur)
- Test eerst met DEMO mode (zonder API key)

---

## 🛠️ Troubleshooting

### "⚠️ API Key invalid - using FALLBACK data"
- Je API key is verkeerd of verlopen
- Verifieer: `echo $env:ODDS_API_KEY`
- Fallback mode werkt nog steeds (met realistische dummy data)

### "Geen wedstrijden gevonden"
- Het is mogelijk dat er vandaag/morgen geen wedstrijden zijn in de 8 competities
- Systeem gebruikt automatisch fallback met typische wedstrijden

### API requests tellen:
- Check je usage op: https://the-odds-api.com/account

---

## 🎯 Voorbeeld Output

```
🏆 GOUDEN MATCH 1
Atletico Madrid vs Real Sociedad (La Liga)
🔴 VANDAAG 20:00
Voorspelling: 3-1
Confidence: 69.8%
Top 3 Scores: 3-0 (8.2%), 2-0 (7.9%), 4-0 (6.3%)

🏆 GOUDEN MATCH 2  
Ajax vs PSV (Eredivisie)
📅 MORGEN 14:30
Voorspelling: 2-1
Confidence: 88.8%
Top 3 Scores: 1-1 (9.9%), 1-0 (9.8%), 2-1 (8.7%)
```

---

## 💡 Volgende Stappen

Als je meer requests nodig hebt:
- **Betaald plan:** $10/maand voor 10,000 requests
- Of gebruik **meerdere gratis accounts** met verschillende emails

---

**Je bent nu klaar om ECHTE wedstrijden te analyseren!** 🚀
