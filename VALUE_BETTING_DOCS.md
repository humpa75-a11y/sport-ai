# 🎯 POISSON VALUE ENGINE - Documentatie

## Overzicht

De **Poisson Value Engine** integreert professionele betting analyse met PROFESSOR DE MEESTER. Het systeem gebruikt:

- **Poisson-verdelingen** voor doelpunten simulaties
- **Expected Value (EV)** berekeningen voor objectieve bet evaluatie
- **Monte Carlo simulaties** (100 runs per wedstrijd)
- **PROFESSOR voorspellingen** als basis voor Expected Goals

## ✨ Wat is Value Betting?

**Value betting** betekent weddenschappen plaatsen waar de bookmaker odds **hoger** zijn dan de werkelijke kans. Dit geeft een **positieve Expected Value (EV)**.

### Expected Value Formule

```
EV = (Probability × (Odds - 1)) - (1 - Probability)

EV > 0 = VALUE BET! 💰
EV < 0 = Slechte bet
```

### Voorbeeld

- **PROFESSOR voorspelling**: Ajax wint met 65% kans
- **Bookmaker odds**: 2.10 voor Ajax
- **Implied probability**: 1/2.10 = 47.6%
- **EV**: (0.65 × 1.10) - 0.35 = **+0.365 (+36.5%!)**

Dit is een **sterke value bet** omdat de PROFESSOR de kans hoger inschat dan de bookmaker!

---

## 🚀 Installatie

### 1. Installeer Dependencies

```bash
pip install scipy numpy pandas
```

(Deze zijn al geïnstalleerd als je requirements.txt hebt gebruikt)

### 2. Start de Backend

```bash
cd backend
python app.py
```

Je ziet:
```
🎯 Poisson Value Engine geactiveerd! (100 simulaties per match)
```

---

## 📡 API Endpoints

### 1️⃣ `/api/value-betting` (POST)

**Single match value analyse** - Volledig rapport met value bets + accumulators

#### Request Body

```json
{
  "home_team": "Ajax",
  "away_team": "PSV",
  "odds_1x2": [2.10, 3.50, 3.20],
  "odds_markets": {
    "over_2_5": 1.80,
    "btts": 1.75,
    "over_1_5": 1.35,
    "under_2_5": 2.00,
    "over_3_5": 2.50
  },
  "speelronde": 12
}
```

**Vereist**:
- `home_team`, `away_team`: Team namen
- `odds_1x2`: [Home Win, Draw, Away Win] odds

**Optioneel**:
- `odds_markets`: Extra markten (Over/Under, BTTS)
- `speelronde`: Ronde nummer (default: 19)

#### Response

```json
{
  "match": "Ajax vs PSV",
  "professor_prediction": {
    "home_goals": 2.1,
    "away_goals": 1.4,
    "total_goals": 3.5
  },
  "simulation_stats": {
    "p_home_win": 0.58,
    "p_draw": 0.24,
    "p_away_win": 0.18,
    "p_over_2_5": 0.72,
    "p_btts_yes": 0.63,
    "exact_scores": [
      {"score": "2-1", "probability": 0.18},
      {"score": "3-1", "probability": 0.14},
      {"score": "1-1", "probability": 0.12}
    ]
  },
  "value_bets": [
    {
      "market": "1X2",
      "bet": "Home Win",
      "odds": 2.10,
      "probability": 0.58,
      "ev": 0.258,
      "ev_percentage": 25.8,
      "implied_odds": 1.72
    }
  ],
  "best_accumulator": {
    "num_bets": 3,
    "total_odds": 8.91,
    "win_probability_pct": 24.36,
    "potential_win": 89.10,
    "expected_return": 21.71
  },
  "betting_advice": {
    "advice": "STERKE VALUE BET - Hoge confidence",
    "risk_level": "LAAG RISICO 🟢",
    "best_bet": "Home Win @ 2.10",
    "expected_value": "+25.8%",
    "strategy": "Single bet op Home Win @ 2.10 OF maak 3-fold accumulator"
  }
}
```

---

### 2️⃣ `/api/value-betting/batch` (POST)

**Batch analyse** - Analyseer meerdere wedstrijden + genereer accumulators

#### Request Body

```json
{
  "matches": [
    {
      "home_team": "Ajax",
      "away_team": "PSV",
      "odds_1x2": [2.10, 3.50, 3.20]
    },
    {
      "home_team": "Feyenoord",
      "away_team": "AZ",
      "odds_1x2": [1.80, 3.60, 4.20]
    },
    {
      "home_team": "FC Twente",
      "away_team": "FC Utrecht",
      "odds_1x2": [2.00, 3.40, 3.80]
    }
  ],
  "speelronde": 12
}
```

#### Response

