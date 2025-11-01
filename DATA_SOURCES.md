# 📊 DATA BRONNEN - SPORT AI SYNC

## ✅ ACTIEVE DATA BRONNEN (Public APIs Only!)

**Update November 2025**: Alle bookmaker scraping is VERWIJDERD voor compliance en betrouwbaarheid.

### 🔥 Primaire Bronnen (Gebruikt door systeem)

1. **Sofascore API** (BESTE!)
   - URL: `https://api.sofascore.com`
   - Data: Live wedstrijden, xG stats, team vorm
   - Authenticatie: Geen (public API)
   - Rate limit: Redelijk
   - Status: ✅ ACTIEF

2. **Flashscore API**
   - URL: Via embedded scripts
   - Data: Live odds (1X2)
   - Authenticatie: Geen
   - Status: ✅ ACTIEF (via live_odds_scraper.py)

3. **API-Football** (Backup)
   - URL: `https://v3.football.api-sports.io`
   - Data: Fixtures, statistieken
   - Authenticatie: API Key (optioneel)
   - Status: ✅ ACTIEF (als backup)

4. **The Odds API** (Backup)
   - URL: `https://api.the-odds-api.com`
   - Data: Odds van meerdere bookmakers
   - Authenticatie: API Key (optioneel)
   - Status: ✅ ACTIEF (als backup)

5. **Odds-Portal Scraper** (Public Data)
   - Node.js scraper voor historische data
   - Data: Odds geschiedenis
   - Status: ✅ ACTIEF (Node.js module)

### ❌ VERWIJDERDE BRONNEN (Nov 2025)

De volgende bookmaker scrapers zijn **VERWIJDERD** voor compliance:

- ❌ TOTO.nl scraping
- ❌ Unibet.nl scraping
- ❌ Jacks.nl scraping
- ❌ Betcity scraping
- ❌ Bet365 scraping
- ❌ Holland Casino scraping

**Reden**: 
- Compliance met bookmaker Terms of Service
- Betrouwbaardere data van public APIs
- Lagere onderhoudskosten
- Geen legal risks

## 🎯 HUIDIGE DATA FLOW

```
┌─────────────────┐
│  Sofascore API  │ ─────┐
└─────────────────┘      │
                         │
┌─────────────────┐      │    ┌──────────────────┐
│ Flashscore API │ ─────┼───►│  Live Features   │
└─────────────────┘      │    │    Generator     │
                         │    └──────────────────┘
┌─────────────────┐      │             │
│ API-Football    │ ─────┤             ▼
└─────────────────┘      │    ┌──────────────────┐
                         │    │   PROFESSOR      │
┌─────────────────┐      │    │   DE MEESTER     │
│  The Odds API   │ ─────┘    └──────────────────┘
└─────────────────┘                    │
                                       ▼
                              ┌──────────────────┐
                              │ Poisson Value    │
                              │     Engine       │
                              └──────────────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │   Value Bets     │
                              │   Dashboard      │
                              └──────────────────┘
```

## 🔧 CONFIGURATIE

### Environment Variables (Optioneel)

```bash
# API-Football (optioneel maar aanbevolen)
export API_FOOTBALL_KEY="your_key_here"

# The Odds API (optioneel)
export ODDS_API_KEY="your_key_here"
```

### Zonder API Keys

Het systeem werkt **volledig zonder API keys** via:
- Sofascore public API
- Flashscore public data
- Intelligent fallback systeem

## 📈 DATA QUALITY

### Match Data Betrouwbaarheid

| Bron | Betrouwbaarheid | Matches/dag | Latency |
|------|----------------|-------------|---------|
| Sofascore | ⭐⭐⭐⭐⭐ | 200+ | < 1s |
| API-Football | ⭐⭐⭐⭐⭐ | 150+ | < 2s |
| Flashscore | ⭐⭐⭐⭐ | 100+ | < 3s |
| The Odds API | ⭐⭐⭐⭐ | 80+ | < 2s |
| Fallback | ⭐⭐⭐ | 20+ | Instant |

### Odds Data

**Momenteel GEEN directe odds scraping!**

Alternatief:
- Gebruik The Odds API (aggregeert 50+ bookmakers)
- Handmatige odds input via frontend
- Focus op PROFESSOR voorspellingen ipv odds arbitrage

## 🚀 TOEKOMSTIGE BRONNEN

Potentiële toevoegingen (allemaal public APIs):

1. **FotMob API**
   - Live data, team stats
   - Status: Under consideration

2. **WhoScored API**
   - Player ratings, advanced stats
   - Status: Under consideration

3. **Understat**
   - xG models, shot maps
   - Status: Under consideration

## 📝 CHANGELOG

### November 2025
- ❌ Verwijderd: Alle bookmaker scraping (TOTO, Unibet, Jacks, etc.)
- ✅ Toegevoegd: Sofascore als primaire bron
- ✅ Verbeterd: Flashscore integration
- ✅ Focus: Public APIs only

### Oktober 2025
- Initial scraper development
- TOTO.nl, Unibet, Jacks scrapers (nu deprecated)

---

**Voor vragen over data bronnen**: Zie `backend/ultimate_matches_fetcher.py`

**Voor odds scraping**: Zie `backend/live_odds_scraper.py`
