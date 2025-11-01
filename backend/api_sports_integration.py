"""
🎯 API-SPORTS.IO INTEGRATION
Real-time football data with your API key

API Key: eec52f29ffbc24effa9bc0e7963a8cd9
Base URL: https://v3.football.api-sports.io/

Author: Sport AI Sync
Date: November 2025
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os


class ApiSportsIntegration:
    """
    Integration met API-Sports.io (api-football)
    100 gratis calls per dag
    """
    
    def __init__(self, api_key=None):
        self.api_key = api_key or "eec52f29ffbc24effa9bc0e7963a8cd9"
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }
        self.requests_today = 0
        self.max_requests = 100  # Free tier limit
    
    def _make_request(self, endpoint, params=None):
        """
        Make API request with rate limiting
        
        Args:
            endpoint: API endpoint (e.g., '/fixtures')
            params: Query parameters
        
        Returns:
            JSON response or None
        """
        if self.requests_today >= self.max_requests:
            print(f"⚠️ Daily limit reached ({self.max_requests} requests)")
            return None
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            self.requests_today += 1
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API call successful ({self.requests_today}/{self.max_requests})")
                return data
            elif response.status_code == 429:
                print("⚠️ Rate limit exceeded - wait 1 minute")
                return None
            else:
                print(f"❌ API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def get_fixtures_by_date(self, date=None, league_id=None):
        """
        Get fixtures for specific date
        
        Args:
            date: Date string (YYYY-MM-DD) or None for today
            league_id: Optional league filter (78=Bundesliga, 39=Premier League, etc.)
        
        Returns:
            DataFrame with matches
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        params = {'date': date}
        if league_id:
            params['league'] = league_id
        
        print(f"\n📡 Fetching fixtures for {date}...")
        data = self._make_request('/fixtures', params)
        
        if not data or 'response' not in data:
            return pd.DataFrame()
        
        matches = []
        for fixture in data['response']:
            # Extract match info
            match_data = {
                'fixture_id': fixture['fixture']['id'],
                'match_date': fixture['fixture']['date'][:10],
                'match_time': fixture['fixture']['date'][11:16],
                'home': fixture['teams']['home']['name'],
                'away': fixture['teams']['away']['name'],
                'tournament': fixture['league']['name'],
                'country': fixture['league']['country'],
                'home_logo': fixture['teams']['home']['logo'],
                'away_logo': fixture['teams']['away']['logo'],
                'venue': fixture['fixture']['venue']['name'],
                'status': fixture['fixture']['status']['short']
            }
            
            # Add odds if available
            if 'odds' in fixture and fixture['odds']:
                try:
                    bookmaker = fixture['odds'][0]
                    bet = bookmaker['bets'][0]
                    values = bet['values']
                    match_data['odds_home'] = float(values[0]['odd'])
                    match_data['odds_draw'] = float(values[1]['odd'])
                    match_data['odds_away'] = float(values[2]['odd'])
                except:
                    pass
            
            matches.append(match_data)
        
        df = pd.DataFrame(matches)
        print(f"✅ Found {len(df)} matches")
        return df
    
    def get_head_to_head(self, team1_id, team2_id, last_n=5):
        """Get head-to-head history"""
        params = {
            'h2h': f"{team1_id}-{team2_id}",
            'last': last_n
        }
        
        data = self._make_request('/fixtures/headtohead', params)
        if not data or 'response' not in data:
            return []
        
        return data['response']
    
    def get_team_statistics(self, team_id, season=2024, league_id=78):
        """
        Get team statistics for season
        
        Args:
            team_id: Team ID
            season: Season year (2024)
            league_id: League ID (78=Bundesliga)
        
        Returns:
            Dict with statistics
        """
        params = {
            'team': team_id,
            'season': season,
            'league': league_id
        }
        
        data = self._make_request('/teams/statistics', params)
        if not data or 'response' not in data:
            return {}
        
        stats = data['response']
        return {
            'form': stats.get('form', 'N/A'),
            'goals_for_avg': stats['goals']['for']['average']['total'],
            'goals_against_avg': stats['goals']['against']['average']['total'],
            'total_matches': stats['fixtures']['played']['total'],
            'wins': stats['fixtures']['wins']['total'],
            'draws': stats['fixtures']['draws']['total'],
            'losses': stats['fixtures']['losses']['total']
        }
    
    def get_league_fixtures(self, league_id, season=2024, date_from=None, date_to=None):
        """
        Get all fixtures for a league
        
        League IDs:
        - 78: Bundesliga (Germany)
        - 39: Premier League (England)
        - 140: La Liga (Spain)
        - 135: Serie A (Italy)
        - 88: Eredivisie (Netherlands)
        - 61: Ligue 1 (France)
        """
        params = {
            'league': league_id,
            'season': season
        }
        
        if date_from:
            params['from'] = date_from
        if date_to:
            params['to'] = date_to
        
        print(f"\n📡 Fetching league {league_id} fixtures...")
        data = self._make_request('/fixtures', params)
        
        if not data or 'response' not in data:
            return pd.DataFrame()
        
        matches = []
        for fixture in data['response']:
            match_data = {
                'fixture_id': fixture['fixture']['id'],
                'match_date': fixture['fixture']['date'][:10],
                'match_time': fixture['fixture']['date'][11:16],
                'home': fixture['teams']['home']['name'],
                'home_id': fixture['teams']['home']['id'],
                'away': fixture['teams']['away']['name'],
                'away_id': fixture['teams']['away']['id'],
                'tournament': fixture['league']['name'],
                'status': fixture['fixture']['status']['short'],
                'venue': fixture['fixture']['venue']['name']
            }
            matches.append(match_data)
        
        df = pd.DataFrame(matches)
        print(f"✅ Found {len(df)} matches")
        return df
    
    def get_odds_for_fixture(self, fixture_id):
        """Get odds for specific fixture"""
        params = {'fixture': fixture_id}
        
        data = self._make_request('/odds', params)
        if not data or 'response' not in data:
            return None
        
        if len(data['response']) == 0:
            return None
        
        # Get first bookmaker's odds
        try:
            bookmaker = data['response'][0]['bookmakers'][0]
            bet = bookmaker['bets'][0]
            values = bet['values']
            
            return {
                'home': float(values[0]['odd']),
                'draw': float(values[1]['odd']),
                'away': float(values[2]['odd']),
                'bookmaker': bookmaker['name']
            }
        except:
            return None


