"""
UNIBET.NL WORKING DEMO SCRAPER
Returns realistic sample data based on Eredivisie + European matches

NOTE: Real scraping needs Selenium/Playwright because Unibet uses heavy JavaScript
This demo gives you working data structure NOW while we can implement real scraping later
"""

import pandas as pd
import json
from datetime import datetime, timedelta
import random
import os

class UnibetDemoScraper:
    """Demo scraper with realistic Eredivisie + European football data"""
    
    def __init__(self):
        self.eredivisie_teams = [
            'Ajax', 'PSV', 'Feyenoord', 'AZ Alkmaar', 'FC Twente',
            'FC Utrecht', 'SC Heerenveen', 'Go Ahead Eagles', 'Fortuna Sittard',
            'NEC Nijmegen', 'FC Groningen', 'PEC Zwolle', 'Sparta Rotterdam',
            'RKC Waalwijk', 'Almere City', 'Heracles Almelo', 'Excelsior', 'FC Volendam'
        ]
        
        self.european_matches = [
            ('Manchester City', 'Arsenal', 'Premier League'),
            ('Liverpool', 'Chelsea', 'Premier League'),
            ('Barcelona', 'Real Madrid', 'La Liga'),
            ('Bayern Munich', 'Borussia Dortmund', 'Bundesliga'),
            ('Inter Milan', 'AC Milan', 'Serie A'),
            ('Paris Saint-Germain', 'Marseille', 'Ligue 1'),
            ('Atletico Madrid', 'Sevilla', 'La Liga'),
            ('Juventus', 'Napoli', 'Serie A'),
            ('Tottenham', 'Manchester United', 'Premier League'),
            ('RB Leipzig', 'Bayer Leverkusen', 'Bundesliga')
        ]
    
    def generate_realistic_odds(self, is_home_favorite=True):
        """Generate realistic 1X2 odds"""
        if is_home_favorite:
            home = round(random.uniform(1.50, 2.20), 2)
            draw = round(random.uniform(3.20, 3.80), 2)
            away = round(random.uniform(3.50, 6.00), 2)
        else:
            home = round(random.uniform(3.00, 5.50), 2)
            draw = round(random.uniform(3.10, 3.70), 2)
            away = round(random.uniform(1.60, 2.30), 2)
        
        return home, draw, away
    
    def scrape_eredivisie(self):
        """Generate Eredivisie matches"""
        print("\nScraping Eredivisie matches...")
        
        matches = []
        num_matches = random.randint(6, 9)  # Typical matchday
        
        teams_available = self.eredivisie_teams.copy()
        random.shuffle(teams_available)
        
        for i in range(0, num_matches * 2, 2):
            if i + 1 < len(teams_available):
                home = teams_available[i]
                away = teams_available[i + 1]
                
                # Determine favorite (top teams)
                is_home_favorite = home in ['Ajax', 'PSV', 'Feyenoord', 'AZ Alkmaar']
                home_odds, draw_odds, away_odds = self.generate_realistic_odds(is_home_favorite)
                
                # Generate match time (weekend afternoon/evening)
                days_ahead = random.randint(0, 2)
                hour = random.choice([14, 16, 18, 20])
                minute = random.choice([0, 30, 45])
                match_time = datetime.now() + timedelta(days=days_ahead, hours=hour-datetime.now().hour, minutes=minute-datetime.now().minute)
                
                match = {
                    'bookmaker': 'Unibet',
                    'league': 'Eredivisie',
                    'home_team': home,
                    'away_team': away,
                    'home_odds': home_odds,
                    'draw_odds': draw_odds,
                    'away_odds': away_odds,
                    'match_time': match_time.strftime('%Y-%m-%d %H:%M'),
                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                matches.append(match)
                print(f"  {home} vs {away} | {home_odds} - {draw_odds} - {away_odds}")
        
        return matches
    
    def scrape_european(self):
        """Generate top European matches"""
        print("\nScraping European top matches...")
        
        matches = []
        selected = random.sample(self.european_matches, k=random.randint(5, 8))
        
        for home, away, league in selected:
            # Big matches = close odds
            home_odds = round(random.uniform(2.10, 3.20), 2)
            draw_odds = round(random.uniform(3.00, 3.60), 2)
            away_odds = round(random.uniform(2.20, 3.50), 2)
            
            # Generate match time
            days_ahead = random.randint(0, 3)
            hour = random.choice([18, 20, 21])
            minute = random.choice([0, 30, 45])
            match_time = datetime.now() + timedelta(days=days_ahead, hours=hour-datetime.now().hour, minutes=minute-datetime.now().minute)
            
            match = {
                'bookmaker': 'Unibet',
                'league': league,
                'home_team': home,
                'away_team': away,
                'home_odds': home_odds,
                'draw_odds': draw_odds,
                'away_odds': away_odds,
                'match_time': match_time.strftime('%Y-%m-%d %H:%M'),
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            matches.append(match)
            print(f"  {home} vs {away} | {home_odds} - {draw_odds} - {away_odds}")
        
        return matches
    
    def scrape_all(self):
        """Scrape everything"""
        print("\n" + "="*80)
        print("UNIBET.NL DEMO SCRAPER (Realistic Sample Data)")
        print("="*80)
        print(f"Start: {datetime.now()}")
        print("\nNOTE: This uses realistic sample data.")
        print("For REAL scraping, use Selenium/Playwright (JavaScript required)")
        
        all_matches = []
        
        # Eredivisie
        eredivisie = self.scrape_eredivisie()
        all_matches.extend(eredivisie)
        
        # European
        european = self.scrape_european()
        all_matches.extend(european)
        
        print(f"\n" + "="*80)
        print(f"TOTAL: {len(all_matches)} matches scraped")
        print("="*80)
        
        return all_matches
    
    def save_results(self, matches):
        """Save to CSV and JSON"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Ensure data directory exists
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Save CSV
        df = pd.DataFrame(matches)
        csv_file = os.path.join(data_dir, f'unibet_odds_{timestamp}.csv')
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\nSaved CSV: {csv_file}")
        
        # Save JSON
        json_file = os.path.join(data_dir, f'unibet_odds_{timestamp}.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(matches, f, indent=2, ensure_ascii=False)
        print(f"Saved JSON: {json_file}")
        
        # Print summary
        print("\nSUMMARY:")
        print(df.groupby('league').size())
        
        print("\nSAMPLE MATCHES:")
        print(df[['league', 'home_team', 'away_team', 'home_odds', 'draw_odds', 'away_odds']].head(10).to_string())
        
        return csv_file, json_file
    
    def run(self):
        """Main run function"""
        matches = self.scrape_all()
        
        if matches:
            csv_file, json_file = self.save_results(matches)
            
            print("\n" + "="*80)
            print("SUCCESS!")
            print("="*80)
            print(f"\nFiles saved:")
            print(f"  CSV:  {csv_file}")
            print(f"  JSON: {json_file}")
            print(f"\nTotal matches: {len(matches)}")
            print("\nREAL SCRAPING:")
            print("  For live Unibet data, install: pip install selenium webdriver-manager")
            print("  Then use: unibet_selenium_scraper.py")
            print("="*80)
            
            return matches
        
        return []


if __name__ == '__main__':
    scraper = UnibetDemoScraper()
    matches = scraper.run()
