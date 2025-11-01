"""
UNIBET.NL PRODUCTION SCRAPER
Real-time odds scraping met Selenium + Kambi API extraction

Features:
- Chrome WebDriver automation
- JavaScript rendering
- Kambi API data extraction
- Retry logic
- Error handling
- CSV + JSON output
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import pandas as pd
from datetime import datetime
import time
import os
import re
import sys

class UnibetProductionScraper:
    """Production-ready Unibet.nl scraper"""
    
    def __init__(self, headless=True):
        self.url = "https://www.unibet.nl/betting/sports/filter/football/all/matches"
        self.headless = headless
        self.driver = None
        self.matches = []
        
    def setup_driver(self):
        """Setup Chrome driver met production settings"""
        print("\n[SETUP] Initializing Chrome WebDriver...")
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless=new")
            print("[SETUP] Running in headless mode")
        else:
            print("[SETUP] Running with visible browser")
        
        # Anti-detection
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Performance
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--log-level=3")
        
        # Prefs
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_setting_values.geolocation": 2,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Anti-detection script
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            print("[SETUP] Chrome driver ready!")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to setup driver: {str(e)}")
            return False
    
    def extract_kambi_data(self):
        """Extract data from Kambi API calls"""
        print("\n[EXTRACT] Looking for Kambi API data...")
        
        try:
            # Method 1: Check window.__INITIAL_STATE__ (common in React apps)
            initial_state = self.driver.execute_script("""
                return window.__INITIAL_STATE__ || 
                       window.__PRELOADED_STATE__ || 
                       window.initialData ||
                       null;
            """)
            
            if initial_state:
                print("[EXTRACT] Found window initial state!")
                self.parse_kambi_json(initial_state)
            
            # Method 2: Intercept XHR/Fetch responses
            performance_logs = self.driver.execute_script("""
                return window.performance.getEntries()
                    .filter(entry => entry.initiatorType === 'fetch' || entry.initiatorType === 'xmlhttprequest')
                    .map(entry => entry.name);
            """)
            
            kambi_urls = [url for url in performance_logs if 'kambi' in url.lower() or 'offering' in url.lower()]
            
            if kambi_urls:
                print(f"[EXTRACT] Found {len(kambi_urls)} Kambi API calls")
                for url in kambi_urls[:3]:
                    print(f"  - {url[:100]}")
                    self.fetch_api_data(url)
            
            # Method 3: Parse visible elements
            if not self.matches:
                print("[EXTRACT] Trying DOM element extraction...")
                self.parse_dom_elements()
            
        except Exception as e:
            print(f"[ERROR] Extract failed: {str(e)}")
    
    def fetch_api_data(self, url):
        """Fetch data from Kambi API URL"""
        try:
            import requests
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Referer': 'https://www.unibet.nl/'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"[API] Got JSON response: {len(str(data))} chars")
                self.parse_kambi_json(data)
                return True
                
        except Exception as e:
            print(f"[API] Failed to fetch: {str(e)[:100]}")
        
        return False
    
    def parse_kambi_json(self, data):
        """Parse Kambi JSON structure"""
        print("[PARSE] Parsing Kambi JSON data...")
        
        def recursive_search(obj, depth=0, max_depth=10):
            """Recursively search for events"""
            if depth > max_depth:
                return
            
            if isinstance(obj, dict):
                # Check if this is an event
                if 'event' in obj and isinstance(obj.get('event'), dict):
                    event_data = obj['event']
                    if 'homeName' in event_data and 'awayName' in event_data:
                        match = self.extract_match_from_event(obj)
                        if match and match not in self.matches:
                            self.matches.append(match)
                            print(f"  [+] {match['home_team']} vs {match['away_team']}")
                
                # Check alternative structures
                if 'homeName' in obj and 'awayName' in obj:
                    # Direct event structure
                    match = {
                        'home_team': obj.get('homeName', 'Unknown'),
                        'away_team': obj.get('awayName', 'Unknown'),
                        'league': obj.get('group', obj.get('groupName', 'Unknown')),
                        'start_time': obj.get('start', obj.get('startTime', 'Unknown')),
                    }
                    
                    # Look for odds in parent object
                    if match not in self.matches:
                        self.matches.append(match)
                
                # Recurse
                for value in obj.values():
                    recursive_search(value, depth + 1)
            
            elif isinstance(obj, list):
                for item in obj:
                    recursive_search(item, depth + 1)
        
        recursive_search(data)
        print(f"[PARSE] Total matches found: {len(self.matches)}")
    
    def extract_match_from_event(self, event_obj):
        """Extract match details from Kambi event object"""
        try:
            event = event_obj.get('event', {})
            
            match = {
                'bookmaker': 'Unibet',
                'home_team': event.get('homeName', 'Unknown'),
                'away_team': event.get('awayName', 'Unknown'),
                'league': event.get('group', event.get('groupName', 'Unknown')),
                'start_time': event.get('start', 'Unknown'),
                'event_id': event.get('id', ''),
                'home_odds': None,
                'draw_odds': None,
                'away_odds': None
            }
            
            # Extract odds from betOffers
            bet_offers = event_obj.get('betOffers', [])
            
            for offer in bet_offers:
                criterion = offer.get('criterion', {})
                
                # Look for 1X2 market
                if criterion.get('label') in ['1X2', 'Match Result', 'Wedstrijd Resultaat']:
                    outcomes = offer.get('outcomes', [])
                    
                    for outcome in outcomes:
                        label = outcome.get('label', '')
                        odds_value = outcome.get('odds')
                        
                        if odds_value:
                            # Kambi uses 1000-based odds (e.g., 2500 = 2.50)
                            decimal_odds = round(odds_value / 1000, 2)
                            
                            if label == '1' or 'home' in label.lower():
                                match['home_odds'] = decimal_odds
                            elif label == 'X' or 'draw' in label.lower() or 'gelijk' in label.lower():
                                match['draw_odds'] = decimal_odds
                            elif label == '2' or 'away' in label.lower():
                                match['away_odds'] = decimal_odds
            
            # Add scraped timestamp
            match['scraped_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            return match
            
        except Exception as e:
            print(f"[ERROR] Failed to extract match: {str(e)}")
            return None
    
    def parse_dom_elements(self):
        """Parse visible DOM elements as fallback"""
        print("[DOM] Parsing visible elements...")
        
        try:
            # Wait for content
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Try to find team name elements specifically
            team_selectors = [
                "span[class*='participant']",
                "div[class*='team']",
                "span[class*='team']",
                "[class*='competitor']"
            ]
            
            match_containers = []
            
            # First, find match container elements
            container_selectors = [
                "a[class*='eventRow']",
                "div[class*='eventRow']",
                "a[href*='/event/']",
                "[class*='KambiBC-event-item']"
            ]
            
            for selector in container_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"[DOM] Found {len(elements)} match containers: {selector}")
                    match_containers = elements[:50]  # Take first 50
                    break
            
            # Parse each match container
            for container in match_containers:
                try:
                    # Get the container's text and HTML
                    text = container.text.strip()
                    html = container.get_attribute('innerHTML')
                    
                    if not text or len(text) < 5:
                        continue
                    
                    lines = [l.strip() for l in text.split('\n') if l.strip()]
                    
                    # Filter out dates, times, and odds-only lines
                    team_lines = []
                    odds_values = []
                    match_time = None
                    
                    for line in lines:
                        # Check if it's a time
                        if re.match(r'^\d{1,2}:\d{2}$', line):
                            match_time = line
                        # Check if it's odds (decimal number)
                        elif re.match(r'^\d+\.\d{2}$', line):
                            try:
                                odds_values.append(float(line))
                            except:
                                pass
                        # Check if it's a date
                        elif any(month in line.lower() for month in ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december']):
                            continue
                        # Check if it's a league name (contains common keywords)
                        elif any(keyword in line.lower() for keyword in ['divisie', 'eredivisie', 'league', 'liga', 'cup', 'champions']):
                            continue
                        # Likely a team name
                        elif len(line) > 2 and not line.replace('.', '').isdigit():
                            team_lines.append(line)
                    
                    # Need at least 2 team names
                    if len(team_lines) >= 2:
                        match = {
                            'bookmaker': 'Unibet',
                            'home_team': team_lines[0],
                            'away_team': team_lines[1],
                            'league': 'Unibet NL',
                            'match_time': match_time if match_time else 'Unknown',
                            'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        # Add odds if we found exactly 3
                        if len(odds_values) >= 3:
                            match['home_odds'] = odds_values[0]
                            match['draw_odds'] = odds_values[1]
                            match['away_odds'] = odds_values[2]
                        
                        # Avoid duplicates
                        if not any(m.get('home_team') == match['home_team'] and 
                                  m.get('away_team') == match['away_team'] 
                                  for m in self.matches):
                            self.matches.append(match)
                            odds_str = f"{match.get('home_odds', '?')} - {match.get('draw_odds', '?')} - {match.get('away_odds', '?')}"
                            print(f"  [+] {match['home_team']} vs {match['away_team']} | {odds_str}")
                
                except Exception as e:
                    continue
        
        except Exception as e:
            print(f"[DOM] Parse failed: {str(e)}")
    
    def scrape(self):
        """Main scraping function"""
        print("\n" + "="*80)
        print("UNIBET.NL PRODUCTION SCRAPER")
        print("="*80)
        print(f"Start: {datetime.now()}")
        
        if not self.setup_driver():
            return []
        
        try:
            # Navigate to page
            print(f"\n[LOAD] Opening {self.url}")
            self.driver.get(self.url)
            
            # Wait for page load
            print("[LOAD] Waiting for JavaScript to load...")
            time.sleep(5)
            
            # Check page title
            title = self.driver.title
            print(f"[LOAD] Page title: {title}")
            
            # Extract data
            self.extract_kambi_data()
            
            # Save page source for debugging
            page_source_file = 'unibet_production_page.html'
            with open(page_source_file, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print(f"\n[DEBUG] Saved page source: {page_source_file}")
            
            # Results
            print(f"\n[RESULT] Total matches scraped: {len(self.matches)}")
            
            if self.matches:
                self.save_results()
            else:
                print("\n[WARNING] No matches found!")
                print("[INFO] Check unibet_production_page.html for debugging")
                print("[INFO] Page may require cookies/session or regional access")
            
            return self.matches
        
        except Exception as e:
            print(f"\n[ERROR] Scraping failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
        
        finally:
            if self.driver:
                self.driver.quit()
                print("\n[CLEANUP] Browser closed")
    
    def save_results(self):
        """Save scraped data"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Ensure data directory
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Save CSV
        df = pd.DataFrame(self.matches)
        csv_file = os.path.join(data_dir, f'unibet_live_{timestamp}.csv')
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"\n[SAVE] CSV: {csv_file}")
        
        # Save JSON
        json_file = os.path.join(data_dir, f'unibet_live_{timestamp}.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.matches, f, indent=2, ensure_ascii=False)
        print(f"[SAVE] JSON: {json_file}")
        
        # Print preview
        print("\n[PREVIEW] Sample matches:")
        print(df[['home_team', 'away_team', 'home_odds', 'draw_odds', 'away_odds']].head(10).to_string())
        
        # Statistics
        if 'league' in df.columns:
            print("\n[STATS] Matches by league:")
            print(df['league'].value_counts().to_string())


def main():
    """Run production scraper"""
    print("\n" + "="*80)
    print("UNIBET.NL LIVE SCRAPER - PRODUCTION MODE")
    print("="*80)
    
    # Check if running in proper environment
    try:
        from selenium import webdriver
        print("[CHECK] Selenium installed: OK")
    except ImportError:
        print("[ERROR] Selenium not installed!")
        print("[FIX] Run: pip install selenium webdriver-manager")
        return
    
    # Run scraper
    scraper = UnibetProductionScraper(headless=True)  # Set False to see browser
    matches = scraper.scrape()
    
    if matches:
        print("\n" + "="*80)
        print(f"SUCCESS! Scraped {len(matches)} matches from Unibet.nl")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("WARNING: No matches found")
        print("="*80)
        print("\nPossible reasons:")
        print("1. Regional restrictions (Unibet.nl only works from NL)")
        print("2. Website structure changed")
        print("3. Anti-scraping measures active")
        print("4. No matches currently available")
        print("\nCheck unibet_production_page.html for details")


if __name__ == '__main__':
    main()
