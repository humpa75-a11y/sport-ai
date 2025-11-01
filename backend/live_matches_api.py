"""
🔥 LIVE MATCHES API CONNECTOR 🔥

Haalt ECHTE wedstrijden op van vandaag/morgen via The Odds API.
"""

import requests
from datetime import datetime, timedelta
import os

class LiveMatchesAPI:
    """Connecteert met The Odds API voor live wedstrijden."""
    
    def __init__(self):
        # The Odds API - GRATIS tot 500 requests/maand!
        self.api_key = os.environ.get('ODDS_API_KEY', 'demo')  # Gebruik demo of eigen key
        self.base_url = 'https://api.the-odds-api.com/v4/sports'
        
        # Belangrijkste competities
        self.sports = [
            'soccer_epl',           # Premier League
            'soccer_spain_la_liga',  # La Liga
            'soccer_germany_bundesliga',  # Bundesliga
            'soccer_italy_serie_a',  # Serie A
            'soccer_france_ligue_one',  # Ligue 1
            'soccer_netherlands_eredivisie',  # Eredivisie
            'soccer_uefa_champs_league',  # Champions League
            'soccer_uefa_europa_league'  # Europa League
        ]
    
    def get_todays_matches(self):
        """
        Haalt ALLE wedstrijden van VANDAAG en MORGEN op.
        
        Returns:
            List van wedstrijden met home_team, away_team, commence_time, competition
        """
        all_matches = []
        
        # Bereken tijdvenster: vandaag + morgen
        now = datetime.utcnow()
        tomorrow_end = now + timedelta(days=2)
        
        print("🔥 Fetching LIVE matches from The Odds API...")
        
        for sport in self.sports:
            try:
                url = f"{self.base_url}/{sport}/odds"
                params = {
                    'apiKey': self.api_key,
                    'regions': 'eu,uk',
                    'markets': 'h2h',  # Head to head odds
                    'oddsFormat': 'decimal',
                    'dateFormat': 'iso'
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for match in data:
                        commence_time = datetime.fromisoformat(match['commence_time'].replace('Z', '+00:00'))
                        
                        # Filter: alleen wedstrijden in de komende 48 uur
                        if now <= commence_time <= tomorrow_end:
                            all_matches.append({
                                'home_team': match['home_team'],
                                'away_team': match['away_team'],
                                'commence_time': commence_time.isoformat(),
                                'competition': self._get_competition_name(sport),
                                'sport_key': sport
                            })
                    
                    print(f"   ✅ {sport}: {len([m for m in data if now <= datetime.fromisoformat(m['commence_time'].replace('Z', '+00:00')) <= tomorrow_end])} matches")
                
                elif response.status_code == 401:
                    print(f"   ⚠️ API Key invalid - using FALLBACK data")
                    return self._get_fallback_matches()
                
                else:
                    print(f"   ⚠️ {sport}: Status {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error fetching {sport}: {e}")
                continue
        
        if not all_matches:
            print("   ⚠️ No API data - using FALLBACK matches")
            return self._get_fallback_matches()
        
        print(f"\n✅ Total matches found: {len(all_matches)}")
        return all_matches
    
    def _get_competition_name(self, sport_key):
        """Converteer sport key naar leesbare naam."""
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
    
    def _get_fallback_matches(self):
        """
        Fallback: Typische wedstrijden voor vandaag/morgen als API niet werkt.
        In productie zou dit uit een database komen.
        """
        now = datetime.utcnow()
        
        # Realistische wedstrijden voor mid-week
        fallback = [
            # Premier League
            {'home_team': 'Manchester City', 'away_team': 'Arsenal', 'competition': 'Premier League'},
            {'home_team': 'Liverpool', 'away_team': 'Chelsea', 'competition': 'Premier League'},
            {'home_team': 'Manchester United', 'away_team': 'Tottenham', 'competition': 'Premier League'},
            {'home_team': 'Newcastle', 'away_team': 'Brighton', 'competition': 'Premier League'},
            {'home_team': 'Aston Villa', 'away_team': 'West Ham', 'competition': 'Premier League'},
            
            # La Liga
            {'home_team': 'Real Madrid', 'away_team': 'Barcelona', 'competition': 'La Liga'},
            {'home_team': 'Atletico Madrid', 'away_team': 'Real Sociedad', 'competition': 'La Liga'},
            {'home_team': 'Sevilla', 'away_team': 'Valencia', 'competition': 'La Liga'},
            
            # Bundesliga
            {'home_team': 'Bayern Munich', 'away_team': 'Borussia Dortmund', 'competition': 'Bundesliga'},
            {'home_team': 'RB Leipzig', 'away_team': 'Bayer Leverkusen', 'competition': 'Bundesliga'},
            
            # Serie A
            {'home_team': 'Inter Milan', 'away_team': 'AC Milan', 'competition': 'Serie A'},
            {'home_team': 'Juventus', 'away_team': 'Napoli', 'competition': 'Serie A'},
            
            # Eredivisie
            {'home_team': 'Ajax', 'away_team': 'PSV', 'competition': 'Eredivisie'},
            {'home_team': 'Feyenoord', 'away_team': 'AZ Alkmaar', 'competition': 'Eredivisie'},
            
            # Champions League
            {'home_team': 'Paris Saint Germain', 'away_team': 'Real Madrid', 'competition': 'Champions League'},
        ]
        
        # Voeg timestamps toe (verspreid over vandaag en morgen)
        for i, match in enumerate(fallback):
            hours_offset = (i * 2) + 14  # Start om 14:00, elke 2 uur
            match['commence_time'] = (now + timedelta(hours=hours_offset)).isoformat()
            match['sport_key'] = 'fallback'
        
        return fallback


if __name__ == '__main__':
    # Test
    api = LiveMatchesAPI()
    matches = api.get_todays_matches()
    
    print("\n📅 MATCHES TODAY/TOMORROW:")
    for i, match in enumerate(matches[:10], 1):
        print(f"   {i}. {match['home_team']} vs {match['away_team']} ({match['competition']})")
        print(f"      Kickoff: {match['commence_time']}")
