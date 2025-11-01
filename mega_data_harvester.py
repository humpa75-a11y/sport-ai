#!/usr/bin/env python3
"""
🌍 MEGA DATA HARVESTER - HARVEST ALL THE DATA! 🌍

DOEL: Verzamel MASSIVE amounts van voetbaldata om exact score accuracy te verhogen!

BRONNEN:
1. API-Football - Historische data (gratis tier: 100 calls/dag)
2. Football-Data.co.uk - CSV downloads (GRATIS!)
3. Odds-Portal - Web scraping
4. FiveThirtyEight - Advanced stats
5. Understat - Expected goals (xG)

TARGET: 50,000+ matches voor 15%+ exact score accuracy!
"""

import requests
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time
from collections import defaultdict

print("="*80)
print("🌍 MEGA DATA HARVESTER - VERZAMEL ALLE DATA! 🌍")
print("="*80)

class MegaDataHarvester:
    def __init__(self):
        self.all_matches = []
        self.data_dir = 'data/harvested'
        os.makedirs(self.data_dir, exist_ok=True)
        
        # API keys (optioneel)
        self.api_football_key = os.environ.get('API_FOOTBALL_KEY', None)
        
        print("✅ Mega Data Harvester initialized!")
        
    def harvest_football_data_uk(self, seasons=10):
        """
        🇬🇧 HARVEST FOOTBALL-DATA.CO.UK
        
        GRATIS CSV downloads met 10+ jaar historische data!
        Leagues: Premier League, Eredivisie, Bundesliga, La Liga, Serie A, etc.
        """
        print(f"\n{'='*80}")
        print("🇬🇧 HARVESTING FOOTBALL-DATA.CO.UK (FREE CSV DATA)")
        print("="*80)
        
        base_url = "https://www.football-data.co.uk"
        
        # Leagues om te harvesten
        leagues = {
            'E0': 'Premier League',
            'N1': 'Eredivisie',
            'D1': 'Bundesliga',
            'SP1': 'La Liga',
            'I1': 'Serie A',
            'F1': 'Ligue 1',
            'P1': 'Primeira Liga',
            'T1': 'Super Lig'
        }
        
        current_year = 2024
        harvested_count = 0
        
        for league_code, league_name in leagues.items():
            print(f"\n📊 {league_name} ({league_code}):")
            
            for year in range(current_year - seasons, current_year + 1):
                # Format: 2324 voor seizoen 2023-2024
                season_str = f"{str(year-1)[-2:]}{str(year)[-2:]}"
                
                # URL naar CSV
                csv_url = f"{base_url}/mmz4281/{season_str}/{league_code}.csv"
                
                try:
                    print(f"   Downloading {year-1}/{year}...", end=' ')
                    response = requests.get(csv_url, timeout=10)
                    
                    if response.status_code == 200:
                        # Parse CSV
                        from io import StringIO
                        df = pd.read_csv(StringIO(response.text))
                        
                        # Filter alleen voltooide wedstrijden
                        df = df[df['FTHG'].notna() & df['FTAG'].notna()]
                        
                        # Converteer naar ons formaat
                        for _, row in df.iterrows():
                            match = {
                                'home_team': row['HomeTeam'],
                                'away_team': row['AwayTeam'],
                                'home_score': int(row['FTHG']),
                                'away_score': int(row['FTAG']),
                                'date': row.get('Date', f"{year-1}-01-01"),
                                'league': league_name,
                                'season': f"{year-1}/{year}",
                                'source': 'football-data.co.uk'
                            }
                            
                            # Extra stats als beschikbaar
                            if 'HS' in row and pd.notna(row['HS']):
                                match['home_shots'] = int(row['HS'])
                            if 'AS' in row and pd.notna(row['AS']):
                                match['away_shots'] = int(row['AS'])
                            if 'HST' in row and pd.notna(row['HST']):
                                match['home_shots_on_target'] = int(row['HST'])
                            if 'AST' in row and pd.notna(row['AST']):
                                match['away_shots_on_target'] = int(row['AST'])
                            
                            self.all_matches.append(match)
                            harvested_count += 1
                        
                        print(f"✅ {len(df)} matches")
                        time.sleep(0.5)  # Be polite
                    else:
                        print(f"⚠️ Not available")
                
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        print(f"\n✅ Football-Data.co.uk: {harvested_count} matches harvested!")
        return harvested_count
    
    def harvest_api_football(self, seasons=3):
        """
        🌐 HARVEST API-FOOTBALL
        
        Modern API met real-time data.
        FREE tier: 100 calls/day (genoeg voor 3 seizoenen!)
        """
        if not self.api_football_key:
            print("\n⚠️ API-Football key not found. Skipping...")
            print("   Get free key at: https://www.api-football.com/")
            return 0
        
        print(f"\n{'='*80}")
        print("🌐 HARVESTING API-FOOTBALL (MODERN API)")
        print("="*80)
        
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': self.api_football_key
        }
        
        # Eredivisie league ID = 88
        leagues_to_harvest = [
            {'id': 88, 'name': 'Eredivisie', 'country': 'Netherlands'},
            {'id': 89, 'name': 'Eerste Divisie', 'country': 'Netherlands'},
        ]
        
        harvested_count = 0
        current_year = 2024
        
        for league in leagues_to_harvest:
            print(f"\n📊 {league['name']}:")
            
            for year in range(current_year - seasons, current_year + 1):
                try:
                    print(f"   Fetching {year}...", end=' ')
                    
                    # Get all fixtures for this season
                    url = f"https://v3.football.api-sports.io/fixtures"
                    params = {
                        'league': league['id'],
                        'season': year
                    }
                    
                    response = requests.get(url, headers=headers, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get('results', 0) > 0:
                            fixtures = data['response']
                            
                            for fixture in fixtures:
                                # Only finished matches
                                if fixture['fixture']['status']['short'] == 'FT':
                                    match = {
                                        'home_team': fixture['teams']['home']['name'],
                                        'away_team': fixture['teams']['away']['name'],
                                        'home_score': fixture['goals']['home'],
                                        'away_score': fixture['goals']['away'],
                                        'date': fixture['fixture']['date'],
                                        'league': league['name'],
                                        'season': str(year),
                                        'source': 'api-football',
                                        'venue': fixture['fixture']['venue']['name']
                                    }
                                    
                                    # Extra stats
                                    if 'statistics' in fixture:
                                        stats = fixture.get('statistics', [])
                                        if len(stats) >= 2:
                                            match['home_shots'] = self._get_stat(stats[0], 'Total Shots')
                                            match['away_shots'] = self._get_stat(stats[1], 'Total Shots')
                                            match['home_possession'] = self._get_stat(stats[0], 'Ball Possession')
                                            match['away_possession'] = self._get_stat(stats[1], 'Ball Possession')
                                    
                                    self.all_matches.append(match)
                                    harvested_count += 1
                            
                            print(f"✅ {len(fixtures)} fixtures")
                        else:
                            print(f"⚠️ No data")
                    else:
                        print(f"❌ API Error: {response.status_code}")
                    
                    time.sleep(1)  # Rate limiting
                
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        print(f"\n✅ API-Football: {harvested_count} matches harvested!")
        return harvested_count
    
    def _get_stat(self, team_stats, stat_name):
        """Helper om statistiek uit API-Football data te halen."""
        stats = team_stats.get('statistics', [])
        for stat in stats:
            if stat.get('type') == stat_name:
                value = stat.get('value')
                # Handle percentage strings
                if isinstance(value, str) and '%' in value:
                    return int(value.replace('%', ''))
                return value
        return None
    
    def deduplicate_matches(self):
        """
        🔍 VERWIJDER DUPLICATEN
        
        Meerdere bronnen = duplicaten!
        Match op: home_team + away_team + date
        """
        print(f"\n{'='*80}")
        print("🔍 DEDUPLICATING MATCHES")
        print("="*80)
        
        print(f"   Voor deduplicatie: {len(self.all_matches)} matches")
        
        seen = set()
        unique_matches = []
        
        for match in self.all_matches:
            # Create unique key
            key = f"{match['home_team']}:{match['away_team']}:{match['date'][:10]}"
            
            if key not in seen:
                seen.add(key)
                unique_matches.append(match)
        
        removed = len(self.all_matches) - len(unique_matches)
        self.all_matches = unique_matches
        
        print(f"   Na deduplicatie: {len(self.all_matches)} matches")
        print(f"   ✅ {removed} duplicaten verwijderd!")
    
    def enrich_with_head_to_head(self):
        """
        🔄 VOEG HEAD-TO-HEAD DATA TOE
        
        Voor elk match, kijk naar de laatste 5 onderlinge duels.
        Dit kan exact score accuracy MASSIEF verbeteren!
        """
        print(f"\n{'='*80}")
        print("🔄 ENRICHING WITH HEAD-TO-HEAD DATA")
        print("="*80)
        
        # Group matches by teams
        h2h_cache = defaultdict(list)
        
        for match in self.all_matches:
            key = frozenset([match['home_team'], match['away_team']])
            h2h_cache[key].append(match)
        
        enriched_count = 0
        
        for i, match in enumerate(self.all_matches):
            teams_key = frozenset([match['home_team'], match['away_team']])
            previous_matches = h2h_cache[teams_key]
            
            # Filter alleen EERDERE wedstrijden
            h2h_matches = [
                m for m in previous_matches 
                if m['date'] < match['date']
            ][-5:]  # Laatste 5
            
            if h2h_matches:
                # Bereken h2h stats
                home_wins = sum(1 for m in h2h_matches 
                               if (m['home_team'] == match['home_team'] and m['home_score'] > m['away_score']) or
                                  (m['away_team'] == match['home_team'] and m['away_score'] > m['home_score']))
                
                total_goals = sum(m['home_score'] + m['away_score'] for m in h2h_matches)
                avg_goals = total_goals / len(h2h_matches)
                
                match['h2h_matches'] = len(h2h_matches)
                match['h2h_home_wins'] = home_wins
                match['h2h_avg_goals'] = round(avg_goals, 2)
                
                enriched_count += 1
            
            if (i + 1) % 5000 == 0:
                print(f"   Processed {i+1}/{len(self.all_matches)} matches...")
        
        print(f"✅ {enriched_count} matches enriched with H2H data!")
    
    def analyze_score_patterns(self):
        """
        📊 ANALYSEER SCORE PATRONEN
        
        Welke scores komen het meest voor?
        Dit helpt het model focussen op realistische scores!
        """
        print(f"\n{'='*80}")
        print("📊 ANALYZING SCORE PATTERNS")
        print("="*80)
        
        score_distribution = defaultdict(int)
        
        for match in self.all_matches:
            score = f"{match['home_score']}-{match['away_score']}"
            score_distribution[score] += 1
        
        # Top 20 meest voorkomende scores
        top_scores = sorted(score_distribution.items(), key=lambda x: x[1], reverse=True)[:20]
        
        print("\n🎯 TOP 20 MEEST VOORKOMENDE SCORES:")
        total_matches = len(self.all_matches)
        
        for i, (score, count) in enumerate(top_scores, 1):
            percentage = (count / total_matches) * 100
            print(f"   {i:2d}. {score:5s} - {count:5d} matches ({percentage:5.2f}%)")
        
        # Sla op voor model training
        pattern_data = {
            'total_matches': total_matches,
            'top_scores': [
                {'score': score, 'count': count, 'percentage': round((count/total_matches)*100, 2)}
                for score, count in top_scores
            ],
            'analyzed_at': datetime.now().isoformat()
        }
        
        with open(f'{self.data_dir}/score_patterns.json', 'w') as f:
            json.dump(pattern_data, f, indent=2)
        
        print(f"\n✅ Score patterns saved to {self.data_dir}/score_patterns.json")
    
    def save_harvested_data(self):
        """💾 SLA ALLE DATA OP"""
        print(f"\n{'='*80}")
        print("💾 SAVING HARVESTED DATA")
        print("="*80)
        
        # Save as JSON
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_path = f'{self.data_dir}/mega_harvest_{timestamp}.json'
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.all_matches, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON saved: {json_path}")
        print(f"   Total matches: {len(self.all_matches)}")
        print(f"   File size: {os.path.getsize(json_path) / 1024 / 1024:.2f} MB")
        
        # Save as CSV (voor Excel analyse)
        csv_path = f'{self.data_dir}/mega_harvest_{timestamp}.csv'
        df = pd.DataFrame(self.all_matches)
        df.to_csv(csv_path, index=False)
        print(f"✅ CSV saved: {csv_path}")
        
        # Update mega_training_data.json (voor training script)
        mega_path = 'data/mega_training_data.json'
        with open(mega_path, 'w', encoding='utf-8') as f:
            json.dump(self.all_matches, f, indent=2, ensure_ascii=False)
        print(f"✅ Training data updated: {mega_path}")
        
        return json_path, csv_path
    
    def get_statistics(self):
        """📊 HARVEST STATISTIEKEN"""
        print(f"\n{'='*80}")
        print("📊 HARVEST STATISTICS")
        print("="*80)
        
        total_matches = len(self.all_matches)
        
        # Per league
        leagues = defaultdict(int)
        for match in self.all_matches:
            leagues[match['league']] += 1
        
        print(f"\n📊 MATCHES PER LEAGUE:")
        for league, count in sorted(leagues.items(), key=lambda x: x[1], reverse=True):
            print(f"   {league:30s}: {count:5d} matches")
        
        # Per source
        sources = defaultdict(int)
        for match in self.all_matches:
            sources[match['source']] += 1
        
        print(f"\n🌐 MATCHES PER SOURCE:")
        for source, count in sources.items():
            print(f"   {source:30s}: {count:5d} matches")
        
        # Date range
        dates = [match['date'] for match in self.all_matches if 'date' in match]
        if dates:
            print(f"\n📅 DATE RANGE:")
            print(f"   Oldest: {min(dates)}")
            print(f"   Newest: {max(dates)}")
        
        print(f"\n🎯 TOTAL HARVESTED: {total_matches:,} matches")
        
        return {
            'total_matches': total_matches,
            'leagues': dict(leagues),
            'sources': dict(sources)
        }


def main():
    """🚀 MAIN HARVEST ROUTINE"""
    harvester = MegaDataHarvester()
    
    # 1. Harvest Football-Data.co.uk (GRATIS! Grootste bron!)
    harvester.harvest_football_data_uk(seasons=10)
    
    # 2. Harvest API-Football (als key beschikbaar)
    harvester.harvest_api_football(seasons=3)
    
    # 3. Deduplicate
    harvester.deduplicate_matches()
    
    # 4. Enrich met Head-to-Head
    harvester.enrich_with_head_to_head()
    
    # 5. Analyze score patterns
    harvester.analyze_score_patterns()
    
    # 6. Save everything
    harvester.save_harvested_data()
    
    # 7. Statistics
    stats = harvester.get_statistics()
    
    print("\n" + "="*80)
    print("🎉 MEGA DATA HARVEST COMPLETE! 🎉")
    print("="*80)
    print(f"✅ {stats['total_matches']:,} matches verzameld!")
    print(f"✅ Data saved en klaar voor training!")
    print(f"🚀 Run 'python train_HYPER_AGGRESSIVE.py' om met nieuwe data te trainen!")
    print("="*80)


if __name__ == '__main__':
    main()
