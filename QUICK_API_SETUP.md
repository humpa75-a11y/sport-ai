# 🔑 SNELLE API KEY SETUP - KRIJG ECHTE WEDSTRIJDEN!

## ⚡ QUICK START (5 minuten)

### Optie 1: API-Football (BESTE! - Gratis 100 calls/dag)

1. **Ga naar:** https://www.api-football.com/
2. **Klik:** "Get Your Free API Key" (groen knopje rechtsboven)
3. **Registreer:**
   - Email: jouw@email.com
   - Wachtwoord: maak aan
   - Klik "Register"
4. **Verifieer email** (check inbox)
5. **Login** en ga naar "Dashboard"
6. **Kopieer je API key** (lange tekst zoals: `abc123def456...`)

7. **Activeer in Windows:**
```powershell
# Open PowerShell als Administrator en run:
[System.Environment]::SetEnvironmentVariable('API_FOOTBALL_KEY', 'PLAK_JOUW_KEY_HIER', 'User')

# Herstart PowerShell (of sluit en open opnieuw)
```

8. **Test:**
```powershell
# Check of key is ingesteld:
echo $env:API_FOOTBALL_KEY

# Herstart de server:
python backend/app.py
```

---

### Optie 2: The Odds API (Ook goed - 500 calls/maand gratis)

1. **Ga naar:** https://the-odds-api.com/
2. **Klik:** "Get Free API Key"
3. **Registreer** met email
4. **Kopieer key**
5. **Activeer:**
```powershell
[System.Environment]::SetEnvironmentVariable('ODDS_API_KEY', 'JOUW_KEY_HIER', 'User')
```

---

## ✅ NA SETUP:

**Herstart server:**
```powershell
python backend/app.py
```

**Open browser:**
```
http://127.0.0.1:5000
```

**Klik "Genereer Gouden Wedstrijden"**

Je zult nu zien:
- ✅ "Bron: API-Football" (of "The-Odds-API")
- ✅ ECHTE wedstrijdtijden van vandaag/morgen
- ✅ Correcte kickoff tijden (14:00, 16:30, 20:00, etc.)

---

## 🔍 TROUBLESHOOTING

**"Nog steeds Intelligent-Fallback"**
- Herstart PowerShell NA het instellen van keys
- Check: `echo $env:API_FOOTBALL_KEY`
- Moet een lange string tonen, niet leeg zijn

**"API Key invalid"**
- Controleer key op API website
- Kopieer zonder extra spaties
- Plak exact tussen de quotes

**"Geen wedstrijden vandaag"**
- Dit is normaal op sommige dagen!
- Maandag/Vrijdag hebben vaak weinig wedstrijden
- Woensdag (Champions League) heeft veel matches

---

## 💡 WAAROM API-FOOTBALL?

- ✅ **Meest nauwkeurig** - exact dezelfde teamnamen als onze database
- ✅ **Real-time** - updates elke minuut
- ✅ **Betrouwbaar** - 99.9% uptime
- ✅ **Gratis** - 100 calls/dag = genoeg voor 10+ generaties
- ✅ **Alle competities** - Premier League, La Liga, Champions League, etc.

**Met API key = PERFECTE tijden!** 🎯