```json
{
  "total_matches_analyzed": 3,
  "total_value_bets_found": 8,
  "top_single_bets": [
    {
      "match": "Ajax vs PSV",
      "bet": "Home Win",
      "odds": 2.10,
      "ev_percentage": 25.8
    }
  ],
  "recommended_accumulators": [
    {
      "type": "4-Fold",
      "total_odds": 42.56,
      "win_probability_pct": 8.24,
      "potential_win": 425.60,
      "bets": [...]
    },
    {
      "type": "3-Fold",
      "total_odds": 12.34,
      "win_probability_pct": 18.45,
      "potential_win": 123.40
    }
  ],
  "summary": {
    "best_ev_bet": {...},
    "best_accumulator": {...},
    "average_ev": 0.145
  }
}
```

---

## 🧪 Testen

### Quick Test

```bash
python test_value_betting.py
```

Dit test:
1. ✅ Single match analyse (Ajax vs PSV)
2. ✅ Batch analyse (4 Eredivisie matches)
3. ✅ Bundesliga voorbeeld (reproduceert jouw originele script)

### Manual Test met cURL

```bash
# Windows PowerShell
$body = @{
    home_team = "Ajax"
    away_team = "PSV"
    odds_1x2 = @(2.10, 3.50, 3.20)
} | ConvertTo-Json

curl -X POST http://127.0.0.1:5000/api/value-betting -H "Content-Type: application/json" -d $body
```

---

## 💡 Gebruik Cases

### 1. Single Match Analyse

**Wanneer?** Je wilt weten of een specifieke bet value heeft

**Voorbeeld**:
```python
import requests

response = requests.post("http://127.0.0.1:5000/api/value-betting", json={
    "home_team": "Ajax",
    "away_team": "PSV",
    "odds_1x2": [2.10, 3.50, 3.20],
    "odds_markets": {
        "over_2_5": 1.80,
        "btts": 1.75
    }
})

result = response.json()
print(f"Value bets: {len(result['value_bets'])}")
print(f"Beste bet: {result['betting_advice']['best_bet']}")
print(f"EV: {result['betting_advice']['expected_value']}")
```

---

### 2. Speeldag Analyse

**Wanneer?** Hele Eredivisie ronde - vind beste bets + accumulators

**Voorbeeld**:
```python
import requests

# Haal odds op van je bookmaker API
matches = [
    {"home_team": "Ajax", "away_team": "PSV", "odds_1x2": [2.10, 3.50, 3.20]},
    {"home_team": "Feyenoord", "away_team": "AZ", "odds_1x2": [1.80, 3.60, 4.20]},
    # ... meer matches
]

response = requests.post("http://127.0.0.1:5000/api/value-betting/batch", json={
    "matches": matches,
    "speelronde": 12
})

report = response.json()

# Top 5 value bets
for bet in report['top_single_bets'][:5]:
    print(f"{bet['match']}: {bet['bet']} @ {bet['odds']} (EV: +{bet['ev_percentage']:.1f}%)")

# Beste accumulator
best_acca = report['recommended_accumulators'][0]
print(f"\nBeste Acca: {best_acca['type']}")
print(f"Odds: {best_acca['total_odds']}x")
print(f"€10 → €{best_acca['potential_win']:.2f}")
```

---

### 3. Live Odds Integratie

**Combine met bookmaker API's**:

```python
import requests

# Stap 1: Haal live odds op (bijv. The Odds API)
odds_response = requests.get(
    "https://api.the-odds-api.com/v4/sports/soccer_netherlands_eredivisie/odds",
    params={"apiKey": "YOUR_KEY", "regions": "eu", "markets": "h2h,totals,btts"}
)

# Stap 2: Converteer naar value betting format
matches = []
for game in odds_response.json():
    matches.append({
        "home_team": game['home_team'],
        "away_team": game['away_team'],
        "odds_1x2": [
            game['bookmakers'][0]['markets'][0]['outcomes'][0]['price'],  # Home
            game['bookmakers'][0]['markets'][0]['outcomes'][1]['price'],  # Draw
            game['bookmakers'][0]['markets'][0]['outcomes'][2]['price']   # Away
        ]
    })

# Stap 3: Analyseer met PROFESSOR
response = requests.post("http://127.0.0.1:5000/api/value-betting/batch", json={
    "matches": matches
})

report = response.json()
# Voila! Automatische value bets voor alle live matches
```

---

## 📊 Markten & Analyses

De engine analyseert automatisch:

### 1X2 Market
- ✅ Home Win
- ✅ Draw
- ✅ Away Win

### Over/Under Market
- ✅ Over 0.5
- ✅ Over 1.5
- ✅ Over 2.5 (most popular)
- ✅ Over 3.5
- ✅ Over 4.5
- ✅ Under 2.5

### BTTS (Both Teams To Score)
- ✅ BTTS Yes
- ✅ BTTS No

### Handicap Market
- ✅ Home -1.5
- ✅ Home -0.5
- ✅ Away -1.5
- ✅ Away -0.5

### Exact Scores
- ✅ Top 5 meest waarschijnlijke scores
- ✅ Met exacte kansen (uit 100 simulaties)

---

## 🎯 Interpretatie van Resultaten

### Expected Value (EV)

