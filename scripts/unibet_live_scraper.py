"""
UNIBET.NL LIVE SCRAPER
Scrapes real football odds from Unibet Nederland

URL: https://www.unibet.nl/betting/sports/filter/football/all/matches
Legal: Public odds data only
"""

import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime
import time
import re

class UnibetScraper:
    """Scrapes live odds from Unibet.nl"""
    
    def __init__(self):
        self.base_url = "https://www.unibet.nl"
        self.matches_url = "https://www.unibet.nl/betting/sports/filter/football/all/matches"
        
        # Headers to look like a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'nl-NL,nl;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def fetch_page(self):
        """Fetch Unibet football matches page"""
        print(f"\nFetching: {self.matches_url}")
        
        try:
            response = self.session.get(
                self.matches_url,
                timeout=15,
                allow_redirects=True
            )
            
            print(f"Status: {response.status_code}")
            print(f"Content length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"ERROR: Status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"ERROR fetching page: {str(e)}")
            return None
    
    def try_api_endpoint(self):
        """Try to find Unibet's API endpoint"""
        print("\nTrying to find API endpoint...")
        
        # Common Unibet API patterns
        api_endpoints = [
            "https://www.unibet.nl/sportsbook-feeds/views/filter/football/all/matches",
            "https://eu-offering-api.kambicdn.com/offering/v2018/ub-nl/listView/football.json",
            "https://eu-offering-api.kambicdn.com/offering/v2018/ub-nl/betoffer/event/live/open.json",
        ]
        
        for api_url in api_endpoints:
            try:
                print(f"\nTrying: {api_url}")
                response = self.session.get(api_url, timeout=10)
                
                if response.status_code == 200:
                    print(f"SUCCESS! Found API: {api_url}")
                    data = response.json()
                    print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'List response'}")
                    return data, api_url
                else:
                    print(f"Status: {response.status_code}")
                    
            except Exception as e:
                print(f"Failed: {str(e)[:100]}")
        
        return None, None
    
    def parse_html(self, html_content):
        """Parse HTML for match data"""
        print("\nParsing HTML content...")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Save HTML for inspection
        with open('unibet_page.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("Saved HTML to: unibet_page.html")
        
        # Look for common patterns
        matches = []
        
        # Try different selectors
        selectors = [
            {'class': 'event'},
            {'class': 'match'},
            {'class': 'KambiBC-event-item'},
            {'class': 'event-wrapper'},
            {'data-testid': 'event-item'}
        ]
        
        for selector in selectors:
            elements = soup.find_all('div', selector)
            if elements:
                print(f"Found {len(elements)} elements with selector: {selector}")
                
                for elem in elements[:3]:  # Show first 3
                    print(f"\nElement text: {elem.get_text()[:200]}")
        
        # Look for script tags with data
        scripts = soup.find_all('script')
        print(f"\nFound {len(scripts)} script tags")
        
        for script in scripts:
            if script.string and ('event' in script.string.lower() or 'match' in script.string.lower()):
                script_text = script.string[:500]
                print(f"\nScript contains match data: {script_text}")
        
        return matches
    
    def extract_from_api(self, api_data):
        """Extract matches from API response"""
        print("\nExtracting matches from API data...")
        print(f"API data type: {type(api_data)}")
        print(f"API data keys: {list(api_data.keys()) if isinstance(api_data, dict) else 'Not a dict'}")
        
        # Save full API response for inspection
        with open('unibet_api_response.json', 'w', encoding='utf-8') as f:
            json.dump(api_data, f, indent=2, ensure_ascii=False)
        print("Saved full API response to: unibet_api_response.json")
        
        matches = []
        
        try:
            # Inspect the structure
            if isinstance(api_data, dict):
                # Look for nested data structures
                for key in ['layout', 'data', 'events', 'competitions', 'groups']:
                    if key in api_data:
                        print(f"\nFound key: {key}")
                        value = api_data[key]
                        print(f"Type: {type(value)}")
                        
                        if isinstance(value, dict):
                            print(f"Sub-keys: {list(value.keys())[:10]}")
                        elif isinstance(value, list):
                            print(f"List length: {len(value)}")
                            if value:
                                print(f"First item keys: {list(value[0].keys()) if isinstance(value[0], dict) else 'Not a dict'}")
            
            # Try to find events in layout structure (common in Unibet/Kambi)
            if 'layout' in api_data:
                layout = api_data['layout']
                print(f"\nLayout structure: {list(layout.keys()) if isinstance(layout, dict) else type(layout)}")
                
                # Recursively search for events
                def find_events(obj, depth=0):
                    """Recursively find event data"""
                    if depth > 5:  # Prevent infinite recursion
                        return []
                    
                    found = []
                    
                    if isinstance(obj, dict):
                        # Check if this looks like an event
                        if 'event' in obj or ('home' in str(obj).lower() and 'away' in str(obj).lower()):
                            found.append(obj)
                        
                        # Recurse into values
                        for value in obj.values():
                            found.extend(find_events(value, depth + 1))
                    
                    elif isinstance(obj, list):
                        for item in obj:
                            found.extend(find_events(item, depth + 1))
                    
                    return found
                
                potential_events = find_events(layout)
                print(f"Found {len(potential_events)} potential event objects")
                
                if potential_events:
                    print("\nFirst event sample:")
                    print(json.dumps(potential_events[0], indent=2)[:500])
            
            # Standard Kambi structure
            if 'events' in api_data:
                events = api_data['events']
                print(f"\nProcessing {len(events)} events from 'events' key")
                matches = self._parse_kambi_events(events)
            
            print(f"\nExtracted {len(matches)} matches with odds")
            return matches
            
        except Exception as e:
            print(f"ERROR extracting from API: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def _parse_kambi_events(self, events):
        """Parse Kambi-style events"""
        matches = []
        
        for event in events[:50]:  # Process first 50
            try:
                match = {
                    'home_team': event.get('event', {}).get('homeName', 'Unknown'),
                    'away_team': event.get('event', {}).get('awayName', 'Unknown'),
                    'start_time': event.get('event', {}).get('start', 'Unknown'),
                    'league': event.get('event', {}).get('group', 'Unknown'),
                    'home_odds': None,
                    'draw_odds': None,
                    'away_odds': None
                }
                
                # Extract odds
                betoffers = event.get('betOffers', [])
                for betoffer in betoffers:
                    if betoffer.get('criterion', {}).get('label') == '1X2':
                        outcomes = betoffer.get('outcomes', [])
                        for outcome in outcomes:
                            label = outcome.get('label')
                            odds = outcome.get('odds')
                            
                            if odds:
                                odds_decimal = odds / 1000  # Kambi uses 1000-based odds
                                
                                if label == '1' or 'home' in label.lower():
                                    match['home_odds'] = odds_decimal
                                elif label == 'X' or 'draw' in label.lower():
                                    match['draw_odds'] = odds_decimal
                                elif label == '2' or 'away' in label.lower():
                                    match['away_odds'] = odds_decimal
                
                if match['home_odds']:  # Only add if we have odds
                    matches.append(match)
                    print(f"  {match['home_team']} vs {match['away_team']} | {match['home_odds']}-{match['draw_odds']}-{match['away_odds']}")
            
            except Exception as e:
                continue
        
        return matches
    
    def scrape_all(self):
        """Main scraping function"""
        print("\n" + "="*80)
        print("UNIBET.NL LIVE SCRAPER")
        print("="*80)
        print(f"Start: {datetime.now()}")
        
        all_matches = []
        
        # Try 1: API endpoint (fastest and most reliable)
        api_data, api_url = self.try_api_endpoint()
        if api_data:
            matches = self.extract_from_api(api_data)
            all_matches.extend(matches)
        
        # Try 2: HTML scraping (fallback)
        if not all_matches:
            print("\nAPI failed, trying HTML scraping...")
            html = self.fetch_page()
            
            if html:
                matches = self.parse_html(html)
                all_matches.extend(matches)
        
        # Save results
        if all_matches:
            self.save_results(all_matches)
        else:
            print("\nWARNING: No matches found!")
            print("\nPlease check:")
            print("1. Website structure may have changed")
            print("2. Need to inspect unibet_page.html")
            print("3. May need browser automation (Selenium/Playwright)")
        
        print("\n" + "="*80)
        print(f"COMPLETE - Found {len(all_matches)} matches")
        print("="*80)
        
        return all_matches
    
    def save_results(self, matches):
        """Save scraped data"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save as CSV
        df = pd.DataFrame(matches)
        csv_file = f'../data/unibet_odds_{timestamp}.csv'
        df.to_csv(csv_file, index=False)
        print(f"\nSaved CSV: {csv_file}")
        
        # Save as JSON
        json_file = f'../data/unibet_odds_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(matches, f, indent=2, ensure_ascii=False)
        print(f"Saved JSON: {json_file}")
        
        # Print preview
        print("\nPREVIEW:")
        print(df.head(10).to_string())


if __name__ == '__main__':
    scraper = UnibetScraper()
    matches = scraper.scrape_all()
    
    if matches:
        print(f"\nSUCCESS! Scraped {len(matches)} matches from Unibet.nl")
    else:
        print("\nNeed to inspect HTML structure.")
        print("Check unibet_page.html for clues.")
        print("\nAlternative: Use Selenium for JavaScript-heavy sites")
