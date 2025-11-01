"""
🇳🇱 EERSTE DIVISIE API SCRAPER 🇳🇱

Scraped Eerste Divisie data via API-Football en andere bronnen!

Bronnen:
1. API-Football (beste optie, real-time data)
2. Odds-Portal (via web scraping)
3. FlashScore (alternatief)

Doel: 5-10 seizoenen Eerste Divisie data voor betere voorspellingen!
"""

import requests
import pandas as pd
import os
from datetime import datetime
import time
import json

class EersteDivisieAPIScraper:
    """Scraped Eerste Divisie data via API-Football."""
    
    def __init__(self, api_key=None):
        self.all_matches = []
        self.api_key = api_key or os.getenv('API_FOOTBALL_KEY')
        self.base_url = "https://v3.football.api-sports.io"
        
        # Eerste Divisie league ID op API-Football
        self.league_id = 89  # Eerste Divisie
        self.country = "Netherlands"
        
    def scrape_api_football(self, start_year=2015, end_year=2024):
        """
        🏆 API-FOOTBALL SCRAPER
        
        Scraped historische Eerste Divisie data via API-Football
        """
        if not self.api_key:
            print("❌ Geen API_FOOTBALL_KEY gevonden!")
            print("   Zet je API key als environment variabele:")
            print("   $env:API_FOOTBALL_KEY='jouw_api_key'")
            return 0
        
        print("\n" + "="*80)
        print("🇳🇱 EERSTE DIVISIE SCRAPER - API-FOOTBALL")
        print("="*80)
        print(f"   API Key: {'***' + self.api_key[-6:]}")
        print(f"   League ID: {self.league_id} (Eerste Divisie)")
        
        headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'v3.football.api-sports.io'
        }
        
        harvested_count = 0
        
        for year in range(start_year, end_year + 1):
            season = year  # API gebruikt jaar van seizoenstart
            print(f"\n📥 Seizoen {year}/{year+1}...")
            
            try:
                # Haal fixtures op voor dit seizoen
                url = f"{self.base_url}/fixtures"
                params = {
                    'league': self.league_id,
                    'season': season
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('errors') and len(data['errors']) > 0:
                        print(f"   ❌ API Error: {data['errors']}")
                        continue
                    
                    fixtures = data.get('response', [])
                    matches_in_season = 0
                    
                    for fixture in fixtures:
                        try:
                            # Skip niet-gespeelde wedstrijden
                            if fixture['fixture']['status']['short'] not in ['FT', 'AET', 'PEN']:
                                continue
                            
                            match_data = {
                                'date': fixture['fixture']['date'].split('T')[0],
                                'season': f"{year}/{year+1}",
                                'home_team': fixture['teams']['home']['name'],
                                'away_team': fixture['teams']['away']['name'],
                                'home_goals': fixture['goals']['home'],
                                'away_goals': fixture['goals']['away'],
                                'result': self._get_result(fixture['goals']['home'], fixture['goals']['away']),
                                'source': 'api-football',
                                'league': 'Eerste Divisie',
                                'country': 'Netherlands',
                                'fixture_id': fixture['fixture']['id']
                            }
                            
                            # Extra statistieken (als beschikbaar)
                            if 'statistics' in fixture:
                                stats = fixture.get('statistics', [])
                                match_data['has_stats'] = True
                            
                            self.all_matches.append(match_data)
                            matches_in_season += 1
                            
                        except Exception as e:
                            print(f"   ⚠️ Fout bij verwerken fixture: {e}")
                            continue
                    
                    harvested_count += matches_in_season
                    print(f"   ✅ {matches_in_season} matches gevonden!")
                    
                elif response.status_code == 429:
                    print(f"   ⚠️ API rate limit bereikt! Wacht 60 seconden...")
                    time.sleep(60)
                    continue
                elif response.status_code == 404:
                    print(f"   ⚠️ Data niet beschikbaar voor seizoen {year}/{year+1}")
                else:
                    print(f"   ❌ HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                print(f"   ❌ Fout: {e}")
            
            # Wees beleefd naar de API (rate limiting)
            time.sleep(2)
        
        print(f"\n{'='*80}")
        print(f"✅ TOTAAL GEOOGST: {harvested_count} Eerste Divisie matches!")
        print(f"{'='*80}\n")
        
        return harvested_count
    
    def scrape_odds_portal_manual(self):
        """
        🌐 ODDS-PORTAL ALTERNATIEF
        
        Instructies voor handmatig scrapen via odds-portal-scraper
        """
        print("\n" + "="*80)
        print("🌐 ALTERNATIEVE BRON: ODDS-PORTAL")
        print("="*80)
        print("\nAls API-Football niet werkt, kun je Odds-Portal gebruiken:")
        print("\n1. Ga naar: odds-portal-scraper directory")
        print("2. Run: node index.js historic eerste-divisie 2015 2024 --odds-format eu --local ../data")
        print("3. Data wordt opgeslagen in JSON formaat")
        print("4. Converteer JSON naar CSV met deze scraper")
        print("\n" + "="*80 + "\n")
    
    def _get_result(self, home_goals, away_goals):
        """Bepaal resultaat (H/D/A)."""
        if home_goals > away_goals:
            return 'H'
        elif home_goals < away_goals:
            return 'A'
        else:
            return 'D'
    
    def save_to_csv(self, filename=None):
        """Sla alle gescrapede data op in CSV formaat."""
        if not self.all_matches:
            print("❌ Geen data om op te slaan!")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"eerste_divisie_api_data_{timestamp}.csv"
        
        # Maak data directory als die niet bestaat
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)
        
        # Converteer naar DataFrame en sla op
        df = pd.DataFrame(self.all_matches)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        print(f"\n💾 DATA OPGESLAGEN!")
        print(f"   📁 Bestand: {filepath}")
        print(f"   📊 Matches: {len(self.all_matches)}")
        print(f"   📅 Periode: {df['season'].min()} tot {df['season'].max()}")
        print(f"   ⚽ Unieke teams: {len(set(df['home_team'].unique()) | set(df['away_team'].unique()))}")
        print(f"   🎯 Gemiddeld doelpunten: {(df['home_goals'].mean() + df['away_goals'].mean()):.2f} per wedstrijd")
        
        return filepath
    
    def get_statistics(self):
        """Laat statistieken zien van de gescrapede data."""
        if not self.all_matches:
            print("❌ Nog geen data gescraped!")
            return
        
        df = pd.DataFrame(self.all_matches)
        
        print("\n" + "="*80)
        print("📊 EERSTE DIVISIE DATA STATISTIEKEN")
        print("="*80)
        
        print(f"\n📈 ALGEMEEN:")
        print(f"   Totaal matches: {len(df)}")
        print(f"   Seizoenen: {df['season'].nunique()}")
        print(f"   Periode: {df['season'].min()} tot {df['season'].max()}")
        all_teams = set(df['home_team'].unique()) | set(df['away_team'].unique())
        print(f"   Unieke teams: {len(all_teams)}")
        
        print(f"\n⚽ DOELPUNTEN:")
        print(f"   Gemiddeld thuis: {df['home_goals'].mean():.2f}")
        print(f"   Gemiddeld uit: {df['away_goals'].mean():.2f}")
        print(f"   Totaal per wedstrijd: {(df['home_goals'].mean() + df['away_goals'].mean()):.2f}")
        print(f"   Hoogste thuisscore: {df['home_goals'].max()}")
        print(f"   Hoogste uitscore: {df['away_goals'].max()}")
        
        print(f"\n🏆 RESULTATEN:")
        result_counts = df['result'].value_counts()
        total = len(df)
        print(f"   Thuisoverwinningen: {result_counts.get('H', 0)} ({result_counts.get('H', 0)/total*100:.1f}%)")
        print(f"   Gelijkspel: {result_counts.get('D', 0)} ({result_counts.get('D', 0)/total*100:.1f}%)")
        print(f"   Uitoverwinningen: {result_counts.get('A', 0)} ({result_counts.get('A', 0)/total*100:.1f}%)")
        
        print(f"\n🎯 TOP 10 MEEST VOORKOMENDE TEAMS:")
        team_counts = pd.concat([df['home_team'], df['away_team']]).value_counts().head(10)
        for team, count in team_counts.items():
            print(f"   {team}: {count} wedstrijden")
        
        print(f"\n🔥 TOP 5 MEEST SCORENDE TEAMS (THUIS):")
        top_home = df.groupby('home_team')['home_goals'].mean().sort_values(ascending=False).head(5)
        for team, avg_goals in top_home.items():
            print(f"   {team}: {avg_goals:.2f} goals/wedstrijd")
        
        print("="*80 + "\n")


def main():
    """🚀 HOOFDPROGRAMMA - SCRAPE EERSTE DIVISIE DATA!"""
    
    print("\n" + "="*80)
    print("🇳🇱 EERSTE DIVISIE API SCRAPER 🇳🇱")
    print("="*80)
    print("\n📋 Dit script scraped historische Eerste Divisie data via API-Football!")
    print("   Doel: 5-10 seizoenen = 1000-2000 matches\n")
    
    # Check voor API key
    api_key = os.getenv('API_FOOTBALL_KEY')
    if not api_key:
        print("\n⚠️ GEEN API KEY GEVONDEN!")
        print("\nOm dit script te gebruiken:")
        print("1. Maak een gratis account op: https://www.api-football.com/")
        print("2. Kopieer je API key")
        print("3. Zet de key als environment variabele:")
        print("   PowerShell: $env:API_FOOTBALL_KEY='jouw_api_key'")
        print("   CMD: set API_FOOTBALL_KEY=jouw_api_key")
        print("\nOf gebruik de Odds-Portal scraper als alternatief!\n")
        
        scraper = EersteDivisieAPIScraper()
        scraper.scrape_odds_portal_manual()
        return
    
    print(f"✅ API Key gevonden: {'***' + api_key[-6:]}\n")
    
    input("Druk op ENTER om te starten...")
    
    # Initialiseer scraper
    scraper = EersteDivisieAPIScraper(api_key)
    
    # Scrape API-Football (2015-2024 = 10 seizoenen!)
    print("\n🚀 STARTEN MET SCRAPEN VIA API-FOOTBALL...")
    scraper.scrape_api_football(start_year=2015, end_year=2024)
    
    if scraper.all_matches:
        # Laat statistieken zien
        scraper.get_statistics()
        
        # Sla op
        filepath = scraper.save_to_csv()
        
        print("\n" + "="*80)
        print("🎉 EERSTE DIVISIE SCRAPING COMPLEET!")
        print("="*80)
        print(f"\n📁 Data opgeslagen in: {filepath}")
        print(f"📊 Totaal matches: {len(scraper.all_matches)}")
        print("\n🎓 VOLGENDE STAP:")
        print("   1. Train een nieuw PROFESSOR model met Eerste Divisie data")
        print("   2. Voeg deze teams toe aan team_database.json")
        print("   3. Verbeter accuracy van 8-10% naar 10-12%!")
        print("\n💪 DE PROFESSOR WORDT NOG SLIMMER! 🧠\n")
    else:
        print("\n❌ Geen data gevonden!")
        print("\nProbeer een van deze alternatieven:")
        print("1. Check je API key (gratis tier heeft limiet van 100 requests/dag)")
        print("2. Gebruik Odds-Portal scraper")
        print("3. Gebruik FlashScore scraper")
        print("4. Wacht 24 uur en probeer opnieuw (rate limit reset)")


if __name__ == "__main__":
    main()
