"""
UNIBET.NL SELENIUM SCRAPER
Uses Selenium to scrape JavaScript-rendered odds

Requires: pip install selenium webdriver-manager
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

class UnibetSeleniumScraper:
    """Scrapes Unibet.nl using Selenium"""
    
    def __init__(self, headless=True):
        self.url = "https://www.unibet.nl/betting/sports/filter/football/all/matches"
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver"""
        print("\nSetting up Chrome driver...")
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("Chrome driver ready!")
            return True
        except Exception as e:
            print(f"ERROR setting up driver: {str(e)}")
            return False
    
    def scrape_matches(self):
        """Scrape all matches"""
        print(f"\nNavigating to: {self.url}")
        
        try:
            self.driver.get(self.url)
            print("Page loaded, waiting for content...")
            
            # Wait for matches to load
            time.sleep(5)  # Give time for JavaScript to load
            
            # Try to find match elements
            selectors = [
                "//div[contains(@class, 'KambiBC-event-item')]",
                "//div[contains(@data-testid, 'event')]",
                "//div[contains(@class, 'event-wrapper')]",
                "//div[contains(@class, 'match')]",
                "//a[contains(@class, 'event')]"
            ]
            
            matches = []
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        print(f"Found {len(elements)} elements with selector: {selector}")
                        
                        for i, elem in enumerate(elements[:10]):  # Process first 10
                            try:
                                text = elem.text
                                html = elem.get_attribute('outerHTML')[:200]
                                
                                print(f"\nElement {i+1}:")
                                print(f"Text: {text[:100]}")
                                print(f"HTML: {html}")
                                
                                # Try to extract match info
                                match = self.parse_element(elem)
                                if match:
                                    matches.append(match)
                            
                            except Exception as e:
                                continue
                        
                        break  # Stop if we found matches
                
                except Exception as e:
                    print(f"Selector failed: {selector}")
                    continue
            
            # Save page source for inspection
            with open('unibet_selenium_page.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            print("\nSaved page source to: unibet_selenium_page.html")
            
            # Try to extract JSON data from page
            script_matches = self.extract_from_scripts()
            if script_matches:
                matches.extend(script_matches)
            
            return matches
        
        except Exception as e:
            print(f"ERROR scraping: {str(e)}")
            return []
    
    def parse_element(self, element):
        """Parse match element"""
        try:
            # Get all text
            full_text = element.text
            
            # Try to split into components
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            
            if len(lines) >= 3:
                # Common pattern: Home Team, Away Team, Odds...
                match = {
                    'raw_text': full_text,
                    'lines': lines,
                    'html': element.get_attribute('outerHTML')[:300]
                }
                return match
        
        except Exception as e:
            return None
    
    def extract_from_scripts(self):
        """Extract match data from script tags"""
        print("\nSearching for JSON data in page scripts...")
        
        try:
            # Look for embedded JSON data
            scripts = self.driver.find_elements(By.TAG_NAME, 'script')
            
            for script in scripts:
                try:
                    content = script.get_attribute('innerHTML')
                    
                    if content and ('event' in content or 'match' in content.lower()):
                        # Look for JSON patterns
                        if '{' in content and '}' in content:
                            # Try to extract JSON
                            start = content.find('{')
                            end = content.rfind('}') + 1
                            
                            if start != -1 and end > start:
                                json_str = content[start:end]
                                
                                try:
                                    data = json.loads(json_str)
                                    print("Found JSON data in script!")
                                    
                                    # Save for inspection
                                    with open('unibet_embedded_data.json', 'w', encoding='utf-8') as f:
                                        json.dump(data, f, indent=2)
                                    
                                    return self.parse_json_data(data)
                                
                                except:
                                    continue
                
                except Exception as e:
                    continue
        
        except Exception as e:
            print(f"Error extracting scripts: {str(e)}")
        
        return []
    
    def parse_json_data(self, data):
        """Parse JSON data for matches"""
        matches = []
        
        # Recursive search for match-like objects
        def search_dict(obj, depth=0):
            if depth > 10:
                return
            
            if isinstance(obj, dict):
                # Look for match indicators
                if 'homeName' in obj or 'awayName' in obj:
                    matches.append(obj)
                
                for value in obj.values():
                    search_dict(value, depth + 1)
            
            elif isinstance(obj, list):
                for item in obj:
                    search_dict(item, depth + 1)
        
        search_dict(data)
        return matches
    
    def run(self):
        """Main run function"""
        print("\n" + "="*80)
        print("UNIBET.NL SELENIUM SCRAPER")
        print("="*80)
        print(f"Start: {datetime.now()}")
        
        if not self.setup_driver():
            print("Failed to setup driver!")
            return []
        
        try:
            matches = self.scrape_matches()
            
            if matches:
                self.save_results(matches)
            else:
                print("\nNo matches found.")
                print("Check unibet_selenium_page.html for debugging")
            
            return matches
        
        finally:
            if self.driver:
                self.driver.quit()
                print("\nDriver closed")
    
    def save_results(self, matches):
        """Save results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save JSON
        json_file = f'../data/unibet_selenium_{timestamp}.json'
        os.makedirs(os.path.dirname(json_file), exist_ok=True)
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(matches, f, indent=2, ensure_ascii=False)
        
        print(f"\nSaved: {json_file}")
        print(f"Found {len(matches)} matches")


if __name__ == '__main__':
    print("="*80)
    print("NOTE: This requires Chrome and selenium packages")
    print("Install with: pip install selenium webdriver-manager")
    print("="*80)
    
    try:
        scraper = UnibetSeleniumScraper(headless=False)  # Set False to see browser
        matches = scraper.run()
        
        if matches:
            print(f"\nSUCCESS! Found {len(matches)} matches")
        else:
            print("\nCheck HTML files for debugging")
    
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("\nMake sure you have installed:")
        print("  pip install selenium webdriver-manager")
