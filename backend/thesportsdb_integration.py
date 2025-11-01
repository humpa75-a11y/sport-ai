"""
TheSportsDB API Integration
============================

VOLLEDIG GRATIS - Geen API key nodig!
- 500+ football leagues
- Team information & statistics
- Player data
- Live scores
- Historical results

API URL: https://www.thesportsdb.com/api/v1/json/3/
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TheSportsDBIntegration:
    """
    TheSportsDB API client voor voetbaldata wereldwijd.
    VOLLEDIG GRATIS - geen API key nodig!
    """
    
    BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"
    
    # League IDs (TheSportsDB uses numeric IDs)
    LEAGUES = {
        "epl": "4328",           # Premier League
        "laliga": "4335",        # La Liga
        "bundesliga": "4331",    # Bundesliga
        "seriea": "4332",        # Serie A
        "ligue1": "4334",        # Ligue 1
        "eredivisie": "4337",    # Eredivisie
        "champions": "4480",     # Champions League
        "europa": "4481",        # Europa League
    }
    
    def __init__(self):
        """Initialiseer TheSportsDB API client (geen credentials nodig!)"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SportAI-BettingSystem/1.0',
            'Accept': 'application/json'
        })
        logger.info("✅ TheSportsDB API Integration initialized (FREE - no key needed!)")
    
    def get_next_matches(self, league: str = "epl", limit: int = 15) -> List[Dict]:
        """
        Haal komende wedstrijden op voor een competitie.
        
        Args:
            league: League slug
            limit: Maximum aantal matches
            
        Returns:
            List van wedstrijden
        """
        league_id = self.LEAGUES.get(league.lower(), "4328")
        
        try:
            url = f"{self.BASE_URL}/eventsnextleague.php"
            params = {'id': league_id}
            
            logger.info(f"🔍 Fetching next matches for {league}...")
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            events = data.get('events', [])
            
            if not events:
                logger.warning(f"⚠️  No upcoming matches found for {league}")
                return []
            
            matches = []
            for event in events[:limit]:
                formatted = self._format_match(event, league)
                if formatted:
                    matches.append(formatted)
            
            logger.info(f"✅ Found {len(matches)} upcoming matches for {league}")
            return matches
            
        except requests.RequestException as e:
            logger.error(f"❌ TheSportsDB API error: {e}")
            return []
    
    def get_last_matches(self, league: str = "epl", limit: int = 15) -> List[Dict]:
        """
        Haal laatste gespeelde wedstrijden op.
        
        Args:
            league: League slug
            limit: Maximum aantal matches
            
        Returns:
            List van wedstrijden
        """
        league_id = self.LEAGUES.get(league.lower(), "4328")
        
        try:
            url = f"{self.BASE_URL}/eventspastleague.php"
            params = {'id': league_id}
            
            logger.info(f"🔍 Fetching last matches for {league}...")
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            events = data.get('events', [])
            
            matches = []
            for event in events[:limit]:
                formatted = self._format_match(event, league)
                if formatted:
                    matches.append(formatted)
            
            logger.info(f"✅ Found {len(matches)} past matches for {league}")
            return matches
            
        except requests.RequestException as e:
            logger.error(f"❌ TheSportsDB API error: {e}")
            return []
    
    def get_team_info(self, team_name: str) -> Optional[Dict]:
        """
        Zoek team informatie op naam.
        
        Args:
            team_name: Naam van het team
            
        Returns:
            Team informatie
        """
        try:
            url = f"{self.BASE_URL}/searchteams.php"
            params = {'t': team_name}
            
            logger.info(f"🔍 Searching for team: {team_name}...")
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            teams = data.get('teams', [])
            
            if not teams:
                logger.warning(f"⚠️  Team not found: {team_name}")
                return None
            
            team = teams[0]  # Take first match
            
            formatted = {
                'id': team.get('idTeam'),
                'name': team.get('strTeam'),
                'short_name': team.get('strTeamShort'),
                'alternate_name': team.get('strAlternate'),
                'year_formed': team.get('intFormedYear'),
                'stadium': team.get('strStadium'),
                'stadium_capacity': team.get('intStadiumCapacity'),
                'stadium_location': team.get('strStadiumLocation'),
                'website': team.get('strWebsite'),
                'league': team.get('strLeague'),
                'description': team.get('strDescriptionEN'),
                'badge': team.get('strTeamBadge'),
                'jersey': team.get('strTeamJersey'),
                'logo': team.get('strTeamLogo'),
                'country': team.get('strCountry'),
                'source': 'TheSportsDB'
            }
            
            logger.info(f"✅ Team info retrieved: {formatted['name']}")
            return formatted
            
        except requests.RequestException as e:
            logger.error(f"❌ TheSportsDB API error: {e}")
            return None
    
    def get_league_table(self, league: str = "epl", season: str = "2024-2025") -> List[Dict]:
        """
        Haal league standings op.
        
        Args:
            league: League slug
            season: Season (format: "2024-2025")
            
        Returns:
            List van teams met standings
        """
        league_id = self.LEAGUES.get(league.lower(), "4328")
        
        try:
            url = f"{self.BASE_URL}/lookuptable.php"
            params = {
                'l': league_id,
                's': season
            }
            
            logger.info(f"🔍 Fetching league table for {league} ({season})...")
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            table = data.get('table', [])
            
            standings = []
            for entry in table:
                standings.append({
                    'position': entry.get('intRank'),
                    'team': entry.get('strTeam'),
                    'played': entry.get('intPlayed'),
                    'won': entry.get('intWin'),
                    'drawn': entry.get('intDraw'),
                    'lost': entry.get('intLoss'),
                    'goals_for': entry.get('intGoalsFor'),
                    'goals_against': entry.get('intGoalsAgainst'),
                    'goal_difference': entry.get('intGoalDifference'),
                    'points': entry.get('intPoints'),
                    'form': entry.get('strForm'),  # Last 5 matches
                })
            
            logger.info(f"✅ Retrieved standings for {len(standings)} teams")
            return standings
            
        except requests.RequestException as e:
            logger.error(f"❌ TheSportsDB API error: {e}")
            return []
    
    def search_player(self, player_name: str) -> List[Dict]:
        """
        Zoek speler informatie.
        
        Args:
            player_name: Naam van de speler
            
        Returns:
            List van speler informatie
        """
        try:
            url = f"{self.BASE_URL}/searchplayers.php"
            params = {'p': player_name}
            
            logger.info(f"🔍 Searching for player: {player_name}...")
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            players = data.get('player', [])
            
            if not players:
                logger.warning(f"⚠️  Player not found: {player_name}")
                return []
            
            results = []
            for player in players:
                results.append({
                    'id': player.get('idPlayer'),
                    'name': player.get('strPlayer'),
                    'team': player.get('strTeam'),
                    'nationality': player.get('strNationality'),
                    'birth_date': player.get('dateBorn'),
                    'height': player.get('strHeight'),
                    'weight': player.get('strWeight'),
                    'position': player.get('strPosition'),
                    'description': player.get('strDescriptionEN'),
                    'photo': player.get('strThumb'),
                    'wage': player.get('strWage'),
                    'source': 'TheSportsDB'
                })
            
            logger.info(f"✅ Found {len(results)} players")
            return results
            
        except requests.RequestException as e:
            logger.error(f"❌ TheSportsDB API error: {e}")
            return []
    
    def _format_match(self, event: Dict, league: str) -> Optional[Dict]:
        """
        Format match data naar ons standaard formaat.
        
        Args:
            event: Raw event data van TheSportsDB
            league: League naam
            
        Returns:
            Geformatteerde match data
        """
        try:
            # Parse date and time
            date_str = event.get('dateEvent')
            time_str = event.get('strTime')
            
            match_date = None
            if date_str:
                try:
                    # TheSportsDB format: YYYY-MM-DD
                    if time_str:
                        datetime_str = f"{date_str} {time_str}"
                        match_date = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                    else:
                        match_date = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    pass
            
            formatted = {
                'id': event.get('idEvent'),
                'league': league.upper(),
                'date': match_date,
                'home_team': event.get('strHomeTeam'),
                'away_team': event.get('strAwayTeam'),
                'home_team_id': event.get('idHomeTeam'),
                'away_team_id': event.get('idAwayTeam'),
                'round': event.get('intRound'),
                'season': event.get('strSeason'),
                'venue': event.get('strVenue'),
                'status': event.get('strStatus'),
                'source': 'TheSportsDB'
            }
            
            # Add score if match is finished
            home_score = event.get('intHomeScore')
            away_score = event.get('intAwayScore')
            
            if home_score is not None and away_score is not None:
                formatted['score'] = {
                    'home': int(home_score),
                    'away': int(away_score)
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
            url = f"{self.BASE_URL}/eventsnextleague.php"
            params = {'id': '4328'}  # Premier League
            
            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            events = data.get('events', [])
            logger.info(f"✅ TheSportsDB API connection OK - {len(events)} EPL matches available")
            return True
            
        except Exception as e:
            logger.error(f"❌ TheSportsDB API connection failed: {e}")
            return False


# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def test_thesportsdb_api():
    """Test TheSportsDB API integratie"""
    print("="*80)
    print("🧪 TESTING THESPORTSDB API INTEGRATION")
    print("="*80)
    
    # Initialize
    print("\n1. Initializing TheSportsDB API client...")
    api = TheSportsDBIntegration()
    
    # Test connection
    print("\n2. Testing connection...")
    if api.test_connection():
        print("   ✅ Connection OK")
    else:
        print("   ❌ Connection FAILED")
        return
    
    # Test next matches
    print("\n3. Testing next matches (Premier League)...")
    next_matches = api.get_next_matches(league="epl", limit=5)
    print(f"   ✅ Found {len(next_matches)} upcoming matches")
    
    if next_matches:
        print("\n   📅 First 3 matches:")
        for i, match in enumerate(next_matches[:3], 1):
            print(f"   {i}. {match['home_team']} vs {match['away_team']}")
            print(f"      Date: {match['date'].strftime('%Y-%m-%d %H:%M') if match['date'] else 'TBD'}")
            print(f"      Venue: {match.get('venue', 'Unknown')}")
    
    # Test team info
    print("\n4. Testing team information...")
    team_info = api.get_team_info("Manchester United")
    if team_info:
        print(f"   ✅ Team: {team_info['name']}")
        print(f"      Stadium: {team_info['stadium']} ({team_info.get('stadium_capacity', 'N/A')} capacity)")
        print(f"      Founded: {team_info.get('year_formed', 'N/A')}")
    
    # Test league table
    print("\n5. Testing league standings...")
    standings = api.get_league_table(league="epl", season="2024-2025")
    print(f"   ✅ Retrieved standings for {len(standings)} teams")
    
    if standings:
        print("\n   🏆 Top 5 teams:")
        for team in standings[:5]:
            print(f"   {team['position']}. {team['team']} - {team['points']} pts ({team['form']})")
    
    # Test multiple leagues
    print("\n6. Testing multiple leagues...")
    leagues = ["laliga", "bundesliga", "seriea"]
    total_matches = 0
    
    for league in leagues:
        matches = api.get_next_matches(league=league, limit=5)
        print(f"   {league.upper()}: {len(matches)} matches")
        total_matches += len(matches)
    
    print(f"   ✅ Total: {total_matches} matches across 3 leagues")
    
    print("\n" + "="*80)
    print("✅ THESPORTSDB API INTEGRATION COMPLETE")
    print("="*80)
    print("""
    GRATIS Features:
    - ✅ Next/Past matches
    - ✅ Team information
    - ✅ League standings
    - ✅ Player search
    - ✅ 500+ leagues worldwide
    - ✅ Rate limited maar genereus
    - ✅ GEEN API key nodig
    """)


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    test_thesportsdb_api()
