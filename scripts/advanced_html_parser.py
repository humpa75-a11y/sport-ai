"""
🔥 ADVANCED HTML PARSER
Analyseert gescrapte HTML en extraheert ALLE nuttige data

Input: unibet_results.html, jacks_sports.html
Output: Training data met scores, odds, teams
"""

from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime
import re
import os

class AdvancedHTMLParser:
    """Parse scraped HTML to extract training data"""
    
    def __init__(self):
        self.matches = []
        
    def parse_unibet_html(self):
        """Parse Unibet HTML file"""
        print("\n" + "="*80)
        print("[PARSE] Analyzing unibet_results.html...")
        print("="*80)
        
        try:
            with open('unibet_results.html', 'r', encoding='utf-8') as f:
                html = f.read()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Method 1: Find all score patterns
            score_pattern = r'(\w[\w\s]+?)\s+(\d+)\s*[-:]\s*(\d+)\s+(\w[\w\s]+?)(?:\s|$|<)'
            matches_found = re.findall(score_pattern, html)
            
            print(f"[PARSE] Found {len(matches_found)} potential matches")
            
            for i, match in enumerate(matches_found[:50]):  # First 50
                if len(match) == 4:
                    home_team, home_score, away_score, away_team = match
                    
                    # Clean team names
                    home_team = re.sub(r'[<>]', '', home_team).strip()
                    away_team = re.sub(r'[<>]', '', away_team).strip()
                    
                    # Validate it looks like a real match
                    if (len(home_team) > 2 and len(away_team) > 2 and 
                        home_team != away_team and
                        not any(char.isdigit() for char in home_team) and
                        not any(char.isdigit() for char in away_team)):
                        
                        match_data = {
                            'home_team': home_team,
                            'away_team': away_team,
                            'home_score': int(home_score),
                            'away_score': int(away_score),
                            'league': 'Unknown',
                            'source': 'unibet'
                        }
                        
                        self.matches.append(match_data)
                        
                        if i < 10:  # Show first 10
                            print(f"  ✅ {home_team} {home_score}-{away_score} {away_team}")
            
            # Method 2: Look for structured data in scripts
            scripts = soup.find_all('script')
            json_matches = 0
            
            for script in scripts:
                if script.string and 'event' in script.string.lower():
                    try:
                        # Try to find JSON objects
                        json_pattern = r'\{[^{}]*"homeName"[^{}]*"awayName"[^{}]*\}'
                        json_objs = re.findall(json_pattern, script.string)
                        
                        for json_str in json_objs:
                            try:
                                data = json.loads(json_str)
                                if 'homeName' in data and 'awayName' in data:
                                    json_matches += 1
                            except:
                                continue
                    except:
                        continue
            
            print(f"[PARSE] JSON structures found: {json_matches}")
            
        except Exception as e:
            print(f"[PARSE] Error: {str(e)}")
    
    def parse_jacks_html(self):
        """Parse Jack's HTML file"""
        print("\n" + "="*80)
        print("[PARSE] Analyzing jacks_sports.html...")
        print("="*80)
        
        try:
            with open('jacks_sports.html', 'r', encoding='utf-8') as f:
                html = f.read()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for match data
            score_matches = re.findall(r'(\w[\w\s]+?)\s+(\d+)\s*[-:]\s*(\d+)\s+(\w[\w\s]+)', html)
            
            print(f"[PARSE] Found {len(score_matches)} score patterns")
            
            for match in score_matches[:20]:
                if len(match) == 4:
                    home, h_score, a_score, away = match
                    print(f"  {home} {h_score}-{a_score} {away}")
            
            # Parse JSON data if available
            if os.path.exists('jacks_json_data.txt'):
                print("\n[PARSE] Analyzing Jack's JSON data...")
                
                with open('jacks_json_data.txt', 'r', encoding='utf-8') as f:
                    json_text = f.read()
                
                # Look for match objects
                match_patterns = [
                    r'"home":\s*"([^"]+)".*?"away":\s*"([^"]+)"',
                    r'"homeTeam":\s*"([^"]+)".*?"awayTeam":\s*"([^"]+)"',
                    r'"participant":\s*"([^"]+)"'
                ]
                
                for pattern in match_patterns:
                    matches = re.findall(pattern, json_text)
                    if matches:
                        print(f"[PARSE] Pattern found {len(matches)} matches")
                        break
            
        except Exception as e:
            print(f"[PARSE] Error: {str(e)}")
    
    def fetch_real_api_data(self):
        """Fetch REAL data from API-Football for training"""
        print("\n" + "="*80)
        print("[API] Fetching REAL historical data...")
        print("="*80)
        
        import requests
        
        api_key = "6bb5247fdf0b0081a72fc46c853dd210"
        headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }
        
        # Get recent results from major leagues
        # Use a specific recent date range that definitely has matches
        
        leagues = [
            (39, 'Premier League'),
            (140, 'La Liga'),
            (78, 'Bundesliga'),
            (135, 'Serie A'),
            (61, 'Ligue 1'),
            (88, 'Eredivisie')
        ]
        
        for league_id, league_name in leagues[:2]:  # Start with 2 leagues
            try:
                # Get last 10 fixtures
                url = "https://v3.football.api-sports.io/fixtures"
                params = {
                    'league': league_id,
                    'season': 2024,
                    'last': 20  # Last 20 matches
                }
                
                print(f"\n[API] {league_name}...")
                response = requests.get(url, headers=headers, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    fixtures = data.get('response', [])
                    
                    print(f"[API] Got {len(fixtures)} matches")
                    
                    for fixture in fixtures:
                        # Only take finished matches
                        if fixture['fixture']['status']['short'] == 'FT':
                            match = {
                                'league': league_name,
                                'date': fixture['fixture']['date'],
                                'home_team': fixture['teams']['home']['name'],
                                'away_team': fixture['teams']['away']['name'],
                                'home_score': fixture['goals']['home'],
                                'away_score': fixture['goals']['away'],
                                'source': 'api-football'
                            }
                            
                            self.matches.append(match)
                            print(f"  ✅ {match['home_team']} {match['home_score']}-{match['away_score']} {match['away_team']}")
                
                else:
                    print(f"[API] Error: {response.status_code}")
                    print(f"[API] Response: {response.text[:200]}")
                
                import time
                time.sleep(2)  # Rate limiting
                
            except Exception as e:
                print(f"[API] {league_name} error: {str(e)}")
                continue
    
    def save_training_data(self):
        """Save extracted data"""
        print("\n" + "="*80)
        print("[SAVE] Saving training data...")
        print("="*80)
        
        if not self.matches:
            print("[SAVE] No data to save!")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create DataFrame
        df = pd.DataFrame(self.matches)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['home_team', 'away_team', 'home_score', 'away_score'])
        
        print(f"[SAVE] Total unique matches: {len(df)}")
        
        # Save CSV
        csv_file = f'../data/real_training_data_{timestamp}.csv'
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"[SAVE] CSV: {csv_file}")
        
        # Save JSON
        json_file = f'../data/real_training_data_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.matches, f, indent=2, ensure_ascii=False)
        print(f"[SAVE] JSON: {json_file}")
        
        # Statistics
        print("\n[STATS] Dataset statistics:")
        print(f"  Total matches: {len(df)}")
        
        if 'league' in df.columns:
            print("\n  By league:")
            print(df['league'].value_counts().to_string())
        
        if 'home_score' in df.columns and 'away_score' in df.columns:
            # Score statistics
            df['total_goals'] = df['home_score'] + df['away_score']
            print(f"\n  Average goals per match: {df['total_goals'].mean():.2f}")
            print(f"  Most common score: {df.groupby(['home_score', 'away_score']).size().idxmax()}")
            
            print("\n  Top 10 scores:")
            score_counts = df.groupby(['home_score', 'away_score']).size().sort_values(ascending=False).head(10)
            for (h, a), count in score_counts.items():
                print(f"    {h}-{a}: {count} times")
        
        # Preview
        print("\n[PREVIEW] Sample matches:")
        print(df.head(20).to_string())
        
        return csv_file
    
    def run(self):
        """Run complete parsing"""
        print("\n" + "="*80)
        print("🔥 ADVANCED HTML PARSER")
        print("="*80)
        print(f"Time: {datetime.now()}\n")
        
        # Parse HTML files
        if os.path.exists('unibet_results.html'):
            self.parse_unibet_html()
        
        if os.path.exists('jacks_sports.html'):
            self.parse_jacks_html()
        
        # Fetch real API data
        self.fetch_real_api_data()
        
        # Save results
        if self.matches:
            csv_file = self.save_training_data()
            
            print("\n" + "="*80)
            print("✅ PARSING COMPLETE")
            print("="*80)
            print(f"\nExtracted {len(self.matches)} real matches with scores!")
            print(f"\nFile: {csv_file}")
            print("\n🎯 Ready for AI training!")
        else:
            print("\n⚠️ No matches extracted")
            print("Check HTML files exist and contain match data")


if __name__ == '__main__':
    parser = AdvancedHTMLParser()
    parser.run()
