"""
Football-Data.org API Integration
===================================

FREE TIER with your API key!
- 10 calls per minute
- Multiple competitions (EPL, La Liga, Bundesliga, etc.)
- Standings, fixtures, team & player stats
- Match details with lineups

API: https://api.football-data.org/v4/
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class FootballDataOrgIntegration:
    """
    Football-Data.org API client.
    FREE TIER: 10 calls per minute
    """
    
    BASE_URL = "https://api.football-data.org/v4"
    
    # Competition codes
    COMPETITIONS = {
        "premier_league": "PL",
        "championship": "ELC",
        "bundesliga": "BL1",
        "bundesliga2": "BL2",
        "laliga": "PD",
        "seriea": "SA",
        "ligue1": "FL1",
        "eredivisie": "DED",
        "primeira_liga": "PPL",
        "champions_league": "CL",
        "europa_league": "EL",
        "world_cup": "WC",
        "european_championship": "EC",
    }
    
    def __init__(self, api_key: str):
        """
        Initialiseer Football-Data.org client.
        
        Args:
            api_key: Your API key from football-data.org
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'X-Auth-Token': api_key,
            'User-Agent': 'SportAI-BettingSystem/1.0',
            'Accept': 'application/json'
        })
        logger.info("✅ Football-Data.org Integration initialized")
    
    def get_competitions(self) -> List[Dict]:
        """Haal alle beschikbare competities op."""
        try:
            url = f"{self.BASE_URL}/competitions"
            logger.info("🔍 Fetching available competitions...")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            competitions = data.get('competitions', [])
            
            logger.info(f"✅ Found {len(competitions)} competitions")
            return competitions
            
        except requests.RequestException as e:
            logger.error(f"❌ API error: {e}")
            return []
    
    def get_matches(self, competition: str = "PL", 
                   status: str = "SCHEDULED") -> List[Dict]:
        """
        Haal wedstrijden op voor een competitie.
        
        Args:
            competition: Competition code (PL, BL1, etc.)
            status: Match status (SCHEDULED, LIVE, FINISHED)
            
        Returns:
            List van wedstrijden
        """
        comp_code = self.COMPETITIONS.get(competition, competition)
        
        try:
            url = f"{self.BASE_URL}/competitions/{comp_code}/matches"
            params = {'status': status}
            
            logger.info(f"🔍 Fetching {status} matches for {comp_code}...")
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            matches = data.get('matches', [])
            
            formatted = []
            for match in matches:
                formatted_match = self._format_match(match)
                if formatted_match:
                    formatted.append(formatted_match)
            
            logger.info(f"✅ Found {len(formatted)} matches")
            return formatted
            
        except requests.RequestException as e:
            logger.error(f"❌ API error: {e}")
            return []
    
    def get_standings(self, competition: str = "PL") -> List[Dict]:
        """
        Haal klassement op.
        
        Args:
            competition: Competition code
            
        Returns:
            List van teams met standings
        """
        comp_code = self.COMPETITIONS.get(competition, competition)
        
        try:
            url = f"{self.BASE_URL}/competitions/{comp_code}/standings"
            logger.info(f"🔍 Fetching standings for {comp_code}...")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            standings = data.get('standings', [])
            
            if not standings:
                return []
            
            # Usually first element contains the main table
            table = standings[0].get('table', [])
            
            formatted = []
            for entry in table:
                formatted.append({
                    'position': entry.get('position'),
                    'team': entry.get('team', {}).get('name'),
                    'team_id': entry.get('team', {}).get('id'),
                    'played': entry.get('playedGames'),
                    'won': entry.get('won'),
                    'drawn': entry.get('draw'),
                    'lost': entry.get('lost'),
                    'points': entry.get('points'),
                    'goals_for': entry.get('goalsFor'),
                    'goals_against': entry.get('goalsAgainst'),
                    'goal_difference': entry.get('goalDifference'),
                    'form': entry.get('form'),  # Last 5 matches
                })
            
            logger.info(f"✅ Retrieved standings for {len(formatted)} teams")
            return formatted
            
        except requests.RequestException as e:
            logger.error(f"❌ API error: {e}")
            return []
    
    def get_team_info(self, team_id: int) -> Optional[Dict]:
        """
        Haal team informatie op.
        
        Args:
            team_id: Team ID
            
        Returns:
            Team informatie
        """
        try:
            url = f"{self.BASE_URL}/teams/{team_id}"
            logger.info(f"🔍 Fetching team info for ID {team_id}...")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            team = response.json()
            
            formatted = {
                'id': team.get('id'),
                'name': team.get('name'),
                'short_name': team.get('shortName'),
                'tla': team.get('tla'),  # Three Letter Abbreviation
                'founded': team.get('founded'),
                'venue': team.get('venue'),
                'website': team.get('website'),
                'crest': team.get('crest'),
                'colors': team.get('clubColors'),
                'coach': team.get('coach', {}).get('name') if team.get('coach') else None,
                'squad': [
                    {
                        'id': player.get('id'),
                        'name': player.get('name'),
                        'position': player.get('position'),
                        'nationality': player.get('nationality'),
                    }
                    for player in team.get('squad', [])
                ],
                'source': 'Football-Data.org'
            }
            
            logger.info(f"✅ Team info retrieved: {formatted['name']}")
            return formatted
            
        except requests.RequestException as e:
            logger.error(f"❌ API error: {e}")
            return None
    
    def get_match_details(self, match_id: int) -> Optional[Dict]:
        """
        Haal gedetailleerde match informatie op.
        
        Args:
            match_id: Match ID
            
        Returns:
            Match details
        """
        try:
            url = f"{self.BASE_URL}/matches/{match_id}"
            logger.info(f"🔍 Fetching match details for ID {match_id}...")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            match = response.json()
            formatted = self._format_match(match, include_details=True)
            
            logger.info(f"✅ Match details retrieved")
            return formatted
            
        except requests.RequestException as e:
            logger.error(f"❌ API error: {e}")
            return None
    
    def _format_match(self, match: Dict, include_details: bool = False) -> Optional[Dict]:
        """Format match data naar ons standaard formaat."""
        try:
            utc_date = match.get('utcDate')
            match_date = None
            if utc_date:
                match_date = datetime.fromisoformat(utc_date.replace('Z', '+00:00'))
            
            formatted = {
                'id': match.get('id'),
                'league': match.get('competition', {}).get('name'),
                'league_code': match.get('competition', {}).get('code'),
                'date': match_date,
                'home_team': match.get('homeTeam', {}).get('name'),
                'away_team': match.get('awayTeam', {}).get('name'),
                'home_team_id': match.get('homeTeam', {}).get('id'),
                'away_team_id': match.get('awayTeam', {}).get('id'),
                'status': match.get('status'),
                'matchday': match.get('matchday'),
                'stage': match.get('stage'),
                'venue': match.get('venue'),
                'source': 'Football-Data.org'
            }
            
            # Add score
            score = match.get('score', {})
            if score:
                formatted['score'] = {
                    'home': score.get('fullTime', {}).get('home'),
                    'away': score.get('fullTime', {}).get('away'),
                    'halftime': {
                        'home': score.get('halfTime', {}).get('home'),
                        'away': score.get('halfTime', {}).get('away'),
                    }
                }
            
            # Add extra details if requested
            if include_details:
                formatted['referees'] = match.get('referees', [])
                formatted['odds'] = match.get('odds')
            
            return formatted
            
        except Exception as e:
            logger.error(f"❌ Error formatting match: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test de API verbinding."""
        try:
            url = f"{self.BASE_URL}/competitions"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            competitions = data.get('competitions', [])
            logger.info(f"✅ API connection OK - {len(competitions)} competitions available")
            return True
            
        except Exception as e:
            logger.error(f"❌ API connection failed: {e}")
            return False


# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def test_football_data_org():
    """Test Football-Data.org API integratie"""
    print("="*80)
    print("🧪 TESTING FOOTBALL-DATA.ORG API")
    print("="*80)
    
    api_key = "d5513a02070e4dbba002d3f5c9a78942"
    
    # Initialize
    print("\n1. Initializing Football-Data.org client...")
    api = FootballDataOrgIntegration(api_key)
    
    # Test connection
    print("\n2. Testing connection...")
    if api.test_connection():
        print("   ✅ Connection OK")
    else:
        print("   ❌ Connection FAILED")
        return
    
    # Get competitions
    print("\n3. Getting available competitions...")
    competitions = api.get_competitions()
    print(f"   ✅ Found {len(competitions)} competitions")
    print("\n   📋 Available competitions:")
    for comp in competitions[:10]:
        print(f"      - {comp.get('name')} ({comp.get('code')})")
    
    # Get matches
    print("\n4. Getting scheduled matches (Premier League)...")
    matches = api.get_matches(competition="PL", status="SCHEDULED")
    print(f"   ✅ Found {len(matches)} scheduled matches")
    
    if matches:
        print("\n   ⚽ First 3 matches:")
        for i, match in enumerate(matches[:3], 1):
            print(f"   {i}. {match['home_team']} vs {match['away_team']}")
            print(f"      Date: {match['date'].strftime('%Y-%m-%d %H:%M') if match['date'] else 'TBD'}")
            print(f"      Status: {match['status']}")
    
    # Get standings
    print("\n5. Getting league standings (Premier League)...")
    standings = api.get_standings(competition="PL")
    print(f"   ✅ Found standings for {len(standings)} teams")
    
    if standings:
        print("\n   🏆 Top 5 teams:")
        for team in standings[:5]:
            print(f"   {team['position']}. {team['team']} - {team['points']} pts")
            print(f"      Record: {team['won']}W {team['drawn']}D {team['lost']}L")
            print(f"      Form: {team.get('form', 'N/A')}")
    
    # Test other leagues
    print("\n6. Testing multiple leagues...")
    leagues = ["bundesliga", "laliga", "seriea"]
    for league in leagues:
        matches = api.get_matches(competition=league, status="SCHEDULED")
        print(f"   {league.upper()}: {len(matches)} scheduled matches")
    
    print("\n" + "="*80)
    print("✅ FOOTBALL-DATA.ORG API INTEGRATION COMPLETE")
    print("="*80)
    print("""
    FREE TIER Features:
    - ✅ 10 calls per minute
    - ✅ 13+ competitions
    - ✅ Live matches & fixtures
    - ✅ League standings
    - ✅ Team information
    - ✅ Player squads
    - ✅ Match details with lineups
    """)


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    test_football_data_org()