# =============================================
# QUICK TEST FUNCTIONS
# =============================================

def test_api_connection():
    """Test if API key works"""
    api = ApiSportsIntegration()
    
    print("="*80)
    print("🧪 TESTING API-SPORTS.IO CONNECTION")
    print("="*80)
    
    # Test fixtures for today
    df = api.get_fixtures_by_date()
    
    if not df.empty:
        print(f"\n✅ SUCCESS! API key works!")
        print(f"\n📊 Sample matches for today:")
        print(df[['home', 'away', 'tournament', 'match_time']].head(5).to_string(index=False))
        return True
    else:
        print("\n❌ No fixtures found or API error")
        return False


def get_bundesliga_today():
    """Get Bundesliga matches for today"""
    api = ApiSportsIntegration()
    
    print("="*80)
    print("⚽ BUNDESLIGA MATCHES TODAY")
    print("="*80)
    
    df = api.get_league_fixtures(
        league_id=78,  # Bundesliga
        season=2024,
        date_from=datetime.now().strftime('%Y-%m-%d'),
        date_to=datetime.now().strftime('%Y-%m-%d')
    )
    
    if not df.empty:
        print(f"\n✅ Found {len(df)} Bundesliga matches")
        print(df[['match_time', 'home', 'away', 'status']].to_string(index=False))
    else:
        print("\n⚠️ No Bundesliga matches today")
    
    return df


if __name__ == "__main__":
    # Test connection
    test_api_connection()
    
    # Get Bundesliga
    print("\n")
    get_bundesliga_today()
