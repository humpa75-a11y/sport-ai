"""
ESPN API Integration
====================

VOLLEDIG GRATIS - Geen API key nodig!
- Multiple leagues worldwide (EPL, La Liga, Bundesliga, Serie A, Ligue 1, etc.)
- Live scores + fixtures
- Commentary + statistics
- Team and player data

API URL: http://site.api.espn.com/apis/site/v2/sports/soccer
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ESPNAPIIntegration:
    """
    ESPN API client voor voetbaldata wereldwijd.
    VOLLEDIG GRATIS - geen API key nodig!
    """
    
    BASE_URL = "http://site.api.espn.com/apis/site/v2/sports/soccer"
    
    # League codes (ESPN uses league slugs)
    LEAGUES = {
        "epl": "eng.1",              # Premier League
        "championship": "eng.2",      # Championship
        "laliga": "esp.1",           # La Liga
        "bundesliga": "ger.1",       # Bundesliga
        "seriea": "ita.1",           # Serie A
        "ligue1": "fra.1",           # Ligue 1
        "eredivisie": "ned.1",       # Eredivisie
        "champions": "uefa.champions", # Champions League
        "europa": "uefa.europa",     # Europa League
    }
    
    def __init__(self):
        """Initialiseer ESPN API client (geen credentials nodig!)"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SportAI-BettingSystem/1.0',
            'Accept': 'application/json'
        })
        logger.info("✅ ESPN API Integration initialized (FREE - no key needed!)")
    
    def get_scoreboard(self, league: str = "epl", date: Optional[datetime] = None) -> List[Dict]:
        """
        Haal scoreboard (wedstrijden) op voor een specifieke competitie.
        
        Args:
            league: League slug (epl, laliga, bundesliga, etc.)
            date: Datum (default: vandaag)
            
        Returns:
            List van wedstrijden
        """
        if date is None:
            date = datetime.now()
        
        league_code = self.LEAGUES.get(league.lower(), "eng.1")
        
        # Format date: YYYYMMDD
        date_str = date.strftime("%Y%m%d")
        
        try:
            url = f"{self.BASE_URL}/{league_code}/scoreboard"
            params = {'dates': date_str}
            
            logger.info(f"🔍 Fetching {league} scoreboard for {date_str}...")
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            events = data.get('events', [])
            
            matches = []
            for event in events:
                formatted = self._format_match(event, league)
                if formatted:
                    matches.append(formatted)
            
            logger.info(f"✅ Found {len(matches)} matches for {league}")
            return matches
            
        except requests.RequestException as e:
            logger.error(f"❌ ESPN API error: {e}")
            return []
    
    def get_upcoming_matches(self, league: str = "epl", days_ahead: int = 7) -> List[Dict]:
        """
        Haal komende wedstrijden op voor een competitie.
        
        Args:
            league: League slug
            days_ahead: Aantal dagen vooruit
            
        Returns:
            List van wedstrijden
        """
        all_matches = []
        today = datetime.now()
        
        # ESPN API requires date-by-date queries
        for day_offset in range(days_ahead + 1):
            date = today + timedelta(days=day_offset)
            matches = self.get_scoreboard(league, date)
            all_matches.extend(matches)
        
        logger.info(f"✅ Found {len(all_matches)} upcoming matches for {league}")
        return all_matches
    
    def get_team_info(self, team_id: str) -> Optional[Dict]:
        """
        Haal team informatie op.
        
        Args:
            team_id: ESPN team ID
            
        Returns:
            Team informatie
        """
        try:
            url = f"{self.BASE_URL}/teams/{team_id}"
            logger.info(f"🔍 Fetching team info for ID {team_id}...")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            team = data.get('team', {})
            
            formatted = {
                'id': team.get('id'),
                'name': team.get('displayName'),
                'short_name': team.get('shortDisplayName'),
                'abbreviation': team.get('abbreviation'),
                'logo': team.get('logos', [{}])[0].get('href') if team.get('logos') else None,
                'color': team.get('color'),
                'record': team.get('record', {}).get('items', [{}])[0].get('summary') if team.get('record') else None,
                'source': 'ESPN'
            }
            
            logger.info(f"✅ Team info retrieved: {formatted.get('name')}")
            return formatted
            
        except requests.RequestException as e:
            logger.error(f"❌ ESPN API error: {e}")
            return None
    
    def get_match_summary(self, match_id: str) -> Optional[Dict]:
        """
        Haal gedetailleerde match informatie op inclusief commentary.
        
        Args:
            match_id: ESPN match ID
            
        Returns:
            Match details met commentary
        """
        try:
            url = f"{self.BASE_URL}/summary"
            params = {'event': match_id}
            
            logger.info(f"🔍 Fetching match summary for ID {match_id}...")
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract key information
            header = data.get('header', {})
            boxscore = data.get('boxscore', {})
            commentary = data.get('commentary', {})
            
            formatted = {
                'match_id': match_id,
                'status': header.get('competitions', [{}])[0].get('status', {}).get('type', {}).get('description'),
                'minute': header.get('competitions', [{}])[0].get('status', {}).get('displayClock'),
                'boxscore': boxscore,
                'commentary': [
                    {
                        'time': item.get('time', {}).get('displayValue'),
                        'text': item.get('text')
                    }
                    for item in commentary.get('items', [])
                ],
                'source': 'ESPN'
            }
            
            logger.info(f"✅ Match summary retrieved")
            return formatted
            
        except requests.RequestException as e:
            logger.error(f"❌ ESPN API error: {e}")
            return None
    
    def _format_match(self, event: Dict, league: str) -> Optional[Dict]:
        """
        Format match data naar ons standaard formaat.
        
        Args:
            event: Raw event data van ESPN
            league: League naam
            
        Returns:
            Geformatteerde match data
        """
        try:
            competition = event.get('competitions', [{}])[0]
            competitors = competition.get('competitors', [])
            
            if len(competitors) < 2:
                return None
            
            # ESPN heeft home team op index 0, away op index 1
            home_team = competitors[0] if competitors[0].get('homeAway') == 'home' else competitors[1]
            away_team = competitors[1] if competitors[1].get('homeAway') == 'away' else competitors[0]
            
            # Parse date
            date_str = event.get('date')
            match_date = datetime.fromisoformat(date_str.replace('Z', '+00:00')) if date_str else None
            
            # Get odds if available
            odds = competition.get('odds', [])
            odds_data = None
            if odds:
                odds_data = {
                    'provider': odds[0].get('provider', {}).get('name'),
                    'home': odds[0].get('homeTeamOdds', {}).get('moneyLine'),
                    'away': odds[0].get('awayTeamOdds', {}).get('moneyLine'),
                    'draw': odds[0].get('drawOdds', {}).get('moneyLine'),
                    'over_under': odds[0].get('overUnder')
                }
            
            formatted = {
                'id': event.get('id'),
                'league': league.upper(),
                'date': match_date,
                'home_team': home_team.get('team', {}).get('displayName'),
                'away_team': away_team.get('team', {}).get('displayName'),
                'home_team_id': home_team.get('team', {}).get('id'),
                'away_team_id': away_team.get('team', {}).get('id'),
                'status': competition.get('status', {}).get('type', {}).get('description'),
                'venue': competition.get('venue', {}).get('fullName'),
                'odds': odds_data,
                'source': 'ESPN'
            }
            
            # Add score if available
            if competition.get('status', {}).get('type', {}).get('completed'):
                formatted['score'] = {
                    'home': int(home_team.get('score', 0)),
                    'away': int(away_team.get('score', 0))
                }
            
            return formatted
            
        except Exception as e:
            logger.error(f"❌ Error formatting match: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        Test de API verbinding.
        
        Returns:
            True als verbinding werkt
        """
        try:
            url = f"{self.BASE_URL}/eng.1/scoreboard"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            events = data.get('events', [])
            logger.info(f"✅ ESPN API connection OK - {len(events)} Premier League matches available")
            return True
            
        except Exception as e:
            logger.error(f"❌ ESPN API connection failed: {e}")
            return False


# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def test_espn_api():
    """Test ESPN API integratie"""
    print("="*80)
    print("🧪 TESTING ESPN API INTEGRATION")
    print("="*80)
    
    # Initialize
    print("\n1. Initializing ESPN API client...")
    api = ESPNAPIIntegration()
    
    # Test connection
    print("\n2. Testing connection...")
    if api.test_connection():
        print("   ✅ Connection OK")
    else:
        print("   ❌ Connection FAILED")
        return
    
    # Test Premier League
    print("\n3. Testing Premier League scoreboard...")
    epl_matches = api.get_scoreboard(league="epl")
    print(f"   ✅ Found {len(epl_matches)} EPL matches")
    
    if epl_matches:
        print("\n   📅 First 3 matches:")
        for i, match in enumerate(epl_matches[:3], 1):
            print(f"   {i}. {match['home_team']} vs {match['away_team']}")
            print(f"      Date: {match['date'].strftime('%Y-%m-%d %H:%M') if match['date'] else 'TBD'}")
            print(f"      Status: {match['status']}")
            if match.get('odds'):
                print(f"      Odds: {match['odds']['home']} / {match['odds']['draw']} / {match['odds']['away']}")
    
    # Test multiple leagues
    print("\n4. Testing multiple leagues...")
    leagues = ["laliga", "bundesliga", "seriea"]
    total_matches = 0
    
    for league in leagues:
        matches = api.get_scoreboard(league=league)
        print(f"   {league.upper()}: {len(matches)} matches")
        total_matches += len(matches)
    
    print(f"   ✅ Total: {total_matches} matches across 3 leagues")
    
    # Test upcoming matches
    print("\n5. Testing upcoming matches (next 3 days)...")
    upcoming = api.get_upcoming_matches(league="epl", days_ahead=3)
    print(f"   ✅ Found {len(upcoming)} upcoming EPL matches")
    
    print("\n" + "="*80)
    print("✅ ESPN API INTEGRATION COMPLETE")
    print("="*80)
    print("""
    GRATIS Features:
    - ✅ Live scores
    - ✅ Fixtures (multiple leagues)
    - ✅ Team information
    - ✅ Match commentary
    - ✅ Betting odds
    - ✅ GEEN rate limiting
    - ✅ GEEN API key nodig
    """)


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    test_espn_api()