| EV | Betekenis | Actie |
|----|-----------|-------|
| **> +0.15** | 🟢 Zeer sterke value | Bet met confidence! |
| **+0.08 tot +0.15** | 🟡 Goede value | Redelijke bet |
| **+0.05 tot +0.08** | 🟠 Marginale value | Voorzichtig betten |
| **< +0.05** | 🔴 Geen value | Skip deze bet |

### Win Probability

| Kans | Accumulators | Strategie |
|------|--------------|-----------|
| **> 60%** | Geschikt voor singles | Hoge stakes OK |
| **40-60%** | Combine in doubles | Medium stakes |
| **20-40%** | Alleen in 3-4 folds | Low stakes |
| **< 20%** | Monster accas only | €1 fun bets |

### Confidence Distribution

```
PROFESSOR Prediction: 2.1 - 1.4
├─ Simulation Mean: 2.08 - 1.38
├─ Over 2.5: 72% kans
└─ Most Likely: 2-1 (18% kans)
```

---

## 🔧 Technische Details

### Poisson Distributie

De engine gebruikt **scipy.stats.poisson** voor doelpunten generatie:

```python
home_goals = poisson.rvs(2.1, size=100)  # 100 random samples
away_goals = poisson.rvs(1.4, size=100)
```

Dit simuleert 100 mogelijke wedstrijden op basis van PROFESSOR's Expected Goals.

### Expected Value Berekening

```python
def calculate_ev(probability, odds):
    return (probability * (odds - 1)) - (1 - probability)
```

### Accumulator Odds

```python
total_odds = bet1_odds × bet2_odds × bet3_odds
total_prob = bet1_prob × bet2_prob × bet3_prob
```

---

## 🎓 Vergelijking met Originele Script

| Aspect | Jouw Script | PROFESSOR Value Engine |
|--------|-------------|------------------------|
| **Simulaties** | 20 runs | 100 runs (5x nauwkeuriger) |
| **Expected Goals** | Handmatig ingevoerd | Automatisch van PROFESSOR |
| **Markten** | 1X2, O/U, BTTS | 1X2, O/U, BTTS, Handicaps, Exact |
| **Output** | Print statements | JSON API responses |
| **Integratie** | Standalone script | Part of Flask backend |
| **Teams** | Bundesliga hardcoded | Alle Eredivisie + EU leagues |
| **Accumulators** | Top 4 & 7 | Dynamisch (2-7 fold) |

---

## 🚨 Belangrijke Disclaimers

### ⚠️ Responsible Gambling

- **Value betting is geen garantie op winst**
- De EV is een **langetermijn statistiek** (100+ bets)
- Gebruik **bankroll management** (max 1-2% per bet)
- **Stop bij verliezen** - never chase losses

### 📊 Model Limitations

- PROFESSOR gebruikt **historische data** (2014-2024)
- **Injuries, suspensions, vorm** zijn niet real-time
- **Bookmaker odds** kunnen betere info hebben
- Gebruik dit als **tool**, niet als heilige graal

### 🔍 Best Practices

1. **Vergelijk meerdere bookmakers** - gebruik hoogste odds
2. **Check lineups** 30 min voor kick-off
3. **Start small** - test met €1-5 bets
4. **Track resultaten** - gebruik `/api/learn` endpoint
5. **Update PROFESSOR** - laat AI leren van echte results

---

## 📈 Roadmap

### In Development
- [ ] Live odds API integratie (The Odds API)
- [ ] Automated bet placement (via bookmaker API's)
- [ ] Performance tracking dashboard
- [ ] Kelly Criterion stake calculator
- [ ] Asian Handicap market support

### Future Ideas
- [ ] Machine learning voor odds movement prediction
- [ ] Arbitrage opportunity detection
- [ ] Closing Line Value (CLV) analysis
- [ ] Bookmaker comparison tool

---

## 🆘 Troubleshooting

### "Poisson Value Engine niet beschikbaar"

**Oplossing**:
```bash
pip install scipy
# Restart backend
python backend/app.py
```

### "Geen value bets gevonden"

**Oorzaken**:
- Bookmaker odds zijn te laag (efficient market)
- PROFESSOR schat teams anders in
- Probeer andere wedstrijden of markten

### "Model niet geladen"

**Check**:
```bash
ls data/de_meester_ULTIMATE_PLUS.pkl
# Of
ls data/de_meester_HYPER.pkl
```

---

## 📞 Support

**Issues?** Open een issue op GitHub of check de logs:

```bash
# Backend logs
tail -f backend/logs/app.log

# Test output
python test_value_betting.py > test_results.txt
```

---

## 🎉 Credits

- **Original Poisson Script**: Jouw Bundesliga analyse
- **PROFESSOR DE MEESTER**: 30,167 matches trained model
- **scipy.stats.poisson**: Wetenschappelijke basis
- **Expected Value Theory**: Professionele betting wiskunde

---

**Made with 💚 by PROFESSOR DE MEESTER**  
*The AI that brings math to betting* 🎓⚽💰
