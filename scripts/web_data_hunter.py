"""
🦈 WEB DATA HUNTER - VREET ALLES VAN HET WEB!
=============================================

Scraped data:
1. Match scores (historical results)
2. Team injuries (blessures)
3. Yellow/Red cards
4. Team form & statistics
5. Head-to-head history

Sources tracked voor elk data point!
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os

class WebDataHunter:
    """Hunt and collect football data from multiple sources"""
    
    def __init__(self):
        self.collected_data = {
            'matches': [],
            'injuries': [],
            'cards': [],
            'team_stats': [],
            'sources': []
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def setup_selenium(self):
        """Setup Selenium browser"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    def scrape_flashscore_results(self, league='eredivisie', days_back=30):
        """
        Scrape recent results from Flashscore.nl
        Source: https://www.flashscore.nl/voetbal/
        """
        print("\n" + "="*80)
        print("⚽ HUNTING FLASHSCORE RESULTS")
        print("="*80)
        
        matches = []
        source = {
            'url': 'https://www.flashscore.nl/voetbal/',
            'type': 'match_results',
            'scraped_at': datetime.now().isoformat(),
            'league': league
        }
        
        try:
            driver = self.setup_selenium()
            
            # Flashscore URLs per league
            urls = {
                'eredivisie': 'https://www.flashscore.nl/voetbal/nederland/eredivisie/resultaten/',
                'premier-league': 'https://www.flashscore.nl/voetbal/engeland/premier-league/resultaten/',
                'bundesliga': 'https://www.flashscore.nl/voetbal/duitsland/bundesliga/resultaten/',
                'la-liga': 'https://www.flashscore.nl/voetbal/spanje/laliga/resultaten/'
            }
            
            url = urls.get(league.lower(), urls['eredivisie'])
            print(f"[HUNT] Target: {url}")
            
            driver.get(url)
            time.sleep(5)  # Wait for JS to load
            
            # Save page source for analysis
            page_source = driver.page_source
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = f'data/flashscore_{league}_{timestamp}.html'
            
            os.makedirs('data', exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(page_source)
            
            print(f"[SAVE] Page saved: {save_path}")
            source['html_file'] = save_path
            
            # Parse results
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Flashscore uses specific classes for matches
            match_elements = soup.find_all('div', class_=re.compile('event__match'))
            
            print(f"[FIND] Found {len(match_elements)} potential matches")
            
            for elem in match_elements[:50]:  # Process first 50
                try:
                    # Extract team names
                    home_elem = elem.find('div', class_=re.compile('event__participant.*home'))
                    away_elem = elem.find('div', class_=re.compile('event__participant.*away'))
                    
                    # Extract scores
                    score_elem = elem.find('div', class_=re.compile('event__score'))
                    
                    if home_elem and away_elem and score_elem:
                        home_team = home_elem.get_text(strip=True)
                        away_team = away_elem.get_text(strip=True)
                        score_text = score_elem.get_text(strip=True)
                        
                        # Parse score (e.g., "2 - 1")
                        score_match = re.search(r'(\d+)\s*-\s*(\d+)', score_text)
                        if score_match:
                            home_score = int(score_match.group(1))
                            away_score = int(score_match.group(2))
                            
                            match = {
                                'home_team': home_team,
                                'away_team': away_team,
                                'home_score': home_score,
                                'away_score': away_score,
                                'league': league,
                                'source': 'flashscore',
                                'scraped_at': datetime.now().isoformat()
                            }
                            
                            matches.append(match)
                            print(f"[MATCH] {home_team} {home_score}-{away_score} {away_team}")
                
                except Exception as e:
                    continue
            
            driver.quit()
            
            print(f"\n[SUCCESS] Scraped {len(matches)} matches from Flashscore")
            self.collected_data['matches'].extend(matches)
            self.collected_data['sources'].append(source)
            
        except Exception as e:
            print(f"[ERROR] Flashscore scraping failed: {e}")
        
        return matches
    
    def scrape_soccerway_results(self, league='eredivisie'):
        """
        Scrape results from Soccerway
        Source: https://nl.soccerway.com/
        """
        print("\n" + "="*80)
        print("⚽ HUNTING SOCCERWAY RESULTS")
        print("="*80)
        
        matches = []
        
        # Soccerway URLs
        urls = {
            'eredivisie': 'https://nl.soccerway.com/national/netherlands/eredivisie/20242025/regular-season/r78825/',
            'premier-league': 'https://nl.soccerway.com/national/england/premier-league/20242025/regular-season/r78830/'
        }
        
        url = urls.get(league.lower(), urls['eredivisie'])
        
        try:
            print(f"[HUNT] Target: {url}")
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Save HTML
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = f'data/soccerway_{league}_{timestamp}.html'
            
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"[SAVE] Page saved: {save_path}")
            
            # Parse match rows
            match_rows = soup.find_all('tr', class_=re.compile('match'))
            
            print(f"[FIND] Found {len(match_rows)} match rows")
            
            for row in match_rows[:30]:
                try:
                    teams = row.find_all('td', class_='team')
                    score = row.find('td', class_='score-time')
                    
                    if len(teams) == 2 and score:
                        home_team = teams[0].get_text(strip=True)
                        away_team = teams[1].get_text(strip=True)
                        score_text = score.get_text(strip=True)
                        
                        score_match = re.search(r'(\d+)\s*-\s*(\d+)', score_text)
                        if score_match:
                            match = {
                                'home_team': home_team,
                                'away_team': away_team,
                                'home_score': int(score_match.group(1)),
                                'away_score': int(score_match.group(2)),
                                'league': league,
                                'source': 'soccerway',
                                'scraped_at': datetime.now().isoformat()
                            }
                            
                            matches.append(match)
                            print(f"[MATCH] {home_team} {match['home_score']}-{match['away_score']} {away_team}")
                
                except Exception as e:
                    continue
            
            print(f"\n[SUCCESS] Scraped {len(matches)} matches from Soccerway")
            self.collected_data['matches'].extend(matches)
            
            self.collected_data['sources'].append({
                'url': url,
                'type': 'match_results',
                'scraped_at': datetime.now().isoformat(),
                'html_file': save_path
            })
            
        except Exception as e:
            print(f"[ERROR] Soccerway scraping failed: {e}")
        
        return matches
    
    def scrape_injury_data(self, team_name):
        """
        Scrape injury data from multiple sources
        Source: physioroom.com, transfermarkt.com
        """
        print("\n" + "="*80)
        print(f"🏥 HUNTING INJURY DATA: {team_name}")
        print("="*80)
        
        injuries = []
        
        # Try Physioroom (English teams)
        try:
            url = f"https://www.physioroom.com/news/english_premier_league/teams.php"
            print(f"[HUNT] Physioroom: {url}")
            
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Save HTML
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = f'data/injuries_physioroom_{timestamp}.html'
            
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Parse injury tables
            injury_tables = soup.find_all('table', class_='injury-table')
            
            print(f"[FIND] Found {len(injury_tables)} injury tables")
            
            for table in injury_tables:
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Skip header
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        player = cols[0].get_text(strip=True)
                        injury_type = cols[1].get_text(strip=True)
                        status = cols[2].get_text(strip=True)
                        
                        injury = {
                            'team': team_name,
                            'player': player,
                            'injury_type': injury_type,
                            'status': status,
                            'source': 'physioroom',
                            'scraped_at': datetime.now().isoformat()
                        }
                        
                        injuries.append(injury)
                        print(f"[INJURY] {player}: {injury_type} ({status})")
            
            self.collected_data['sources'].append({
                'url': url,
                'type': 'injuries',
                'scraped_at': datetime.now().isoformat(),
                'html_file': save_path
            })
            
        except Exception as e:
            print(f"[ERROR] Physioroom scraping failed: {e}")
        
        self.collected_data['injuries'].extend(injuries)
        return injuries
    
    def scrape_card_statistics(self, league='eredivisie'):
        """
        Scrape yellow/red card statistics
        Source: whoscored.com, flashscore.com
        """
        print("\n" + "="*80)
        print(f"🟨🟥 HUNTING CARD STATISTICS: {league}")
        print("="*80)
        
        card_stats = []
        
        try:
            # Use Flashscore for card stats
            driver = self.setup_selenium()
            
            urls = {
                'eredivisie': 'https://www.flashscore.nl/voetbal/nederland/eredivisie/statistieken/',
                'premier-league': 'https://www.flashscore.nl/voetbal/engeland/premier-league/statistieken/'
            }
            
            url = urls.get(league.lower(), urls['eredivisie'])
            print(f"[HUNT] Target: {url}")
            
            driver.get(url)
            time.sleep(5)
            
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Save HTML
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = f'data/cards_{league}_{timestamp}.html'
            
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(page_source)
            
            print(f"[SAVE] Page saved: {save_path}")
            
            # Parse card statistics (structure varies)
            stat_rows = soup.find_all('div', class_=re.compile('stat.*row'))
            
            print(f"[FIND] Found {len(stat_rows)} stat rows")
            
            for row in stat_rows[:20]:
                try:
                    team_elem = row.find('div', class_=re.compile('team'))
                    yellow_elem = row.find('div', class_=re.compile('yellow'))
                    red_elem = row.find('div', class_=re.compile('red'))
                    
                    if team_elem:
                        team_name = team_elem.get_text(strip=True)
                        yellow_cards = yellow_elem.get_text(strip=True) if yellow_elem else '0'
                        red_cards = red_elem.get_text(strip=True) if red_elem else '0'
                        
                        stat = {
                            'team': team_name,
                            'yellow_cards': yellow_cards,
                            'red_cards': red_cards,
                            'league': league,
                            'source': 'flashscore',
                            'scraped_at': datetime.now().isoformat()
                        }
                        
                        card_stats.append(stat)
                        print(f"[CARDS] {team_name}: {yellow_cards} yellow, {red_cards} red")
                
                except Exception as e:
                    continue
            
            driver.quit()
            
            self.collected_data['sources'].append({
                'url': url,
                'type': 'card_statistics',
                'scraped_at': datetime.now().isoformat(),
                'html_file': save_path
            })
            
        except Exception as e:
            print(f"[ERROR] Card statistics scraping failed: {e}")
        
        self.collected_data['cards'].extend(card_stats)
        return card_stats
    
    def scrape_team_form(self, team_name, league='eredivisie'):
        """
        Scrape team form (last 5 matches)
        """
        print("\n" + "="*80)
        print(f"📊 HUNTING TEAM FORM: {team_name}")
        print("="*80)
        
        form_data = {
            'team': team_name,
            'league': league,
            'last_5_results': [],
            'goals_scored': 0,
            'goals_conceded': 0,
            'points': 0,
            'source': 'aggregated',
            'scraped_at': datetime.now().isoformat()
        }
        
        # Extract from already scraped matches
        team_matches = [
            m for m in self.collected_data['matches']
            if m['home_team'] == team_name or m['away_team'] == team_name
        ]
        
        for match in team_matches[-5:]:  # Last 5
            if match['home_team'] == team_name:
                scored = match['home_score']
                conceded = match['away_score']
                result = 'W' if scored > conceded else ('D' if scored == conceded else 'L')
            else:
                scored = match['away_score']
                conceded = match['home_score']
                result = 'W' if scored > conceded else ('D' if scored == conceded else 'L')
            
            form_data['last_5_results'].append(result)
            form_data['goals_scored'] += scored
            form_data['goals_conceded'] += conceded
            form_data['points'] += (3 if result == 'W' else (1 if result == 'D' else 0))
        
        print(f"[FORM] Last 5: {' '.join(form_data['last_5_results'])}")
        print(f"[FORM] Goals: {form_data['goals_scored']}-{form_data['goals_conceded']}")
        print(f"[FORM] Points: {form_data['points']}/15")
        
        self.collected_data['team_stats'].append(form_data)
        return form_data
    
    def save_all_data(self):
        """Save all collected data to files"""
        print("\n" + "="*80)
        print("💾 SAVING ALL COLLECTED DATA")
        print("="*80)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save matches
        if self.collected_data['matches']:
            df_matches = pd.DataFrame(self.collected_data['matches'])
            csv_file = f'data/web_matches_{timestamp}.csv'
            df_matches.to_csv(csv_file, index=False)
            print(f"[SAVE] Matches: {csv_file} ({len(df_matches)} rows)")
        
        # Save injuries
        if self.collected_data['injuries']:
            df_injuries = pd.DataFrame(self.collected_data['injuries'])
            csv_file = f'data/web_injuries_{timestamp}.csv'
            df_injuries.to_csv(csv_file, index=False)
            print(f"[SAVE] Injuries: {csv_file} ({len(df_injuries)} rows)")
        
        # Save cards
        if self.collected_data['cards']:
            df_cards = pd.DataFrame(self.collected_data['cards'])
            csv_file = f'data/web_cards_{timestamp}.csv'
            df_cards.to_csv(csv_file, index=False)
            print(f"[SAVE] Cards: {csv_file} ({len(df_cards)} rows)")
        
        # Save team stats
        if self.collected_data['team_stats']:
            df_stats = pd.DataFrame(self.collected_data['team_stats'])
            csv_file = f'data/web_team_stats_{timestamp}.csv'
            df_stats.to_csv(csv_file, index=False)
            print(f"[SAVE] Team stats: {csv_file} ({len(df_stats)} rows)")
        
        # Save all data as JSON (includes sources!)
        json_file = f'data/web_data_complete_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, indent=2, ensure_ascii=False)
        print(f"[SAVE] Complete dataset: {json_file}")
        
        # Print statistics
        print("\n" + "="*80)
        print("📊 DATA COLLECTION SUMMARY")
        print("="*80)
        print(f"Matches collected:      {len(self.collected_data['matches'])}")
        print(f"Injuries collected:     {len(self.collected_data['injuries'])}")
        print(f"Card stats collected:   {len(self.collected_data['cards'])}")
        print(f"Team stats collected:   {len(self.collected_data['team_stats'])}")
        print(f"Sources tracked:        {len(self.collected_data['sources'])}")
        print("="*80)
        
        return {
            'timestamp': timestamp,
            'matches': len(self.collected_data['matches']),
            'injuries': len(self.collected_data['injuries']),
            'cards': len(self.collected_data['cards']),
            'team_stats': len(self.collected_data['team_stats']),
            'sources': len(self.collected_data['sources'])
        }


