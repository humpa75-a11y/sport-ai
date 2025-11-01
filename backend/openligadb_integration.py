"""
OpenLigaDB API Integration
===========================

VOLLEDIG GRATIS - Geen API key nodig!
- Bundesliga 1 & 2
- Live scores + fixtures
- Geen rate limiting
- Direct werkend

API Documentatie: https://api.openligadb.de/
"""

import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class OpenLigaDBIntegration:
    """
    OpenLigaDB API client voor Duitse voetbalcompetities.
    VOLLEDIG GRATIS - geen API key nodig!
    """
    
    BASE_URL = "https://api.openligadb.de"
    
    # League codes
    LEAGUES = {
        "bundesliga": "bl1",      # Bundesliga 1
        "bundesliga2": "bl2",     # Bundesliga 2
    }
    
    def __init__(self):
        """Initialiseer OpenLigaDB client (geen credentials nodig!)"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SportAI-BettingSystem/1.0',
            'Accept': 'application/json'
        })
        logger.info("✅ OpenLigaDB Integration initialized (FREE - no key needed!)")
    
    def get_current_season(self) -> str:
        """Get current season year"""
        now = datetime.now()
        # Season starts in August
        if now.month >= 8:
            return str(now.year)
        else:
            return str(now.year - 1)
    
    def get_fixtures_by_date(self, league: str = "bundesliga", 
                            date: Optional[datetime] = None) -> List[Dict]:
        """
        Haal wedstrijden op voor een specifieke datum.
        
        Args:
            league: "bundesliga" of "bundesliga2"
            date: Datum (default: vandaag)
            
        Returns:
            List van wedstrijden
        """
        if date is None:
            date = datetime.now()
        
        league_code = self.LEAGUES.get(league.lower(), "bl1")
        season = self.get_current_season()
        
        # Format date: YYYY-MM-DD
        date_str = date.strftime("%Y-%m-%d")
        
        try:
            url = f"{self.BASE_URL}/getmatchdata/{league_code}/{season}"
            logger.info(f"🔍 Fetching {league} fixtures for {date_str}...")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            all_matches = response.json()
            
            # Filter matches voor de gevraagde datum
            target_date = date.date()
            filtered_matches = []
            
            for match in all_matches:
                match_date_str = match.get('matchDateTime', '')
                if match_date_str:
                    try:
                        match_date = datetime.fromisoformat(match_date_str.replace('Z', '+00:00'))
                        if match_date.date() == target_date:
                            formatted = self._format_match(match)
                            if formatted:  # Only add if formatting succeeded
                                filtered_matches.append(formatted)
                    except Exception as e:
                        logger.debug(f"Date parsing error: {e}")
                        continue
            
            logger.info(f"✅ Found {len(filtered_matches)} matches for {date_str}")
            return filtered_matches
            
        except requests.RequestException as e:
            logger.error(f"❌ OpenLigaDB API error: {e}")
            return []
    
    def get_upcoming_fixtures(self, league: str = "bundesliga", 
                             days_ahead: int = 7) -> List[Dict]:
        """
        Haal komende wedstrijden op.
        
        Args:
            league: "bundesliga" of "bundesliga2"
            days_ahead: Aantal dagen vooruit
            
        Returns:
            List van wedstrijden
        """
        league_code = self.LEAGUES.get(league.lower(), "bl1")
        season = self.get_current_season()
        
        try:
            url = f"{self.BASE_URL}/getmatchdata/{league_code}/{season}"
            logger.info(f"🔍 Fetching upcoming {league} fixtures (next {days_ahead} days)...")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            all_matches = response.json()
            
            # Filter voor komende wedstrijden
            now = datetime.now()
            end_date = now + timedelta(days=days_ahead)
            
            upcoming_matches = []
            
            for match in all_matches:
                match_date_str = match.get('matchDateTime', '')
                if match_date_str:
                    try:
                        match_date = datetime.fromisoformat(match_date_str.replace('Z', '+00:00'))
                        if now <= match_date <= end_date:
                            formatted = self._format_match(match)
                            if formatted:  # Only add if formatting succeeded
                                upcoming_matches.append(formatted)
                    except Exception as e:
                        logger.debug(f"Date parsing error: {e}")
                        continue
            
            # Sorteer op datum
            if upcoming_matches:
                upcoming_matches.sort(key=lambda x: x['date'])
            
            logger.info(f"✅ Found {len(upcoming_matches)} upcoming matches")
            return upcoming_matches
            
        except requests.RequestException as e:
            logger.error(f"❌ OpenLigaDB API error: {e}")
            return []
    
    def get_live_matches(self, league: str = "bundesliga") -> List[Dict]:
        """
        Haal live wedstrijden op.
        
        Args:
            league: "bundesliga" of "bundesliga2"
            
        Returns:
            List van live wedstrijden
        """
        league_code = self.LEAGUES.get(league.lower(), "bl1")
        
        try:
            url = f"{self.BASE_URL}/getmatchdata/{league_code}"
            logger.info(f"🔴 Fetching LIVE {league} matches...")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            matches = response.json()
            
            # Filter voor live matches (matchIsFinished=False en heeft goals)
            live_matches = []
            
            for match in matches:
                if not match.get('matchIsFinished', True):
                    formatted = self._format_match(match)
                    if formatted:
                        live_matches.append(formatted)
            
            logger.info(f"✅ Found {len(live_matches)} LIVE matches")
            return live_matches
            
        except requests.RequestException as e:
            logger.error(f"❌ OpenLigaDB API error: {e}")
            return []
    
    def get_team_statistics(self, team_name: str, league: str = "bundesliga") -> Optional[Dict]:
        """
        Haal team statistieken op (via seizoen data analyse).
        
        Args:
            team_name: Naam van het team
            league: "bundesliga" of "bundesliga2"
            
        Returns:
            Team statistieken
        """
        league_code = self.LEAGUES.get(league.lower(), "bl1")
        season = self.get_current_season()
        
        try:
            url = f"{self.BASE_URL}/getmatchdata/{league_code}/{season}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            all_matches = response.json()
            
            # Analyseer team performance
            stats = {
                'team_name': team_name,
                'matches_played': 0,
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'goals_scored': 0,
                'goals_conceded': 0,
                'recent_form': []
            }
            
            for match in all_matches:
                if not match.get('matchIsFinished', False):
                    continue
                
                team1 = match.get('team1', {}).get('teamName', '')
                team2 = match.get('team2', {}).get('teamName', '')
                
                if team_name.lower() not in team1.lower() and team_name.lower() not in team2.lower():
                    continue
                
                # Extract score
                results = match.get('matchResults', [])
                if not results:
                    continue
                
                final_result = next((r for r in results if r.get('resultName') == 'Endergebnis'), None)
                if not final_result:
                    continue
                
                goals1 = final_result.get('pointsTeam1', 0)
                goals2 = final_result.get('pointsTeam2', 0)
                
                is_home = team_name.lower() in team1.lower()
                
                if is_home:
                    stats['goals_scored'] += goals1
                    stats['goals_conceded'] += goals2
                    
                    if goals1 > goals2:
                        stats['wins'] += 1
                        stats['recent_form'].append('W')
                    elif goals1 == goals2:
                        stats['draws'] += 1
                        stats['recent_form'].append('D')
                    else:
                        stats['losses'] += 1
                        stats['recent_form'].append('L')
                else:
                    stats['goals_scored'] += goals2
                    stats['goals_conceded'] += goals1
                    
                    if goals2 > goals1:
                        stats['wins'] += 1
                        stats['recent_form'].append('W')
                    elif goals2 == goals1:
                        stats['draws'] += 1
                        stats['recent_form'].append('D')
                    else:
                        stats['losses'] += 1
                        stats['recent_form'].append('L')
                
                stats['matches_played'] += 1
            
            # Keep only last 5 matches for form
            stats['recent_form'] = stats['recent_form'][-5:]
            
            if stats['matches_played'] > 0:
                logger.info(f"✅ Team stats for {team_name}: {stats['matches_played']} matches")
                return stats
            else:
                logger.warning(f"⚠️  No matches found for team: {team_name}")
                return None
            
        except requests.RequestException as e:
            logger.error(f"❌ OpenLigaDB API error: {e}")
            return None
    
    def _format_match(self, match: Dict) -> Optional[Dict]:
        """
        Format match data naar ons standaard formaat.
        
        Args:
            match: Raw match data van OpenLigaDB
            
        Returns:
            Geformatteerde match data
        """
        try:
            match_date_str = match.get('matchDateTime', '')
            if not match_date_str:
                return None
                
            match_date = datetime.fromisoformat(match_date_str.replace('Z', '+00:00'))
            
            team1 = match.get('team1')
            team2 = match.get('team2')
            
            if not team1 or not team2:
                return None
            
            # Get venue safely
            location = match.get('location')
            venue = 'Unknown'
            if location and isinstance(location, dict):
                venue = location.get('locationStadium', 'Unknown')
            
            formatted = {
                'id': match.get('matchID'),
                'league': 'Bundesliga',
                'date': match_date,
                'home_team': team1.get('teamName', 'Unknown'),
                'away_team': team2.get('teamName', 'Unknown'),
                'home_team_id': team1.get('teamId'),
                'away_team_id': team2.get('teamId'),
                'status': 'finished' if match.get('matchIsFinished') else 'scheduled',
                'venue': venue,
                'source': 'OpenLigaDB'
            }
            
            # Add score if available
            results = match.get('matchResults', [])
            if results:
                final_result = next((r for r in results if r.get('resultName') == 'Endergebnis'), results[0])
                formatted['score'] = {
                    'home': final_result.get('pointsTeam1', 0),
                    'away': final_result.get('pointsTeam2', 0)
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
            url = f"{self.BASE_URL}/getmatchdata/bl1"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            matches = response.json()
            logger.info(f"✅ OpenLigaDB connection OK - {len(matches)} matches available")
            return True
            
        except Exception as e:
            logger.error(f"❌ OpenLigaDB connection failed: {e}")
            return False


# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def test_openligadb():
    """Test OpenLigaDB integratie"""
    print("="*80)
    print("🧪 TESTING OPENLIGADB INTEGRATION")
    print("="*80)
    
    # Initialize
    print("\n1. Initializing OpenLigaDB client...")
    api = OpenLigaDBIntegration()
    
    # Test connection
    print("\n2. Testing connection...")
    if api.test_connection():
        print("   ✅ Connection OK")
    else:
        print("   ❌ Connection FAILED")
        return
    
    # Test upcoming fixtures
    print("\n3. Testing upcoming fixtures (next 7 days)...")
    fixtures = api.get_upcoming_fixtures(league="bundesliga", days_ahead=7)
    print(f"   ✅ Found {len(fixtures)} upcoming matches")
    
    if fixtures:
        print("\n   📅 First 3 matches:")
        for i, match in enumerate(fixtures[:3], 1):
            print(f"   {i}. {match['home_team']} vs {match['away_team']}")
            print(f"      Date: {match['date'].strftime('%Y-%m-%d %H:%M')}")
            print(f"      Venue: {match['venue']}")
    
    # Test today's fixtures
    print("\n4. Testing today's fixtures...")
    today_fixtures = api.get_fixtures_by_date(league="bundesliga")
    print(f"   ✅ Found {len(today_fixtures)} matches today")
    
    # Test live matches
    print("\n5. Testing live matches...")
    live = api.get_live_matches(league="bundesliga")
    print(f"   ✅ Found {len(live)} LIVE matches")
    
    # Test team statistics
    print("\n6. Testing team statistics...")
    team_stats = api.get_team_statistics("Bayern", league="bundesliga")
    if team_stats:
        print(f"   ✅ Stats for {team_stats['team_name']}:")
        print(f"      Matches: {team_stats['matches_played']}")
        print(f"      Record: {team_stats['wins']}W-{team_stats['draws']}D-{team_stats['losses']}L")
        print(f"      Goals: {team_stats['goals_scored']} scored, {team_stats['goals_conceded']} conceded")
        print(f"      Form: {'-'.join(team_stats['recent_form'][-5:])}")
    
    print("\n" + "="*80)
    print("✅ OPENLIGADB INTEGRATION COMPLETE")
    print("="*80)
    print("""
    GRATIS Features:
    - ✅ Live scores
    - ✅ Fixtures (upcoming + by date)
    - ✅ Team statistics
    - ✅ Bundesliga 1 & 2
    - ✅ GEEN rate limiting
    - ✅ GEEN API key nodig
    """)


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    test_openligadb()
