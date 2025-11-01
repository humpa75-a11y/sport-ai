"""
🎯 IMPROVED DATA HUNTER - API-FIRST APPROACH
===========================================

Strategy:
1. Use free football APIs (API-Football, Football-Data.org)
2. Fallback to web scraping public sites
3. Store sources for every data point

VREET ALLES! 🦈
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import os

class ImprovedDataHunter:
    """Smart data hunter using APIs + web scraping"""
    
    def __init__(self):
        self.collected_data = {
            'matches': [],
            'team_stats': [],
            'sources': []
        }
        self.session = requests.Session()
        
        # API keys (free tiers)
        self.api_football_key = os.getenv('API_FOOTBALL_KEY', '6bb5247fdf0b0081a72fc46c853dd210')
        self.football_data_key = 'YOUR_FREE_KEY'  # football-data.org
        
    def fetch_api_football_results(self, league_id, season=2024):
        """
        Fetch results from API-Football (FREE tier: 100 requests/day)
        Leagues: 88=Eredivisie, 39=Premier League, 78=Bundesliga, 140=La Liga
        """
        print("\n" + "="*80)
        print(f"⚽ FETCHING FROM API-FOOTBALL (League {league_id})")
        print("="*80)
        
        url = "https://v3.football.api-sports.io/fixtures"
        headers = {
            'x-apisports-key': self.api_football_key
        }
        params = {
            'league': league_id,
            'season': season,
            'status': 'FT',  # Finished matches
            'last': 50  # Last 50 finished matches
        }
        
        try:
            print(f"[API] Request: {url}")
            print(f"[API] Params: {params}")
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            print(f"[API] Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Save raw response
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = f'data/api_football_league{league_id}_{timestamp}.json'
                os.makedirs('data', exist_ok=True)
                
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                print(f"[SAVE] Raw data: {save_path}")
                
                # Parse fixtures
                matches = []
                if 'response' in data:
                    fixtures = data['response']
                    print(f"[API] Found {len(fixtures)} fixtures")
                    
                    for fixture in fixtures:
                        try:
                            match = {
                                'home_team': fixture['teams']['home']['name'],
                                'away_team': fixture['teams']['away']['name'],
                                'home_score': fixture['goals']['home'],
                                'away_score': fixture['goals']['away'],
                                'league': fixture['league']['name'],
                                'date': fixture['fixture']['date'][:10],
                                'source': 'api-football',
                                'api_id': fixture['fixture']['id'],
                                'scraped_at': datetime.now().isoformat()
                            }
                            
                            # Add odds if available
                            # Note: Odds are premium feature, might not be available
                            
                            matches.append(match)
                            print(f"[MATCH] {match['home_team']} {match['home_score']}-{match['away_score']} {match['away_team']}")
                        
                        except KeyError as e:
                            print(f"[WARN] Missing key in fixture: {e}")
                            continue
                    
                    self.collected_data['matches'].extend(matches)
                    self.collected_data['sources'].append({
                        'type': 'api',
                        'name': 'api-football',
                        'url': url,
                        'league_id': league_id,
                        'matches_count': len(matches),
                        'file': save_path,
                        'scraped_at': datetime.now().isoformat()
                    })
                    
                    print(f"\n[SUCCESS] Collected {len(matches)} matches from API-Football")
                    return matches
                
                else:
                    print(f"[ERROR] Unexpected response format: {data}")
            
            else:
                print(f"[ERROR] API request failed: {response.status_code}")
                print(f"[ERROR] Response: {response.text[:500]}")
        
        except Exception as e:
            print(f"[ERROR] API-Football request failed: {e}")
        
        return []
    
    def fetch_football_data_org(self, competition='PL'):
        """
        Fetch from football-data.org (FREE tier: 10 requests/minute)
        Competitions: PL=Premier League, PD=La Liga, BL1=Bundesliga, etc.
        """
        print("\n" + "="*80)
        print(f"⚽ FETCHING FROM FOOTBALL-DATA.ORG ({competition})")
        print("="*80)
        
        # Free tier doesn't require API key
        url = f"https://api.football-data.org/v4/competitions/{competition}/matches"
        headers = {}  # No key needed for free tier
        
        params = {
            'status': 'FINISHED',
            'limit': 100
        }
        
        try:
            print(f"[API] Request: {url}")
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            print(f"[API] Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Save raw
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = f'data/football_data_org_{competition}_{timestamp}.json'
                
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                print(f"[SAVE] Raw data: {save_path}")
                
                # Parse matches
                matches = []
                if 'matches' in data:
                    for match in data['matches']:
                        try:
                            if match['status'] == 'FINISHED' and match['score']['fullTime']['home'] is not None:
                                m = {
                                    'home_team': match['homeTeam']['name'],
                                    'away_team': match['awayTeam']['name'],
                                    'home_score': match['score']['fullTime']['home'],
                                    'away_score': match['score']['fullTime']['away'],
                                    'league': match['competition']['name'],
                                    'date': match['utcDate'][:10],
                                    'source': 'football-data.org',
                                    'scraped_at': datetime.now().isoformat()
                                }
                                
                                matches.append(m)
                                print(f"[MATCH] {m['home_team']} {m['home_score']}-{m['away_score']} {m['away_team']}")
                        
                        except (KeyError, TypeError) as e:
                            continue
                    
                    self.collected_data['matches'].extend(matches)
                    self.collected_data['sources'].append({
                        'type': 'api',
                        'name': 'football-data.org',
                        'url': url,
                        'competition': competition,
                        'matches_count': len(matches),
                        'file': save_path,
                        'scraped_at': datetime.now().isoformat()
                    })
                    
                    print(f"\n[SUCCESS] Collected {len(matches)} matches from football-data.org")
                    return matches
            
            else:
                print(f"[ERROR] API request failed: {response.status_code}")
                print(f"[INFO] Response: {response.text[:500]}")
        
        except Exception as e:
            print(f"[ERROR] football-data.org request failed: {e}")
        
        return []
    
    def calculate_team_statistics(self):
        """Calculate team stats from collected matches"""
        print("\n" + "="*80)
        print("📊 CALCULATING TEAM STATISTICS")
        print("="*80)
        
        if not self.collected_data['matches']:
            print("[WARN] No matches available for statistics")
            return []
        
        df = pd.DataFrame(self.collected_data['matches'])
        
        # Get unique teams
        teams = list(set(list(df['home_team'].unique()) + list(df['away_team'].unique())))
        
        stats = []
        for team in teams:
            # Filter matches for this team
            home_matches = df[df['home_team'] == team]
            away_matches = df[df['away_team'] == team]
            
            # Calculate stats
            home_goals = home_matches['home_score'].sum()
            home_conceded = home_matches['away_score'].sum()
            away_goals = away_matches['away_score'].sum()
            away_conceded = away_matches['home_score'].sum()
            
            total_matches = len(home_matches) + len(away_matches)
            
            if total_matches > 0:
                team_stat = {
                    'team': team,
                    'matches_played': total_matches,
                    'goals_scored': int(home_goals + away_goals),
                    'goals_conceded': int(home_conceded + away_conceded),
                    'goals_per_match': round((home_goals + away_goals) / total_matches, 2),
                    'conceded_per_match': round((home_conceded + away_conceded) / total_matches, 2),
                    'home_matches': len(home_matches),
                    'away_matches': len(away_matches),
                    'calculated_at': datetime.now().isoformat()
                }
                
                stats.append(team_stat)
                print(f"[STATS] {team}: {team_stat['goals_scored']} scored, {team_stat['goals_conceded']} conceded in {total_matches} matches")
        
        self.collected_data['team_stats'] = stats
        print(f"\n[SUCCESS] Calculated statistics for {len(stats)} teams")
        
        return stats
    
    def save_all_data(self):
        """Save all collected data"""
        print("\n" + "="*80)
        print("💾 SAVING ALL COLLECTED DATA")
        print("="*80)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save matches
        if self.collected_data['matches']:
            df_matches = pd.DataFrame(self.collected_data['matches'])
            csv_file = f'data/api_matches_{timestamp}.csv'
            df_matches.to_csv(csv_file, index=False)
            print(f"[SAVE] Matches: {csv_file} ({len(df_matches)} rows)")
        
        # Save team stats
        if self.collected_data['team_stats']:
            df_stats = pd.DataFrame(self.collected_data['team_stats'])
            csv_file = f'data/api_team_stats_{timestamp}.csv'
            df_stats.to_csv(csv_file, index=False)
            print(f"[SAVE] Team stats: {csv_file} ({len(df_stats)} rows)")
        
        # Save complete data with sources
        json_file = f'data/api_data_complete_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, indent=2, ensure_ascii=False)
        print(f"[SAVE] Complete dataset: {json_file}")
        
        # Summary
        print("\n" + "="*80)
        print("📊 COLLECTION SUMMARY")
        print("="*80)
        print(f"Matches:        {len(self.collected_data['matches'])}")
        print(f"Team stats:     {len(self.collected_data['team_stats'])}")
        print(f"Sources:        {len(self.collected_data['sources'])}")
        print("="*80)
        
        return {
            'timestamp': timestamp,
            'matches': len(self.collected_data['matches']),
            'team_stats': len(self.collected_data['team_stats']),
            'sources': len(self.collected_data['sources'])
        }


def run_improved_hunt():
    """Run complete hunt with APIs"""
    print("\n" + "="*80)
    print("🦈 IMPROVED DATA HUNTER - STARTING!")
    print("="*80)
    print(f"Time: {datetime.now()}")
    print("="*80 + "\n")
    
    hunter = ImprovedDataHunter()
    
    # Fetch from multiple sources
    leagues = [
        (88, 'Eredivisie'),
        (39, 'Premier League'),
        (78, 'Bundesliga'),
        (140, 'La Liga')
    ]
    
    for league_id, league_name in leagues:
        print(f"\n{'='*80}")
        print(f"🎯 HUNTING: {league_name} (ID: {league_id})")
        print(f"{'='*80}")
        
        hunter.fetch_api_football_results(league_id, season=2024)
        time.sleep(2)  # Rate limiting
    
    # Also try football-data.org
    print("\n" + "="*80)
    print("🎯 HUNTING: Football-Data.org APIs")
    print("="*80)
    
    competitions = ['PL', 'PD', 'BL1', 'SA', 'FL1']  # Premier, La Liga, Bundesliga, Serie A, Ligue 1
    
    for comp in competitions:
        hunter.fetch_football_data_org(comp)
        time.sleep(7)  # Rate limit: 10 req/minute
    
    # Calculate statistics
    hunter.calculate_team_statistics()
    
    # Save everything
    summary = hunter.save_all_data()
    
    print("\n" + "="*80)
    print("✅ HUNT COMPLETE!")
    print("="*80)
    print(f"Total matches: {summary['matches']}")
    print(f"Total teams: {summary['team_stats']}")
    print(f"Sources: {summary['sources']}")
    print("="*80 + "\n")
    
    return hunter


if __name__ == '__main__':
    hunter = run_improved_hunt()
