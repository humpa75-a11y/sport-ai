"""
🏆 LIVE ODDS SCRAPER - SOFASCORE + FLASHSCORE + PREDICTZ
=============================================

Haalt LIVE data op van meerdere publieke bronnen:
- Sofascore: Wedstrijden, teams, xG stats
- Flashscore: Live odds (1X2)
- PredictZ: Community voorspellingen
- ESPN: Backup data

GEEN API-KEYS NODIG - Publieke endpoints!
"""

import requests
import pandas as pd
import time
import json
from datetime import datetime, timedelta
import warnings
import re
from typing import Dict, List, Optional
warnings.filterwarnings("ignore")

# =============================================
# 1. CONFIG: API ENDPOINTS (PUBLIEK, GRATIS, LEGAAL)
# =============================================
SOFASCORE_API = "https://api.sofascore.com/api/v1"
FLASHSCORE_API = "https://d.flashscore.com/x/feed"
PREDICTZ_API = "https://www.predictz.com/predictions"
ESPN_API = "https://site.api.espn.com/apis/site/v2/sports/soccer"

# Headers om te lijken op echte browser (geen blokkade)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.sofascore.com/",
    "Origin": "https://www.sofascore.com"
}

# Cache voor API responses (5 minuten TTL)
_cache = {}
CACHE_TTL = 300  # 5 minuten

def _get_cached(key: str):
    """Haal data uit cache als niet verlopen."""
    if key in _cache:
        data, timestamp = _cache[key]
        if time.time() - timestamp < CACHE_TTL:
            return data
    return None

def _set_cache(key: str, data):
    """Sla data op in cache."""
    _cache[key] = (data, time.time())

