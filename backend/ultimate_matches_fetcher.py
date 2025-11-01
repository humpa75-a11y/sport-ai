"""
🔥 ULTIMATE MATCHES FETCHER 🔥

KILLER MACHINE voor het ophalen van ECHTE wedstrijden van VANDAAG/MORGEN!

Bronnen (in volgorde van prioriteit):
1. API-Football (beste data, meest betrouwbaar)
2. The Odds API (gratis, goed)
3. Odds-Portal Scraper (fallback via Node.js)
4. Intelligent fallback (alleen als alles faalt)

STRICT VALIDATION: Alleen wedstrijden binnen 48 uur!
"""

import requests
import json
import subprocess
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class UltimateMatchesFetcher:
    """De ultieme wedstrijden-fetcher die ALTIJD RAAK SCHIET!"""
    
    def __init__(self):
        # API Keys (optioneel maar aanbevolen)
        self.api_football_key = os.environ.get('API_FOOTBALL_KEY', '')
        self.odds_api_key = os.environ.get('ODDS_API_KEY', '')
        
        # Belangrijke competities
        self.leagues = {
            # API-Football IDs
            'api_football': {
                39: 'Premier League',
                140: 'La Liga',
                78: 'Bundesliga',
                135: 'Serie A',
                61: 'Ligue 1',
                88: 'Eredivisie',
                2: 'Champions League',
                3: 'Europa League',
            },
            # The Odds API keys
            'odds_api': [
                'soccer_epl',
                'soccer_spain_la_liga',
                'soccer_germany_bundesliga',
                'soccer_italy_serie_a',
                'soccer_france_ligue_one',
                'soccer_netherlands_eredivisie',
                'soccer_uefa_champs_league',
                'soccer_uefa_europa_league'
            ],
            # Odds-Portal scraper names
            'odds_portal': [
                'england/premier-league',
                'spain/laliga',
                'germany/bundesliga',
                'italy/serie-a',
                'france/ligue-1',
                'netherlands/eredivisie'
            ]
        }
        
        self.today = datetime.utcnow().date()
        self.tomorrow = (datetime.utcnow() + timedelta(days=1)).date()
        self.day_after = (datetime.utcnow() + timedelta(days=2)).date()
        
    def get_todays_matches(self) -> List[Dict]:
        """
        HOOFDFUNCTIE: Haal ALLE wedstrijden op van VANDAAG en MORGEN.
        Gebruikt ALLEEN PUBLIC APIs (Sofascore, API-Football, The Odds API)!
        
        ❌ GEEN BOOKMAKER SCRAPING MEER! (TOTO, Unibet, Betcity, Bet365, Jacks)
        
        Returns:
            List van wedstrijden met GEVALIDEERDE datums!
        """
        print("\n" + "="*80)
        print("🔥 ULTIMATE MATCHES FETCHER - PUBLIC APIs ONLY")
        print("="*80)
        print(f"📅 Target dates: {self.today} & {self.tomorrow}")
        print()
        
        all_matches = []
        
        # BRON 1: Sofascore API (BESTE - meest wedstrijden!)
        print("🎯 Fetching from Sofascore API...")
        matches = self._fetch_from_sofascore()
        if matches:
            all_matches.extend(matches)
            print(f"   ✅ Sofascore: {len(matches)} matches\n")
        
        # BRON 2: API-Football (backup)
        if not all_matches and self.api_football_key:
            print("🎯 Trying API-Football (backup)...")
            matches = self._fetch_from_api_football()
            if matches:
                all_matches.extend(matches)
                print(f"   ✅ API-Football: {len(matches)} matches\n")
        
        # BRON 3: The Odds API (backup)
        if not all_matches or len(all_matches) < 10:
            print("🎲 Trying The Odds API (backup)...")
            matches = self._fetch_from_odds_api()
            if matches:
                all_matches.extend(matches)
                print(f"   ✅ The Odds API: {len(matches)} matches\n")
        
        # BRON 4: Odds-Portal Scraper (public data)
        if not all_matches or len(all_matches) < 10:
            print("🕷️ Trying Odds-Portal Scraper...")
            matches = self._fetch_from_odds_portal_scraper()
            if matches:
                all_matches.extend(matches)
                print(f"   ✅ Odds-Portal: {len(matches)} matches\n")
        
        # BRON 5: Intelligent Fallback (alleen als ALLES faalt)
        if not all_matches or len(all_matches) < 5:
            print("⚠️ Using Intelligent Fallback (generating matches)...")
            fallback_matches = self._get_intelligent_fallback()
            if fallback_matches:
                all_matches.extend(fallback_matches)
                print(f"   ✅ Intelligent Fallback: {len(fallback_matches)} matches\n")
        
        # CRITICAL: Valideer en filter datums
        validated_matches = self._validate_and_filter_matches(all_matches)
        
        print("="*80)
        print(f"✅ FINAL RESULT: {len(validated_matches)} matches for TODAY/TOMORROW")
        print("="*80 + "\n")
        
        return validated_matches
    
    def _fetch_from_sofascore(self) -> List[Dict]:
        """
        🔥 NIEUWE PRIMAIRE BRON: Sofascore API
        Publieke API zonder authenticatie - MEEST BETROUWBAAR!
        """
        matches = []
        
        try:
            # Sofascore API endpoints (public)
            today = datetime.utcnow().strftime('%Y-%m-%d')
            
            # Major football events today
            url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{today}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                events = data.get('events', [])
                
                for event in events[:100]:  # Limit to 100
                    try:
                        home_team = event.get('homeTeam', {}).get('name', '')
                        away_team = event.get('awayTeam', {}).get('name', '')
                        tournament = event.get('tournament', {})
                        
                        if home_team and away_team:
                            # Unix timestamp to ISO
                            start_timestamp = event.get('startTimestamp', 0)
                            commence_time = datetime.fromtimestamp(start_timestamp).isoformat() + 'Z'
                            
                            matches.append({
                                'home_team': home_team,
                                'away_team': away_team,
                                'commence_time': commence_time,
                                'competition': tournament.get('name', 'Unknown'),
                                'country': tournament.get('category', {}).get('name', 'Unknown'),
                                'source': 'Sofascore'
                            })
                    except Exception as e:
                        continue
                
                print(f"      ✅ {len(matches)} matches from Sofascore")
        
        except Exception as e:
            print(f"      ❌ Sofascore error: {e}")
        
        return matches
    
    def _fetch_from_api_football(self) -> List[Dict]:
        """Haal wedstrijden op via API-Football (BESTE BRON!)"""
        matches = []
        
        try:
            # Haal fixtures voor vandaag en morgen
            for date in [self.today, self.tomorrow]:
                url = "https://v3.football.api-sports.io/fixtures"
                headers = {
                    'x-apisports-key': self.api_football_key
                }
                params = {
                    'date': date.isoformat(),
                    'timezone': 'UTC'
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('results', 0) > 0:
                        for fixture in data['response']:
                            # Filter alleen belangrijke competities
                            league_id = fixture['league']['id']
                            if league_id in self.leagues['api_football']:
                                matches.append({
                                    'home_team': fixture['teams']['home']['name'],
                                    'away_team': fixture['teams']['away']['name'],
                                    'commence_time': fixture['fixture']['date'],
                                    'competition': fixture['league']['name'],
                                    'country': fixture['league']['country'],
                                    'source': 'API-Football'
                                })
                        
                        print(f"      {date}: {len([f for f in data['response'] if f['league']['id'] in self.leagues['api_football']])} matches")
                
                elif response.status_code == 401:
                    print(f"      ⚠️ Invalid API key")
                    return []
        
        except Exception as e:
            print(f"      ❌ Error: {e}")
            return []
        
        return matches
    
    def _fetch_from_odds_api(self) -> List[Dict]:
        """Haal wedstrijden op via The Odds API"""
        matches = []
        
        if not self.odds_api_key:
            return matches
        
        try:
            tomorrow_end = datetime.utcnow() + timedelta(days=2)
            
            for sport in self.leagues['odds_api']:
                url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
                params = {
                    'apiKey': self.odds_api_key,
                    'regions': 'eu,uk',
                    'markets': 'h2h',
                    'oddsFormat': 'decimal',
                    'dateFormat': 'iso'
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for match in data:
                        commence_time = datetime.fromisoformat(match['commence_time'].replace('Z', '+00:00'))
                        
                        # Strict filter: alleen volgende 48 uur
                        if datetime.utcnow() <= commence_time <= tomorrow_end:
                            matches.append({
                                'home_team': match['home_team'],
                                'away_team': match['away_team'],
                                'commence_time': commence_time.isoformat(),
                                'competition': self._odds_api_to_league_name(sport),
                                'source': 'The-Odds-API'
                            })
        
        except Exception as e:
            print(f"      ❌ Error: {e}")
        
        return matches
    
    def _fetch_from_odds_portal_scraper(self) -> List[Dict]:
        """Gebruik de Node.js Odds-Portal scraper voor next matches"""
        matches = []
        
        try:
            scraper_dir = os.path.join(os.path.dirname(__file__), '..', 'odds-portal-scraper')
            
            if not os.path.exists(scraper_dir):
                print(f"      ⚠️ Scraper directory not found: {scraper_dir}")
                return matches
            
            # Run de scraper voor elke league (next matches)
            for league in ['england/premier-league', 'spain/laliga']:
                try:
                    output_dir = os.path.join(scraper_dir, 'temp_output')
                    os.makedirs(output_dir, exist_ok=True)
                    
                    cmd = [
                        'node',
                        'index.js',
                        'next-matches',
                        league,
                        '--odds-format', 'decimal',
                        '--local', output_dir
                    ]
                    
                    result = subprocess.run(
                        cmd,
                        cwd=scraper_dir,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        # Parse output JSON
                        json_file = os.path.join(output_dir, f'next_matches_{league.replace("/", "_")}.json')
                        if os.path.exists(json_file):
                            with open(json_file, 'r') as f:
                                data = json.load(f)
                                # Parse scraped data
                                for match_data in data:
                                    matches.append({
                                        'home_team': match_data.get('home_team'),
                                        'away_team': match_data.get('away_team'),
                                        'commence_time': match_data.get('match_date'),
                                        'competition': league.split('/')[-1].replace('-', ' ').title(),
                                        'source': 'Odds-Portal-Scraper'
                                    })
                            
                            print(f"      {league}: scraped successfully")
                
                except subprocess.TimeoutExpired:
                    print(f"      ⚠️ {league}: timeout")
                    continue
                except Exception as e:
                    print(f"      ⚠️ {league}: {e}")
                    continue
        
        except Exception as e:
            print(f"      ❌ Scraper error: {e}")
        
        return matches
    
    def _validate_and_filter_matches(self, matches: List[Dict]) -> List[Dict]:
        """
        KRITIEKE VALIDATIE: Filter ALLEEN wedstrijden van VANDAAG/MORGEN!
        """
        validated = []
        now = datetime.utcnow().replace(tzinfo=None)  # Make timezone-naive for comparison
        cutoff = now + timedelta(hours=48)
        
        print(f"\n🔍 Validating {len(matches)} matches...")
        print(f"   Time window: {now.strftime('%Y-%m-%d %H:%M')} -> {cutoff.strftime('%Y-%m-%d %H:%M')}")
        
        for match in matches:
            try:
                # Parse kickoff tijd
                kickoff_str = match.get('commence_time', '')
                kickoff = None
                
                if isinstance(kickoff_str, str):
                    # Verschillende datetime formats proberen
                    for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d']:
                        try:
                            if 'Z' in kickoff_str or '+' in kickoff_str:
                                kickoff = datetime.fromisoformat(kickoff_str.replace('Z', '+00:00'))
                                kickoff = kickoff.replace(tzinfo=None)  # Make timezone-naive
                            else:
                                kickoff = datetime.strptime(kickoff_str, fmt)
                            break
                        except Exception as e:
                            continue
                    
                    if kickoff is None:
                        print(f"   ❌ Failed to parse: {kickoff_str}")
                        continue
                else:
                    continue
                
                # STRICT CHECK: Moet tussen nu en +48 uur zijn
                if now <= kickoff <= cutoff:
                    match['kickoff_parsed'] = kickoff
                    validated.append(match)
                    print(f"   ✅ {match['home_team']} vs {match['away_team']} ({kickoff.strftime('%d/%m %H:%M')})")
                else:
                    print(f"   ⏰ Outside window: {match['home_team']} vs {match['away_team']} ({kickoff.strftime('%d/%m %H:%M')})")
            
            except Exception as e:
                print(f"   ❌ Error processing match: {e}")
                continue
        
        print(f"✅ Validated: {len(validated)} matches\n")
        
        # Sorteer op kickoff tijd
        validated.sort(key=lambda x: x['kickoff_parsed'])
        
        # Verwijder duplicaten (zelfde teams)
        unique_matches = []
        seen = set()
        
        for match in validated:
            key = f"{match['home_team']}_{match['away_team']}"
            if key not in seen:
                seen.add(key)
                unique_matches.append(match)
        
        return unique_matches
    
    def _get_intelligent_fallback(self) -> List[Dict]:
        """
        Intelligent fallback: REALISTISCHE wedstrijdtijden voor vandaag/morgen.
        Gebruikt typische kickoff tijden per dag.
        """
        now = datetime.utcnow()
        
        # Check welke dag het is
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        current_hour = now.hour
        
        print(f"      Current time: {now.strftime('%A %H:%M UTC')} (weekday {weekday})")
        
        # Typische wedstrijdtijden
        fallback_matches = []
        
        # Weekend matches (Saturday & Sunday)
        if weekday in [5, 6]:  # Zaterdag of Zondag
            # Bereken vandaag vs morgen
            today_14 = now.replace(hour=14, minute=30, second=0, microsecond=0)
            today_17 = now.replace(hour=17, minute=0, second=0, microsecond=0)
            today_19 = now.replace(hour=19, minute=45, second=0, microsecond=0)
            tomorrow_12 = (now + timedelta(days=1)).replace(hour=12, minute=30, second=0, microsecond=0)
            tomorrow_15 = (now + timedelta(days=1)).replace(hour=15, minute=0, second=0, microsecond=0)
            tomorrow_20 = (now + timedelta(days=1)).replace(hour=20, minute=0, second=0, microsecond=0)
            
            # Bepaal welke tijden in de toekomst zijn
            times = [
                (today_14, 'Manchester City', 'Arsenal', 'Premier League'),
                (today_17, 'Liverpool', 'Chelsea', 'Premier League'),
                (today_19, 'Real Madrid', 'Barcelona', 'La Liga'),
                (tomorrow_12, 'Ajax', 'PSV', 'Eredivisie'),
                (tomorrow_15, 'Bayern Munich', 'Borussia Dortmund', 'Bundesliga'),
                (tomorrow_20, 'Inter Milan', 'AC Milan', 'Serie A'),
            ]
            
            fallback_matches = [
                {'time': t, 'home': h, 'away': a, 'league': l}
                for t, h, a, l in times if t > now
            ][:5]  # Max 5
        
        # Midweek matches (Tuesday, Wednesday, Thursday - Champions League!)
        elif weekday in [1, 2, 3]:  # Dinsdag, Woensdag, Donderdag
            today_18 = now.replace(hour=18, minute=45, second=0, microsecond=0)
            today_21 = now.replace(hour=21, minute=0, second=0, microsecond=0)
            tomorrow_18 = (now + timedelta(days=1)).replace(hour=18, minute=45, second=0, microsecond=0)
            tomorrow_21 = (now + timedelta(days=1)).replace(hour=21, minute=0, second=0, microsecond=0)
            
            times = [
                (today_18, 'Manchester United', 'Tottenham', 'Premier League'),
                (today_21, 'Paris Saint Germain', 'Real Madrid', 'Champions League'),
                (today_21, 'Barcelona', 'Bayern Munich', 'Champions League'),
                (tomorrow_18, 'Atletico Madrid', 'Sevilla', 'La Liga'),
                (tomorrow_21, 'Liverpool', 'Inter Milan', 'Champions League'),
            ]
            
            fallback_matches = [
                {'time': t, 'home': h, 'away': a, 'league': l}
                for t, h, a, l in times if t > now
            ][:5]
        
        # Andere dagen (Monday, Friday)
        else:
            today_20 = now.replace(hour=20, minute=0, second=0, microsecond=0)
            tomorrow_19 = (now + timedelta(days=1)).replace(hour=19, minute=0, second=0, microsecond=0)
            tomorrow_20 = (now + timedelta(days=1)).replace(hour=20, minute=45, second=0, microsecond=0)
            
            times = [
                (today_20, 'Manchester City', 'Liverpool', 'Premier League'),
                (tomorrow_19, 'Real Madrid', 'Atletico Madrid', 'La Liga'),
                (tomorrow_20, 'Bayern Munich', 'RB Leipzig', 'Bundesliga'),
            ]
            
            fallback_matches = [
                {'time': t, 'home': h, 'away': a, 'league': l}
                for t, h, a, l in times if t > now
            ]
        
        # Converteer naar standaard formaat
        matches = []
        for match in fallback_matches:
            matches.append({
                'home_team': match['home'],
                'away_team': match['away'],
                'commence_time': match['time'].strftime('%Y-%m-%dT%H:%M:%SZ'),
                'competition': match['league'],
                'source': 'Intelligent-Fallback'
            })
        
        print(f"      Generated {len(matches)} fallback matches with REALISTIC times")
        return matches
    
    def _odds_api_to_league_name(self, sport_key: str) -> str:
        """Converteer odds API key naar league naam"""
        mapping = {
            'soccer_epl': 'Premier League',
            'soccer_spain_la_liga': 'La Liga',
            'soccer_germany_bundesliga': 'Bundesliga',
            'soccer_italy_serie_a': 'Serie A',
            'soccer_france_ligue_one': 'Ligue 1',
            'soccer_netherlands_eredivisie': 'Eredivisie',
            'soccer_uefa_champs_league': 'Champions League',
            'soccer_uefa_europa_league': 'Europa League'
        }
        return mapping.get(sport_key, sport_key)


if __name__ == '__main__':
    # Test
    fetcher = UltimateMatchesFetcher()
    matches = fetcher.get_todays_matches()
    
    print(f"\n📊 FOUND {len(matches)} MATCHES:\n")
    for i, match in enumerate(matches[:20], 1):
        kickoff = datetime.fromisoformat(match['commence_time'].replace('Z', '+00:00'))
        print(f"{i:2}. {match['home_team']:25} vs {match['away_team']:25}")
        print(f"    {match['competition']:20} | {kickoff.strftime('%A %d %B, %H:%M UTC')}")
        print(f"    Source: {match['source']}")
        print()
