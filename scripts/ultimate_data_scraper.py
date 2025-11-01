"""
🔥 ULTIMATE DATA SCRAPER 🔥

Haalt VERSE data op van ALLE bronnen en bereidt voor voor ZWARE AI TRAINING!

Bronnen:
1. API-Football (live fixtures + statistieken)
2. The Odds API (odds + market data)
3. Odds-Portal Scraper (historische data)
4. Combineert alles tot MASTER DATASET

Output: Fresh training data voor KILLER AI
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time

class UltimateDataScraper:
    """MASTER SCRAPER - Haalt ALLE data op voor AI training"""
    
    def __init__(self):
        self.api_football_key = os.environ.get('API_FOOTBALL_KEY', '')
        self.odds_api_key = os.environ.get('ODDS_API_KEY', '')
        
        # Belangrijke leagues
        self.leagues = {
            39: 'Premier League',
            140: 'La Liga', 
            78: 'Bundesliga',
            135: 'Serie A',
            61: 'Ligue 1',
            88: 'Eredivisie',
            2: 'Champions League',
            3: 'Europa League'
        }
        
        self.all_data = []
        
    def scrape_api_football_fixtures(self, season=2024, days_back=90):
        """
        Haal fixtures + statistics op van API-Football
        
        Args:
            season: Seizoen (2024 voor 2024/2025)
            days_back: Hoeveel dagen terug
        """
        print("\n" + "="*80)
        print("SCRAPING API-FOOTBALL - FIXTURES + STATS")
        print("="*80)
        
        if not self.api_football_key:
            print("ERROR: No API-Football key found!")
            return []
        
        all_fixtures = []
        headers = {'x-apisports-key': self.api_football_key}
        
        # Datum range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        for league_id, league_name in self.leagues.items():
            print(f"\n{league_name} (ID: {league_id})...")
            
            try:
                # Haal fixtures op
                url = "https://v3.football.api-sports.io/fixtures"
                params = {
                    'league': league_id,
                    'season': season,
                    'from': start_date.strftime('%Y-%m-%d'),
                    'to': end_date.strftime('%Y-%m-%d'),
                    'status': 'FT'  # Alleen afgelopen wedstrijden
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    fixtures = data.get('response', [])
                    
                    print(f"   Found {len(fixtures)} finished matches")
                    
                    for fixture in fixtures:
                        # Basis fixture data
                        fixture_data = {
                            'fixture_id': fixture['fixture']['id'],
                            'date': fixture['fixture']['date'],
                            'league': league_name,
                            'league_id': league_id,
                            'home_team': fixture['teams']['home']['name'],
                            'away_team': fixture['teams']['away']['name'],
                            'home_goals': fixture['goals']['home'],
                            'away_goals': fixture['goals']['away'],
                            'home_id': fixture['teams']['home']['id'],
                            'away_id': fixture['teams']['away']['id']
                        }
                        
                        all_fixtures.append(fixture_data)
                    
                    # Rate limit: wacht even
                    time.sleep(1)
                    
                elif response.status_code == 429:
                    print(f"   Rate limit reached, waiting...")
                    time.sleep(60)
                    
                else:
                    print(f"   Error: Status {response.status_code}")
                    
            except Exception as e:
                print(f"   ERROR: {e}")
                continue
        
        print(f"\nTotal fixtures scraped: {len(all_fixtures)}")
        return all_fixtures
    
    def scrape_team_statistics(self, fixtures):
        """
        Haal team statistieken op voor alle teams in fixtures
        """
        print("\n" + "="*80)
        print("SCRAPING TEAM STATISTICS")
        print("="*80)
        
        if not self.api_football_key:
            print("ERROR: No API-Football key found!")
            return {}
        
        headers = {'x-apisports-key': self.api_football_key}
        team_stats = {}
        
        # Unieke teams
        teams = set()
        for f in fixtures:
            teams.add((f['home_id'], f['home_team'], f['league_id']))
            teams.add((f['away_id'], f['away_team'], f['league_id']))
        
        print(f"Fetching stats for {len(teams)} unique teams...")
        
        for i, (team_id, team_name, league_id) in enumerate(teams, 1):
            if team_id in team_stats:
                continue
                
            print(f"[{i}/{len(teams)}] {team_name}...", end=' ')
            
            try:
                url = "https://v3.football.api-sports.io/teams/statistics"
                params = {
                    'team': team_id,
                    'league': league_id,
                    'season': 2024
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('response'):
                        stats = data['response']
                        
                        team_stats[team_id] = {
                            'team_id': team_id,
                            'team_name': team_name,
                            'league_id': league_id,
                            'played': stats.get('fixtures', {}).get('played', {}).get('total', 0),
                            'wins': stats.get('fixtures', {}).get('wins', {}).get('total', 0),
                            'draws': stats.get('fixtures', {}).get('draws', {}).get('total', 0),
                            'losses': stats.get('fixtures', {}).get('loses', {}).get('total', 0),
                            'goals_for': stats.get('goals', {}).get('for', {}).get('total', {}).get('total', 0),
                            'goals_against': stats.get('goals', {}).get('against', {}).get('total', {}).get('total', 0),
                            'clean_sheets': stats.get('clean_sheet', {}).get('total', 0),
                            'failed_to_score': stats.get('failed_to_score', {}).get('total', 0)
                        }
                        
                        print("OK")
                    else:
                        print("No data")
                        
                    time.sleep(0.5)  # Rate limit
                    
                elif response.status_code == 429:
                    print("Rate limit!")
                    time.sleep(60)
                else:
                    print(f"Error {response.status_code}")
                    
            except Exception as e:
                print(f"ERROR: {e}")
                continue
        
        print(f"\nTotal team stats scraped: {len(team_stats)}")
        return team_stats
    
    def scrape_odds_data(self, days_back=30):
        """
        Haal odds data op van The Odds API
        """
        print("\n" + "="*80)
        print("SCRAPING ODDS DATA")
        print("="*80)
        
        if not self.odds_api_key:
            print("WARNING: No Odds API key found, skipping...")
            return []
        
        sports = [
            'soccer_epl',
            'soccer_spain_la_liga',
            'soccer_germany_bundesliga',
            'soccer_italy_serie_a',
            'soccer_france_ligue_one'
        ]
        
        all_odds = []
        
        for sport in sports:
            print(f"\n{sport}...", end=' ')
            
            try:
                url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
                params = {
                    'apiKey': self.odds_api_key,
                    'regions': 'eu,uk',
                    'markets': 'h2h',
                    'oddsFormat': 'decimal'
                }
                
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"{len(data)} matches with odds")
                    all_odds.extend(data)
                else:
                    print(f"Error {response.status_code}")
                    
            except Exception as e:
                print(f"ERROR: {e}")
                continue
        
        print(f"\nTotal odds scraped: {len(all_odds)}")
        return all_odds
    
    def combine_and_enrich_data(self, fixtures, team_stats, odds_data):
        """
        Combineer alle data tot MASTER training dataset
        """
        print("\n" + "="*80)
        print("COMBINING DATA INTO MASTER DATASET")
        print("="*80)
        
        enriched_data = []
        
        for fixture in fixtures:
            try:
                home_id = fixture['home_id']
                away_id = fixture['away_id']
                
                # Voeg team stats toe
                home_stats = team_stats.get(home_id, {})
                away_stats = team_stats.get(away_id, {})
                
                enriched = {
                    **fixture,
                    'home_played': home_stats.get('played', 0),
                    'home_wins': home_stats.get('wins', 0),
                    'home_draws': home_stats.get('draws', 0),
                    'home_losses': home_stats.get('losses', 0),
                    'home_goals_for': home_stats.get('goals_for', 0),
                    'home_goals_against': home_stats.get('goals_against', 0),
                    'away_played': away_stats.get('played', 0),
                    'away_wins': away_stats.get('wins', 0),
                    'away_draws': away_stats.get('draws', 0),
                    'away_losses': away_stats.get('losses', 0),
                    'away_goals_for': away_stats.get('goals_for', 0),
                    'away_goals_against': away_stats.get('goals_against', 0),
                }
                
                # Bereken extra features
                if enriched['home_played'] > 0:
                    enriched['home_win_rate'] = enriched['home_wins'] / enriched['home_played']
                    enriched['home_avg_goals_scored'] = enriched['home_goals_for'] / enriched['home_played']
                    enriched['home_avg_goals_conceded'] = enriched['home_goals_against'] / enriched['home_played']
                else:
                    enriched['home_win_rate'] = 0
                    enriched['home_avg_goals_scored'] = 0
                    enriched['home_avg_goals_conceded'] = 0
                
                if enriched['away_played'] > 0:
                    enriched['away_win_rate'] = enriched['away_wins'] / enriched['away_played']
                    enriched['away_avg_goals_scored'] = enriched['away_goals_for'] / enriched['away_played']
                    enriched['away_avg_goals_conceded'] = enriched['away_goals_against'] / enriched['away_played']
                else:
                    enriched['away_win_rate'] = 0
                    enriched['away_avg_goals_scored'] = 0
                    enriched['away_avg_goals_conceded'] = 0
                
                enriched_data.append(enriched)
                
            except Exception as e:
                print(f"Error enriching fixture {fixture.get('fixture_id')}: {e}")
                continue
        
        print(f"Enriched {len(enriched_data)} fixtures")
        return enriched_data
    
    def save_to_csv(self, data, filename):
        """Sla data op als CSV"""
        df = pd.DataFrame(data)
        filepath = os.path.join(os.path.dirname(__file__), '..', 'data', filename)
        df.to_csv(filepath, index=False)
        print(f"\nSaved to: {filepath}")
        print(f"Shape: {df.shape}")
        return filepath
    
    def run_full_scrape(self):
        """
        RUN COMPLETE SCRAPING PIPELINE
        """
        print("\n" + "="*80)
        print("ULTIMATE DATA SCRAPER - FULL PIPELINE")
        print("="*80)
        print(f"Start time: {datetime.now()}")
        print(f"API-Football Key: {'SET' if self.api_football_key else 'MISSING'}")
        print(f"Odds API Key: {'SET' if self.odds_api_key else 'MISSING'}")
        
        # Step 1: Scrape fixtures (SEIZOEN 2023 = 2023/2024)
        fixtures = self.scrape_api_football_fixtures(season=2023, days_back=180)
        
        if not fixtures:
            print("\nERROR: No fixtures scraped! Check API keys.")
            return None
        
        # Step 2: Scrape team statistics
        team_stats = self.scrape_team_statistics(fixtures)
        
        # Step 3: Scrape odds (optional)
        odds_data = self.scrape_odds_data(days_back=30)
        
        # Step 4: Combine all data
        master_data = self.combine_and_enrich_data(fixtures, team_stats, odds_data)
        
        # Step 5: Save to CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = self.save_to_csv(master_data, f'master_training_data_{timestamp}.csv')
        
        print("\n" + "="*80)
        print("SCRAPING COMPLETE!")
        print("="*80)
        print(f"End time: {datetime.now()}")
        print(f"Total records: {len(master_data)}")
        print(f"Ready for AI training!")
        
        return filepath


if __name__ == '__main__':
    scraper = UltimateDataScraper()
    filepath = scraper.run_full_scrape()
    
    if filepath:
        print(f"\n SUCCESS! Training data ready at: {filepath}")
        print("\nNext step: Run heavy AI training with:")
        print("  python scripts/ultimate_ai_trainer.py")
    else:
        print("\nFAILED! Check API keys and try again.")
