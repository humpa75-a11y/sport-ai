"""
🔥 SOFASCORE API INTEGRATION (RapidAPI)
Real-time scores, xG, lineups, and live stats

API Key: 31cc8f0670msh7870ef60d95c4e1p140715jsnb70514972a34
Provider: RapidAPI (Sofascore)

Author: Sport AI Sync
Date: November 2025
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time


class SofascoreAPI:
    """
    Sofascore API via RapidAPI
    Better for live scores, xG, and detailed stats
    """
    
    def __init__(self, api_key=None):
        self.api_key = api_key or "31cc8f0670msh7870ef60d95c4e1p140715jsnb70514972a34"
        self.base_url = "https://sofascore.p.rapidapi.com"
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'sofascore.p.rapidapi.com'
        }
        self.requests_today = 0
    
    def _make_request(self, endpoint, params=None):
        """Make API request"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            self.requests_today += 1
            
            if response.status_code == 200:
                print(f"✅ Sofascore API call successful ({self.requests_today} requests)")
                return response.json()
            else:
                print(f"❌ Sofascore error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def get_matches_by_date(self, date=None):
        """
        Get all matches for a specific date
        
        Args:
            date: Date string (YYYY-MM-DD) or None for today
        
        Returns:
            List of matches with full details
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Sofascore uses timestamp format
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        
        print(f"\n📡 Fetching Sofascore matches for {date}...")
        
        # Get events for date
        endpoint = f"/events/date/{date}"
        data = self._make_request(endpoint)
        
        if not data or 'events' not in data:
            return []
        
        matches = []
        for event in data['events']:
            try:
                match_info = {
                    'match_id': event['id'],
                    'match_date': date,
                    'match_time': datetime.fromtimestamp(event['startTimestamp']).strftime('%H:%M'),
                    'home': event['homeTeam']['name'],
                    'home_id': event['homeTeam']['id'],
                    'away': event['awayTeam']['name'],
                    'away_id': event['awayTeam']['id'],
                    'tournament': event['tournament']['name'],
                    'country': event['tournament'].get('category', {}).get('name', 'Unknown'),
                    'status': event['status']['type']
                }
                
                # Add scores if match started
                if 'homeScore' in event:
                    match_info['home_score'] = event['homeScore'].get('current', 0)
                    match_info['away_score'] = event['awayScore'].get('current', 0)
                
                matches.append(match_info)
            except Exception as e:
                print(f"⚠️ Error parsing match: {e}")
                continue
        
        print(f"✅ Found {len(matches)} matches")
        return matches
    
    def get_match_statistics(self, match_id):
        """
        Get detailed statistics for a match (including xG!)
        
        Args:
            match_id: Sofascore match ID
        
        Returns:
            Dict with statistics
        """
        endpoint = f"/events/statistics/{match_id}"
        data = self._make_request(endpoint)
        
        if not data or 'statistics' not in data:
            return {}
        
        stats = {}
        
        for period in data['statistics']:
            for group in period.get('groups', []):
                for stat in group.get('statisticsItems', []):
                    stat_name = stat['name'].lower()
                    
                    # Extract xG if available
                    if 'expected goals' in stat_name or 'xg' in stat_name:
                        stats['home_xg'] = float(stat.get('home', 0))
                        stats['away_xg'] = float(stat.get('away', 0))
                    
                    # Extract other key stats
                    elif 'shots' in stat_name and 'total' in stat_name:
                        stats['home_shots'] = int(stat.get('home', 0))
                        stats['away_shots'] = int(stat.get('away', 0))
                    
                    elif 'shots on target' in stat_name:
                        stats['home_sot'] = int(stat.get('home', 0))
                        stats['away_sot'] = int(stat.get('away', 0))
                    
                    elif 'possession' in stat_name:
                        stats['home_possession'] = int(stat.get('home', 0))
                        stats['away_possession'] = int(stat.get('away', 0))
        
        return stats
    
    def get_team_form(self, team_id, last_n=5):
        """Get recent form for a team"""
        endpoint = f"/teams/results/{team_id}"
        data = self._make_request(endpoint)
        
        if not data or 'events' not in data:
            return "N/A"
        
        form = []
        for event in data['events'][:last_n]:
            if event['homeTeam']['id'] == team_id:
                home_score = event['homeScore']['current']
                away_score = event['awayScore']['current']
                
                if home_score > away_score:
                    form.append('W')
                elif home_score < away_score:
                    form.append('L')
                else:
                    form.append('D')
            else:
                home_score = event['homeScore']['current']
                away_score = event['awayScore']['current']
                
                if away_score > home_score:
                    form.append('W')
                elif away_score < home_score:
                    form.append('L')
                else:
                    form.append('D')
        
        return '-'.join(form)
    
    def get_h2h(self, home_id, away_id):
        """Get head-to-head history"""
        endpoint = f"/teams/h2h/{home_id}/{away_id}"
        data = self._make_request(endpoint)
        
        if not data or 'events' not in data:
            return []
        
        return data['events'][:5]  # Last 5 H2H matches
    
    def get_upcoming_matches(self, days_ahead=7):
        """
        Get upcoming matches for next N days
        
        Args:
            days_ahead: Number of days to look ahead
        
        Returns:
            DataFrame with upcoming matches
        """
        all_matches = []
        
        for day_offset in range(days_ahead + 1):
            date = (datetime.now() + timedelta(days=day_offset)).strftime('%Y-%m-%d')
            matches = self.get_matches_by_date(date)
            all_matches.extend(matches)
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        if not all_matches:
            return pd.DataFrame()
        
        df = pd.DataFrame(all_matches)
        print(f"\n✅ Total upcoming matches: {len(df)}")
        return df
    
    def get_league_matches(self, tournament_id, date_from=None, date_to=None):
        """
        Get matches for specific league/tournament
        
        Args:
            tournament_id: Sofascore tournament ID
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
        
        Returns:
            DataFrame with matches
        """
        if date_from is None:
            date_from = datetime.now().strftime('%Y-%m-%d')
        
        if date_to is None:
            date_to = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        print(f"\n📡 Fetching league {tournament_id} matches...")
        
        # Get all matches in date range
        all_matches = self.get_upcoming_matches(days_ahead=7)
        
        if all_matches.empty:
            return pd.DataFrame()
        
        # Filter by tournament (would need tournament ID mapping)
        # For now return all
        return all_matches


# =============================================
# QUICK TEST FUNCTIONS
# =============================================

def test_sofascore_connection():
    """Test if Sofascore API works"""
    api = SofascoreAPI()
    
    print("="*80)
    print("🧪 TESTING SOFASCORE API (RapidAPI)")
    print("="*80)
    
    # Test matches for today
    matches = api.get_matches_by_date()
    
    if matches:
        print(f"\n✅ SUCCESS! Found {len(matches)} matches")
        print("\n📊 Sample matches:")
        for i, match in enumerate(matches[:5], 1):
            print(f"{i}. {match['home']} vs {match['away']}")
            print(f"   Tournament: {match['tournament']}")
            print(f"   Time: {match['match_time']}")
        return True
    else:
        print("\n❌ No matches found")
        return False


def get_detailed_match_data(match_id):
    """Get full details for a match including xG"""
    api = SofascoreAPI()
    
    print(f"\n📊 Getting detailed stats for match {match_id}...")
    stats = api.get_match_statistics(match_id)
    
    if stats:
        print("\n✅ Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    else:
        print("⚠️ No statistics available")
    
    return stats


if __name__ == "__main__":
    # Test connection
    test_sofascore_connection()