def run_full_hunt():
    """Run complete data hunting operation"""
    print("\n" + "="*80)
    print("🦈 WEB DATA HUNTER - STARTING FULL HUNT!")
    print("="*80)
    print(f"Time: {datetime.now()}")
    print("="*80 + "\n")
    
    hunter = WebDataHunter()
    
    # Hunt Eredivisie data
    print("\n🇳🇱 HUNTING EREDIVISIE DATA...")
    hunter.scrape_flashscore_results('eredivisie')
    hunter.scrape_soccerway_results('eredivisie')
    hunter.scrape_card_statistics('eredivisie')
    
    # Hunt Premier League data
    print("\n🏴󠁧󠁢󠁥󠁮󠁧󠁿 HUNTING PREMIER LEAGUE DATA...")
    hunter.scrape_flashscore_results('premier-league')
    hunter.scrape_soccerway_results('premier-league')
    hunter.scrape_card_statistics('premier-league')
    
    # Hunt injury data (sample teams)
    print("\n🏥 HUNTING INJURY DATA...")
    hunter.scrape_injury_data('Manchester City')
    hunter.scrape_injury_data('Arsenal')
    hunter.scrape_injury_data('Liverpool')
    
    # Calculate team forms from collected data
    print("\n📊 CALCULATING TEAM FORMS...")
    unique_teams = list(set(
        [m['home_team'] for m in hunter.collected_data['matches']] +
        [m['away_team'] for m in hunter.collected_data['matches']]
    ))
    
    for team in unique_teams[:10]:  # First 10 teams
        hunter.scrape_team_form(team)
    
    # Save everything
    summary = hunter.save_all_data()
    
    print("\n" + "="*80)
    print("✅ HUNT COMPLETE!")
    print("="*80)
    print(f"Total data points collected: {summary['matches'] + summary['injuries'] + summary['cards'] + summary['team_stats']}")
    print(f"All sources tracked and saved!")
    print("="*80 + "\n")
    
    return hunter


if __name__ == '__main__':
    hunter = run_full_hunt()
