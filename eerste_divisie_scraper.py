"""
🇳🇱 EERSTE DIVISIE MEGA SCRAPER 🇳🇱

Scraped historische data van de Nederlandse Eerste Divisie voor AI training!

Bronnen:
1. Football-Data.co.uk - CSV downloads (GRATIS! Betrouwbaar!)
2. API-Football (optioneel, als je API key hebt)

Doel: 5-10 seizoenen data (1000-2000 matches) voor betere Eerste Divisie voorspellingen!
"""

import requests
import pandas as pd
import os
from datetime import datetime
import time

class EersteDivisieScraper:
    """Scraped Eerste Divisie data van meerdere bronnen."""
    
    def __init__(self):
        self.all_matches = []
        self.base_url = "https://www.football-data.co.uk"
        
    def scrape_football_data_uk(self, start_year=2015, end_year=2024):
        """
        🇬🇧 FOOTBALL-DATA.CO.UK SCRAPER
        
        Scraped gratis CSV data van Nederlandse Eerste Divisie (code: D2)
        """
        print("\n" + "="*80)
        print("🇳🇱 EERSTE DIVISIE SCRAPER - FOOTBALL-DATA.CO.UK")
        print("="*80)
        
        # Eerste Divisie league code is D2
        league_code = 'D2'
        harvested_count = 0
        
        for year in range(start_year, end_year + 1):
            # Seizoen formaat: 2324 voor 2023/2024
            season_str = f"{str(year)[2:]}{str(year+1)[2:]}"
            csv_url = f"{self.base_url}/mmz4281/{season_str}/{league_code}.csv"
            
            print(f"\n📥 Seizoen {year}/{year+1} ({season_str})...")
            print(f"   URL: {csv_url}")
            
            try:
                response = requests.get(csv_url, timeout=10)
                
                if response.status_code == 200:
                    # Lees CSV in pandas
                    from io import StringIO
                    df = pd.read_csv(StringIO(response.text))
                    
                    # Verwijder rijen zonder datum (soms staan er notities onderaan)
                    df = df[df['Date'].notna()]
                    
                    matches_in_season = 0
                    
                    for idx, row in df.iterrows():
                        try:
                            # Parse datum
                            date_str = str(row['Date'])
                            
                            # Football-Data gebruikt DD/MM/YY of DD/MM/YYYY formaat
                            if '/' in date_str:
                                parts = date_str.split('/')
                                day = int(parts[0])
                                month = int(parts[1])
                                year_part = parts[2]
                                
                                # Handle 2-digit years
                                if len(year_part) == 2:
                                    # Assume 20xx for years 00-49, 19xx for 50-99
                                    full_year = 2000 + int(year_part) if int(year_part) < 50 else 1900 + int(year_part)
                                else:
                                    full_year = int(year_part)
                                
                                match_date = f"{full_year}-{month:02d}-{day:02d}"
                            else:
                                match_date = date_str
                            
                            match_data = {
                                'date': match_date,
                                'season': f"{year}/{year+1}",
                                'home_team': str(row['HomeTeam']).strip(),
                                'away_team': str(row['AwayTeam']).strip(),
                                'home_goals': int(row['FTHG']),  # Full Time Home Goals
                                'away_goals': int(row['FTAG']),  # Full Time Away Goals
                                'result': str(row['FTR']),  # Full Time Result (H/D/A)
                                'source': 'football-data.co.uk',
                                'league': 'Eerste Divisie',
                                'country': 'Netherlands'
                            }
                            
                            # Optionele extra statistieken (als beschikbaar)
                            if 'HS' in row and pd.notna(row['HS']):
                                match_data['home_shots'] = int(row['HS'])
                                match_data['away_shots'] = int(row['AS'])
                            
                            if 'HST' in row and pd.notna(row['HST']):
                                match_data['home_shots_on_target'] = int(row['HST'])
                                match_data['away_shots_on_target'] = int(row['AST'])
                            
                            if 'HC' in row and pd.notna(row['HC']):
                                match_data['home_corners'] = int(row['HC'])
                                match_data['away_corners'] = int(row['AC'])
                            
                            if 'HY' in row and pd.notna(row['HY']):
                                match_data['home_yellow_cards'] = int(row['HY'])
                                match_data['away_yellow_cards'] = int(row['AY'])
                            
                            if 'HR' in row and pd.notna(row['HR']):
                                match_data['home_red_cards'] = int(row['HR'])
                                match_data['away_red_cards'] = int(row['AR'])
                            
                            self.all_matches.append(match_data)
                            matches_in_season += 1
                            
                        except Exception as e:
                            print(f"   ⚠️ Fout bij verwerken rij: {e}")
                            continue
                    
                    harvested_count += matches_in_season
                    print(f"   ✅ {matches_in_season} matches gevonden!")
                    
                elif response.status_code == 404:
                    print(f"   ⚠️ Data niet beschikbaar (404)")
                else:
                    print(f"   ❌ HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Fout: {e}")
            
            # Wees beleefd naar de server
            time.sleep(0.5)
        
        print(f"\n{'='*80}")
        print(f"✅ TOTAAL GEOOGST: {harvested_count} Eerste Divisie matches!")
        print(f"{'='*80}\n")
        
        return harvested_count
    
    def save_to_csv(self, filename=None):
        """Sla alle gescrapede data op in CSV formaat."""
        if not self.all_matches:
            print("❌ Geen data om op te slaan!")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"eerste_divisie_data_{timestamp}.csv"
        
        # Maak data directory als die niet bestaat
        os.makedirs('data', exist_ok=True)
        filepath = os.path.join('data', filename)
        
        # Converteer naar DataFrame en sla op
        df = pd.DataFrame(self.all_matches)
        df.to_csv(filepath, index=False)
        
        print(f"\n💾 DATA OPGESLAGEN!")
        print(f"   📁 Bestand: {filepath}")
        print(f"   📊 Matches: {len(self.all_matches)}")
        print(f"   📅 Periode: {df['season'].min()} tot {df['season'].max()}")
        print(f"   ⚽ Teams: {df['home_team'].nunique() + df['away_team'].nunique()} unieke teams")
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
        print(f"   Unieke teams: {df['home_team'].nunique()}")
        
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
        
        print(f"\n🎯 TOP 5 MEEST SCORENDE TEAMS (THUIS):")
        top_home = df.groupby('home_team')['home_goals'].mean().sort_values(ascending=False).head(5)
        for team, avg_goals in top_home.items():
            print(f"   {team}: {avg_goals:.2f} goals/wedstrijd")
        
        print(f"\n🛡️ TOP 5 BESTE VERDEDIGING (THUIS):")
        top_defense = df.groupby('home_team')['away_goals'].mean().sort_values().head(5)
        for team, avg_conceded in top_defense.items():
            print(f"   {team}: {avg_conceded:.2f} tegendoelpunten/wedstrijd")
        
        print("="*80 + "\n")


def main():
    """🚀 HOOFDPROGRAMMA - SCRAPE EERSTE DIVISIE DATA!"""
    
    print("\n" + "="*80)
    print("🇳🇱 EERSTE DIVISIE MEGA SCRAPER 🇳🇱")
    print("="*80)
    print("\n📋 Dit script scraped historische Eerste Divisie data voor AI training!")
    print("   Bron: Football-Data.co.uk (GRATIS en BETROUWBAAR)")
    print("   Doel: 5-10 seizoenen = 1000-2000 matches\n")
    
    input("Druk op ENTER om te starten...")
    
    # Initialiseer scraper
    scraper = EersteDivisieScraper()
    
    # Scrape Football-Data.co.uk (2015-2024 = 10 seizoenen!)
    print("\n🚀 STARTEN MET SCRAPEN...")
    scraper.scrape_football_data_uk(start_year=2015, end_year=2024)
    
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
    print("   1. Train een nieuw model met deze Eerste Divisie data")
    print("   2. Voeg deze teams toe aan de team_database.json")
    print("   3. Verbeter de PROFESSOR's Eerste Divisie accuracy!")
    print("\n💪 DE PROFESSOR WORDT NOG SLIMMER! 🧠\n")


if __name__ == "__main__":
    main()