# =============================================
# 2. FUNCTIE: HAAL LIVE/VOORBIJE WEDSTRIJDEN (Sofascore)
# =============================================
def get_sofascore_matches(league: str = "bundesliga", date: Optional[str] = None) -> pd.DataFrame:
    """
    Haalt wedstrijden op van Sofascore voor een specifieke competitie.
    
    Args:
        league: Competitie naam (bijv. "bundesliga", "eredivisie", "premier-league")
        date: Datum in YYYY-MM-DD formaat (default: vandaag)
    
    Returns:
        DataFrame met wedstrijden
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    cache_key = f"sofascore_{league}_{date}"
    cached = _get_cached(cache_key)
    if cached is not None:
        print(f"[Sofascore] Cache hit voor {league} {date}")
        return cached
    
    url = f"{SOFASCORE_API}/sport/football/scheduled-events/{date}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            matches = []
            
            for event in data.get('events', []):
                tournament_name = event.get('tournament', {}).get('name', '').lower()
                
                # Filter op league (flexibel: "bundesliga" matched "Bundesliga 1")
                if league.lower() in tournament_name or tournament_name in league.lower():
                    match = {
                        'home': event['homeTeam']['name'],
                        'away': event['awayTeam']['name'],
                        'time': datetime.fromtimestamp(event['startTimestamp']).strftime('%H:%M'),
                        'datetime': datetime.fromtimestamp(event['startTimestamp']),
                        'status': event.get('status', {}).get('type', 'notstarted'),
                        'home_score': event.get('homeScore', {}).get('current'),
                        'away_score': event.get('awayScore', {}).get('current'),
                        'league': event['tournament']['name'],
                        'match_id': event.get('id'),
                        'home_id': event['homeTeam'].get('id'),
                        'away_id': event['awayTeam'].get('id')
                    }
                    matches.append(match)
            
            df = pd.DataFrame(matches)
            _set_cache(cache_key, df)
            print(f"[Sofascore] {len(matches)} wedstrijden gevonden voor {league}")
            return df
        else:
            print(f"[Sofascore] Fout: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        print(f"[Sofascore] Error: {e}")
        return pd.DataFrame()


def get_all_todays_matches() -> pd.DataFrame:
    """
    Haalt ALLE wedstrijden van vandaag + morgen op van Sofascore.
    
    Returns:
        DataFrame met alle wedstrijden
    """
    cache_key = "sofascore_all_today"
    cached = _get_cached(cache_key)
    if cached is not None:
        print("[Sofascore] Cache hit voor alle matches")
        return cached
    
    all_matches = []
    
    # Vandaag + morgen
    for days_ahead in [0, 1]:
        date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        url = f"{SOFASCORE_API}/sport/football/scheduled-events/{date}"
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                for event in data.get('events', []):
                    match = {
                        'home': event['homeTeam']['name'],
                        'away': event['awayTeam']['name'],
                        'time': datetime.fromtimestamp(event['startTimestamp']).strftime('%H:%M'),
                        'datetime': datetime.fromtimestamp(event['startTimestamp']),
                        'status': event.get('status', {}).get('type', 'notstarted'),
                        'home_score': event.get('homeScore', {}).get('current'),
                        'away_score': event.get('awayScore', {}).get('current'),
                        'league': event['tournament']['name'],
                        'country': event['tournament'].get('category', {}).get('name', 'Unknown'),
                        'match_id': event.get('id'),
                        'home_id': event['homeTeam'].get('id'),
                        'away_id': event['awayTeam'].get('id')
                    }
                    all_matches.append(match)
                
                print(f"[Sofascore] {len(data.get('events', []))} wedstrijden gevonden voor {date}")
                time.sleep(0.5)  # Rate limiting
        except Exception as e:
            print(f"[Sofascore] Error voor {date}: {e}")
    
    df = pd.DataFrame(all_matches)
    _set_cache(cache_key, df)
    print(f"[Sofascore] Totaal {len(all_matches)} wedstrijden van vandaag/morgen")
    return df


# =============================================
# 3. FUNCTIE: HAAL ODDS (Flashscore – via open feed)
# =============================================
def get_flashscore_odds(match_id: str) -> Dict:
    """
    Haalt live odds op van Flashscore voor een specifieke wedstrijd.
    
    Args:
        match_id: Sofascore match ID
    
    Returns:
        Dict met odds: {'1': 2.10, 'X': 3.50, '2': 3.20}
    """
    cache_key = f"flashscore_odds_{match_id}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached
    
    url = f"{FLASHSCORE_API}/dc_1_{match_id}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            lines = response.text.split('\n')
            odds = {}
            
            for line in lines:
                if line.startswith('odds'):
                    parts = line.split('~')
                    if len(parts) > 3:
                        odds['1'] = float(parts[1]) if parts[1] != '-' else None
                        odds['X'] = float(parts[2]) if parts[2] != '-' else None
                        odds['2'] = float(parts[3]) if parts[3] != '-' else None
            
            _set_cache(cache_key, odds)
            return odds
        return {}
    except Exception as e:
        print(f"[Flashscore] Error voor match {match_id}: {e}")
        return {}


# =============================================
# 4. FUNCTIE: HAAL VOORSPELLINGEN (PredictZ – via JSON feed)
# =============================================
def get_predictz_predictions(league: str = "germany-bundesliga") -> pd.DataFrame:
    """
    Haalt community voorspellingen op van PredictZ.
    
    Args:
        league: League slug (bijv. "germany-bundesliga", "netherlands-eredivisie")
    
    Returns:
        DataFrame met voorspellingen
    """
    cache_key = f"predictz_{league}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached
    
    url = f"https://www.predictz.com/predictions/{league}/"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            # PredictZ heeft een JSON in de HTML (data-matches)
            json_str = re.search(r'data-matches="([^"]+)"', response.text)
            if json_str:
                data = json.loads(json_str.group(1).replace('&quot;', '"'))
                preds = []
                
                for m in data:
                    preds.append({
                        'home': m['home_team'],
                        'away': m['away_team'],
                        'prediction': m['prediction'],
                        'probability': m.get('probability', 0),
                        'votes': m.get('votes', 0)
                    })
                
                df = pd.DataFrame(preds)
                _set_cache(cache_key, df)
                print(f"[PredictZ] {len(preds)} voorspellingen voor {league}")
                return df
        
        return pd.DataFrame()
    except Exception as e:
        print(f"[PredictZ] Error: {e}")
        return pd.DataFrame()


# =============================================
# 5. FUNCTIE: HAAL TEAM STATS (Sofascore – expected goals, form)
# =============================================
def get_team_xg(team_id: int, season: int = 2024) -> Dict:
    """
    Haalt expected goals en vorm op voor een team.
    
    Args:
        team_id: Sofascore team ID
        season: Seizoen (default: 2024)
    
    Returns:
        Dict met xG stats: {'xg_for': 1.8, 'xg_against': 1.2, 'form': 'WWDLW'}
    """
    cache_key = f"team_xg_{team_id}_{season}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached
    
    url = f"{SOFASCORE_API}/team/{team_id}/statistics/overall/{season}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            stats = response.json()
            xg_data = {
                'xg_for': stats.get('statistics', {}).get('expectedGoals', 0),
                'xg_against': stats.get('statistics', {}).get('expectedGoalsAgainst', 0),
                'form': ''.join([s.get('result', 'D')[0] for s in stats.get('form', [])[-5:]])
            }
            _set_cache(cache_key, xg_data)
            return xg_data
        return {}
    except Exception as e:
        print(f"[Team xG] Error voor team {team_id}: {e}")
        return {}


# =============================================
# 6. HOOFDFUNCTIE: ALLE DATA SAMENVOEGEN
# =============================================
def get_enhanced_matches(league: Optional[str] = None, include_odds: bool = True, 
                        include_xg: bool = True, include_predictz: bool = False) -> List[Dict]:
    """
    🏆 MASTER FUNCTIE - Combineert alle data bronnen
    
    Haalt wedstrijden op en verrijkt ze met:
    - Live odds (Flashscore)
    - Expected Goals (Sofascore)
    - Community voorspellingen (PredictZ - optioneel)
    
    Args:
        league: Specifieke competitie (None = alle wedstrijden)
        include_odds: Haal live odds op
        include_xg: Haal xG stats op
        include_predictz: Haal PredictZ voorspellingen op
    
    Returns:
        List van dicts met alle wedstrijd data
    """
    print("\n" + "="*80)
    print("🏆 ENHANCED MATCHES SCRAPER - SOFASCORE + FLASHSCORE + XG")
    print("="*80)
    
    # 1. Haal wedstrijden op
    if league:
        matches_df = get_sofascore_matches(league=league)
    else:
        matches_df = get_all_todays_matches()
    
    if matches_df.empty:
        print("❌ Geen wedstrijden gevonden")
        return []
    
    print(f"✅ {len(matches_df)} wedstrijden gevonden")
    
    # 2. Verrijk met extra data
    enhanced_matches = []
    
    for idx, match in matches_df.iterrows():
        enhanced = match.to_dict()
        
        # Haal odds op (rate limited)
        if include_odds and match.get('match_id'):
            odds = get_flashscore_odds(match['match_id'])
            enhanced['odds'] = odds
            enhanced['has_odds'] = len(odds) > 0
            time.sleep(0.2)  # Rate limiting
        
        # Haal xG stats op (rate limited)
        if include_xg:
            if match.get('home_id'):
                home_xg = get_team_xg(match['home_id'])
                enhanced['home_xg_for'] = home_xg.get('xg_for', 0)
                enhanced['home_xg_against'] = home_xg.get('xg_against', 0)
                enhanced['home_form'] = home_xg.get('form', 'N/A')
                time.sleep(0.2)
            
            if match.get('away_id'):
                away_xg = get_team_xg(match['away_id'])
                enhanced['away_xg_for'] = away_xg.get('xg_for', 0)
                enhanced['away_xg_against'] = away_xg.get('xg_against', 0)
                enhanced['away_form'] = away_xg.get('form', 'N/A')
                time.sleep(0.2)
        
        enhanced_matches.append(enhanced)
    
    # 3. Optioneel: Voeg PredictZ voorspellingen toe
    if include_predictz and league:
        league_slug = league.lower().replace(' ', '-')
        predictz_df = get_predictz_predictions(league=league_slug)
        
        if not predictz_df.empty:
            for match in enhanced_matches:
                # Match teams (fuzzy matching)
                pred = predictz_df[
                    (predictz_df['home'].str.contains(match['home'], case=False, na=False)) &
                    (predictz_df['away'].str.contains(match['away'], case=False, na=False))
                ]
                
                if not pred.empty:
                    match['predictz_prediction'] = pred.iloc[0]['prediction']
                    match['predictz_probability'] = pred.iloc[0]['probability']
                    match['predictz_votes'] = pred.iloc[0]['votes']
    
    print(f"✅ {len(enhanced_matches)} wedstrijden verrijkt met extra data")
    print("="*80 + "\n")
    
    return enhanced_matches


# =============================================
# 7. LEAGUE SLUGS MAPPING
# =============================================
LEAGUE_SLUGS = {
    'bundesliga': 'germany-bundesliga',
    'eredivisie': 'netherlands-eredivisie',
    'premier league': 'england-premier-league',
    'la liga': 'spain-la-liga',
    'serie a': 'italy-serie-a',
    'ligue 1': 'france-ligue-1',
    'primeira liga': 'portugal-primeira-liga'
}


# =============================================
# 8. DEMO/TEST FUNCTIE
# =============================================
if __name__ == '__main__':
    # Test: Haal Bundesliga wedstrijden op met alle data
    matches = get_enhanced_matches(
        league='bundesliga',
        include_odds=True,
        include_xg=True,
        include_predictz=False  # Tijdrovend, optioneel
    )
    
    print(f"\n📊 RESULTATEN: {len(matches)} wedstrijden\n")
    
    for i, match in enumerate(matches[:3], 1):  # Toon eerste 3
        print(f"{i}. {match['home']} vs {match['away']}")
        print(f"   ⏰ {match['time']} | 🏆 {match['league']}")
        
        if match.get('odds'):
            print(f"   💰 Odds: 1={match['odds'].get('1', 'N/A')} X={match['odds'].get('X', 'N/A')} 2={match['odds'].get('2', 'N/A')}")
        
        if match.get('home_xg_for'):
            print(f"   📈 xG: {match['home_xg_for']:.2f} - {match['away_xg_for']:.2f}")
            print(f"   📊 Vorm: {match.get('home_form', 'N/A')} vs {match.get('away_form', 'N/A')}")
        
        print()
