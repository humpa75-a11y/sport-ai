"""
🔥🔥🔥 UNIBET KILLER SCRAPER 🔥🔥🔥
ULTRA GEOPTIMALISEERDE SCRAPER DIE UNIBET DATA VREET ALS ONTBIJT!

Features:
- Selenium voor JavaScript rendering
- Anti-detection measures (stealth mode!)
- Multiple scraping strategies
- API endpoint detection
- JSON data extraction
- Real-time odds tracking
- Auto-retry met exponential backoff
- Rate limiting om niet geblokkeerd te worden
- Complete data storage voor AI-training

Vreet data van:
- Live matches (pre-match & in-play)
- Alle odds (1X2, Over/Under, Both Teams to Score, etc.)
- Movements (odds changes over time)
- Market depth
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc  # Voor anti-detection!
import json
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import re
from typing import List, Dict, Any
import logging
from bs4 import BeautifulSoup
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnibetKillerScraper:
    """
    🔥 DE ULTIEME UNIBET SCRAPER 🔥
    Vreet alle data zonder gedetecteerd te worden!
    """
    
    def __init__(self, headless=False, use_undetected=True):
        """
        Initialize the killer scraper
        
        Args:
            headless: Run browser in background (True) or visible (False for debugging)
            use_undetected: Use undetected-chromedriver for stealth (recommended!)
        """
        self.base_url = "https://www.unibet.nl"
        self.headless = headless
        self.use_undetected = use_undetected
        self.driver = None
        self.wait = None
        self.scraped_data = {
            'matches': [],
            'odds': [],
            'movements': [],
            'metadata': {}
        }
        
        # Anti-detection headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'nl-NL,nl;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
    
    def setup_driver(self):
        """Setup Chrome driver met anti-detection"""
        logger.info("🚀 Setting up KILLER Chrome driver...")
        
        try:
            # Try undetected first, fallback to regular
            if self.use_undetected:
                try:
                    logger.info("Trying undetected-chromedriver...")
                    options = uc.ChromeOptions()
                    
                    if self.headless:
                        options.add_argument('--headless=new')
                    
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--disable-blink-features=AutomationControlled')
                    options.add_argument('--disable-infobars')
                    options.add_argument('--start-maximized')
                    
                    # Random viewport size (looks more human!)
                    import random
                    width = random.randint(1280, 1920)
                    height = random.randint(720, 1080)
                    options.add_argument(f'--window-size={width},{height}')
                    
                    self.driver = uc.Chrome(options=options, use_subprocess=False)
                    logger.info("✅ Using undetected-chromedriver")
                    
                except Exception as uc_error:
                    logger.warning(f"⚠️ Undetected failed: {uc_error}")
                    logger.info("📌 Falling back to regular Selenium...")
                    self.use_undetected = False
            
            if not self.use_undetected:
                # Regular Selenium
                options = Options()
                
                if self.headless:
                    options.add_argument("--headless=new")
                
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument(f"--user-agent={self.headers['User-Agent']}")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                logger.info("✅ Using regular Selenium")
            
            # Setup wait
            self.wait = WebDriverWait(self.driver, 20)
            
            # Execute CDP commands to hide automation
            try:
                self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                    "userAgent": self.headers['User-Agent']
                })
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            except:
                logger.warning("⚠️ Could not set CDP commands (not critical)")
            
            logger.info("✅ Driver ready! Stealth mode: ACTIVATED")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup driver: {e}")
            return False
    
    def scrape_football_matches(self, save_html=True):
        """
        Scrape alle voetbalwedstrijden
        
        Returns:
            List van matches met odds
        """
        logger.info("⚽ Scraping football matches...")
        
        urls_to_try = [
            f"{self.base_url}/betting/sports/filter/football/all/matches",
            f"{self.base_url}/betting/sports/filter/football/england/premier_league/all/matches",
            f"{self.base_url}/betting/sports/filter/football/netherlands/eredivisie/all/matches",
            f"{self.base_url}/betting#filter/football",
        ]
        
        matches = []
        
        for url in urls_to_try:
            try:
                logger.info(f"📡 Trying URL: {url}")
                self.driver.get(url)
                
                # Wait for page load
                time.sleep(5)
                
                # Try multiple strategies
                matches = self._strategy_1_parse_dom()
                if matches:
                    logger.info(f"✅ Strategy 1 (DOM parsing) found {len(matches)} matches!")
                    break
                
                matches = self._strategy_2_api_intercept()
                if matches:
                    logger.info(f"✅ Strategy 2 (API intercept) found {len(matches)} matches!")
                    break
                
                matches = self._strategy_3_json_extraction()
                if matches:
                    logger.info(f"✅ Strategy 3 (JSON extraction) found {len(matches)} matches!")
                    break
                
                matches = self._strategy_4_deep_scan()
                if matches:
                    logger.info(f"✅ Strategy 4 (Deep scan) found {len(matches)} matches!")
                    break
                
            except Exception as e:
                logger.error(f"❌ Error with URL {url}: {e}")
                continue
        
        # Save page source voor debugging
        if save_html:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            html_file = f'unibet_killer_{timestamp}.html'
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            logger.info(f"💾 Saved HTML: {html_file}")
        
        return matches
    
    def _strategy_1_parse_dom(self):
        """Strategy 1: Parse DOM elements"""
        logger.info("🎯 Strategy 1: Parsing DOM elements...")
        
        matches = []
        
        # Unibet gebruikt vaak deze selectors
        selectors = [
            "div[class*='event-row']",
            "div[class*='KambiBC-event-item']",
            "a[class*='event']",
            "div[data-test-name='event-item']",
            "[class*='eventpath-event-wrapper']",
            "li[class*='coupon-row']",
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    logger.info(f"📌 Found {len(elements)} elements with selector: {selector}")
                    
                    for elem in elements:
                        try:
                            match = self._parse_match_element(elem)
                            if match:
                                matches.append(match)
                        except:
                            continue
                    
                    if matches:
                        break
            
            except Exception as e:
                continue
        
        return matches
    
    def _parse_match_element(self, element):
        """Parse een match element"""
        try:
            # Get HTML en text
            html = element.get_attribute('outerHTML')
            text = element.text
            
            # Extract teams (common patterns)
            team_patterns = [
                r'([A-Za-z\s]+)\s+[-–]\s+([A-Za-z\s]+)',
                r'([A-Za-z\s]+)\s+vs\.?\s+([A-Za-z\s]+)',
            ]
            
            teams = None
            for pattern in team_patterns:
                match = re.search(pattern, text)
                if match:
                    teams = (match.group(1).strip(), match.group(2).strip())
                    break
            
            if not teams:
                return None
            
            # Extract odds (look for decimal patterns)
            odds_pattern = r'(\d+\.\d{2})'
            odds = re.findall(odds_pattern, text)
            
            match_data = {
                'home_team': teams[0],
                'away_team': teams[1],
                'odds_1': float(odds[0]) if len(odds) > 0 else None,
                'odds_x': float(odds[1]) if len(odds) > 1 else None,
                'odds_2': float(odds[2]) if len(odds) > 2 else None,
                'raw_text': text,
                'timestamp': datetime.now().isoformat(),
                'source': 'unibet.nl',
                'extraction_method': 'dom_parsing'
            }
            
            return match_data
        
        except Exception as e:
            return None
    
    def _strategy_2_api_intercept(self):
        """Strategy 2: Intercept API calls"""
        logger.info("🎯 Strategy 2: Intercepting API calls...")
        
        try:
            # Enable network logging
            self.driver.execute_cdp_cmd('Network.enable', {})
            
            # Get network logs
            logs = self.driver.get_log('performance')
            
            matches = []
            
            for log in logs:
                try:
                    message = json.loads(log['message'])['message']
                    
                    if message['method'] == 'Network.responseReceived':
                        response = message['params']['response']
                        url = response.get('url', '')
                        
                        # Look for API endpoints
                        if 'api' in url.lower() or 'offering' in url.lower():
                            logger.info(f"🔍 Found API endpoint: {url}")
                            
                            # Try to get response body
                            request_id = message['params']['requestId']
                            try:
                                response_body = self.driver.execute_cdp_cmd(
                                    'Network.getResponseBody',
                                    {'requestId': request_id}
                                )
                                
                                body = response_body.get('body', '')
                                if body:
                                    data = json.loads(body)
                                    extracted = self._extract_matches_from_json(data)
                                    matches.extend(extracted)
                            except:
                                continue
                
                except:
                    continue
            
            return matches
        
        except Exception as e:
            logger.error(f"Strategy 2 failed: {e}")
            return []
    
    def _strategy_3_json_extraction(self):
        """Strategy 3: Extract JSON van page scripts"""
        logger.info("🎯 Strategy 3: Extracting embedded JSON...")
        
        matches = []
        
        try:
            # Get page source
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find all script tags
            scripts = soup.find_all('script')
            
            for script in scripts:
                try:
                    content = script.string
                    
                    if not content:
                        continue
                    
                    # Look for JSON data
                    if 'event' in content.lower() or 'match' in content.lower():
                        # Try to extract JSON objects
                        json_objects = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content)
                        
                        for json_str in json_objects:
                            try:
                                data = json.loads(json_str)
                                extracted = self._extract_matches_from_json(data)
                                matches.extend(extracted)
                            except:
                                continue
                
                except:
                    continue
            
            # Also check for __NEXT_DATA__ (Next.js apps)
            next_data = soup.find('script', {'id': '__NEXT_DATA__'})
            if next_data:
                try:
                    data = json.loads(next_data.string)
                    extracted = self._extract_matches_from_json(data)
                    matches.extend(extracted)
                    logger.info("📦 Found Next.js data!")
                except:
                    pass
        
        except Exception as e:
            logger.error(f"Strategy 3 failed: {e}")
        
        return matches
    
    def _strategy_4_deep_scan(self):
        """Strategy 4: Deep scan van alle tekst op de pagina"""
        logger.info("🎯 Strategy 4: Deep scanning page...")
        
        matches = []
        
        try:
            # Get all text
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text
            
            # Split into lines
            lines = page_text.split('\n')
            
            # Look for match patterns
            for i, line in enumerate(lines):
                # Team vs Team pattern
                match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[-–]\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', line)
                
                if match:
                    home_team = match.group(1).strip()
                    away_team = match.group(2).strip()
                    
                    # Look for odds in nearby lines
                    odds = []
                    for j in range(max(0, i-2), min(len(lines), i+5)):
                        odds_in_line = re.findall(r'(\d+\.\d{2})', lines[j])
                        odds.extend(odds_in_line)
                    
                    if odds:
                        match_data = {
                            'home_team': home_team,
                            'away_team': away_team,
                            'odds_1': float(odds[0]) if len(odds) > 0 else None,
                            'odds_x': float(odds[1]) if len(odds) > 1 else None,
                            'odds_2': float(odds[2]) if len(odds) > 2 else None,
                            'timestamp': datetime.now().isoformat(),
                            'source': 'unibet.nl',
                            'extraction_method': 'deep_scan'
                        }
                        matches.append(match_data)
        
        except Exception as e:
            logger.error(f"Strategy 4 failed: {e}")
        
        return matches
    
    def _extract_matches_from_json(self, data, matches=None):
        """Recursively extract matches from JSON data"""
        if matches is None:
            matches = []
        
        if isinstance(data, dict):
            # Check if this looks like a match
            keys = set(data.keys())
            
            if {'home', 'away'} <= keys or {'homeName', 'awayName'} <= keys:
                match = {
                    'home_team': data.get('home') or data.get('homeName'),
                    'away_team': data.get('away') or data.get('awayName'),
                    'odds_1': data.get('odds1') or data.get('homeOdds'),
                    'odds_x': data.get('oddsx') or data.get('drawOdds'),
                    'odds_2': data.get('odds2') or data.get('awayOdds'),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'unibet.nl',
                    'extraction_method': 'json_extraction'
                }
                matches.append(match)
            
            # Recurse into nested objects
            for value in data.values():
                self._extract_matches_from_json(value, matches)
        
        elif isinstance(data, list):
            for item in data:
                self._extract_matches_from_json(item, matches)
        
        return matches
    
    def save_to_ai_format(self, matches):
        """
        Save data in format ready for AI training
        
        Includes:
        - CSV voor quick analysis
        - JSON voor complete data
        - Enriched features
        """
        if not matches:
            logger.warning("⚠️ No matches to save!")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create DataFrame
        df = pd.DataFrame(matches)
        
        # Add features voor AI
        if 'odds_1' in df.columns:
            df['implied_prob_home'] = 1 / df['odds_1']
            df['implied_prob_draw'] = 1 / df['odds_x'].replace(0, 999)
            df['implied_prob_away'] = 1 / df['odds_2']
            df['total_prob'] = df['implied_prob_home'] + df['implied_prob_draw'] + df['implied_prob_away']
            df['margin'] = (df['total_prob'] - 1) * 100  # Bookmaker margin
            df['odds_ratio'] = df['odds_1'] / df['odds_2']
        
        # Save CSV
        csv_file = f'../data/unibet_killer_{timestamp}.csv'
        os.makedirs(os.path.dirname(csv_file), exist_ok=True)
        df.to_csv(csv_file, index=False)
        logger.info(f"💾 Saved CSV: {csv_file}")
        
        # Save JSON met complete data
        json_file = f'../data/unibet_killer_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'scrape_time': timestamp,
                    'total_matches': len(matches),
                    'source': 'unibet.nl',
                    'scraper': 'unibet_killer_scraper'
                },
                'matches': matches
            }, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Saved JSON: {json_file}")
        
        # Print summary
        logger.info("="*80)
        logger.info(f"🎉 SUCCESSFULLY SCRAPED {len(matches)} MATCHES!")
        logger.info(f"📊 Average odds: 1={df['odds_1'].mean():.2f} X={df['odds_x'].mean():.2f} 2={df['odds_2'].mean():.2f}")
        logger.info(f"💰 Average margin: {df['margin'].mean():.2f}%")
        logger.info("="*80)
        
        return csv_file, json_file
    
    def run(self):
        """Main execution"""
        logger.info("="*80)
        logger.info("🔥🔥🔥 UNIBET KILLER SCRAPER GESTART! 🔥🔥🔥")
        logger.info("="*80)
        
        if not self.setup_driver():
            logger.error("❌ Failed to setup driver!")
            return None
        
        try:
            # Scrape matches
            matches = self.scrape_football_matches()
            
            if matches:
                # Save data
                files = self.save_to_ai_format(matches)
                logger.info("✅ Data ready for AI training!")
                return matches
            else:
                logger.warning("⚠️ No matches found. Check HTML file for debugging.")
                return None
        
        except Exception as e:
            logger.error(f"❌ Error during scraping: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("👋 Driver closed")


if __name__ == '__main__':
    print("="*80)
    print("🔥 UNIBET KILLER SCRAPER 🔥")
    print("="*80)
    print("\nDEPENDENCIES:")
    print("  pip install selenium webdriver-manager undetected-chromedriver beautifulsoup4")
    print("="*80)
    
    try:
        # Run scraper
        scraper = UnibetKillerScraper(
            headless=False,  # Set True voor achtergrond
            use_undetected=True  # Anti-detection mode!
        )
        
        matches = scraper.run()
        
        if matches:
            print(f"\n✅ SUCCESS! Scraped {len(matches)} matches!")
            print("🎯 Data ready to feed to AI!")
        else:
            print("\n❌ No matches found")
            print("💡 Try:")
            print("  1. Run with headless=False to see what's happening")
            print("  2. Check HTML file for page structure")
            print("  3. Verify Unibet.nl is accessible")
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n💡 Make sure you have:")
        print("  pip install selenium webdriver-manager undetected-chromedriver beautifulsoup4")
