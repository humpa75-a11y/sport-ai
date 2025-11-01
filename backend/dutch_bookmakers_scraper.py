"""
🎯 DUTCH BOOKMAKERS SCRAPER - SELENIUM EDITION 🎯

Haalt LIVE odds van Nederlandse bookmakers met browser automation:
- Toto
- Jack's Casino  
- Holland Casino
- Unibet

SNIPER MODE: Accuraat, robuust, en ontwijkt anti-scraping.
"""

import json
import time
import random
from datetime import datetime
from typing import List, Dict

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class DutchBookmakersScraper:
    """
    Professionele scraper voor Nederlandse bookmakers met Selenium.
    """
    
    def __init__(self):
        self.driver = None
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        self.results = {
            'timestamp': None,
            'bookmakers': {},
            'matches': []
        }

    def _setup_driver(self) -> webdriver.Chrome:
        """Zet de Selenium WebDriver op met anti-detectie opties."""
        print("   - Initializing Chrome WebDriver...")
        options = ChromeOptions()
        options.add_argument(f"user-agent={random.choice(self.user_agents)}")
        options.add_argument("--headless")  # Draai op de achtergrond
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3") # Minder logs
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # Installeer of gebruik gecachte Chrome driver
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print("   - WebDriver ready.")
        return driver

    def _random_delay(self, min_sec: float = 2.0, max_sec: float = 5.0):
        """Wacht een willekeurige tijd om menselijk gedrag te simuleren."""
        time.sleep(random.uniform(min_sec, max_sec))

    def scrape_toto(self) -> List[Dict]:
        """
        🎲 TOTO SCRAPER (SELENIUM)
        
        Haalt odds van toto.nl/wedden/voetbal met een geautomatiseerde browser.
        """
        print("\n🎲 SCRAPING TOTO (SELENIUM)...")
        matches = []
        self.driver = self._setup_driver()
        
        try:
            url = "https://www.toto.nl/wedden/voetbal"
            print(f"   - Navigating to {url}")
            self.driver.get(url)
            
            # Wacht tot de wedstrijden geladen zijn. We zoeken naar een container.
            # Dit is de cruciale stap: wachten op de JavaScript om te renderen.
            # De class 'event-list-item-v2' lijkt een goede kandidaat voor een wedstrijd.
            wait = WebDriverWait(self.driver, 20) # Wacht max 20 seconden
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "event-list-item-v2__event-info")))
            print("   - Wedstrijden container gevonden. Pagina is geladen.")
            
            self._random_delay(3, 5) # Extra wachttijd voor alle data

            # Haal de pagina source op NADAT JavaScript is uitgevoerd
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')
            
            # Zoek alle wedstrijd-elementen
            match_elements = soup.find_all('div', class_=lambda c: c and 'event-list-item-v2' in c)
            print(f"   - {len(match_elements)} potentiële wedstrijd-elementen gevonden.")

            for element in match_elements:
                try:
                    # Extract team names
                    team_elements = element.find_all('div', class_="event-list-item-v2__competitor-name")
                    if len(team_elements) < 2:
                        continue
                        
                    home_team = team_elements[0].text.strip()
                    away_team = team_elements[1].text.strip()

                    # Extract odds (1X2)
                    odds_elements = element.find_all('span', class_="outcome-v2__odds")
                    if len(odds_elements) < 3:
                        continue

                    home_odd = float(odds_elements[0].text.strip())
                    draw_odd = float(odds_elements[1].text.strip())
                    away_odd = float(odds_elements[2].text.strip())
                    
                    matches.append({
                        'home_team': home_team,
                        'away_team': away_team,
                        'bookmaker': 'Toto',
                        'odds': {
                            'home_win': home_odd,
                            'draw': draw_odd,
                            'away_win': away_odd
                        },
                        'url': url
                    })
                except Exception as e:
                    # print(f"   ⚠️ Error parsing Toto match: {e}") # Te veel logs
                    continue
            
            print(f"   ✅ Toto: {len(matches)} wedstrijden succesvol gescraped.")
            
        except Exception as e:
            print(f"   ❌ Toto scraping failed: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                print("   - WebDriver closed.")
        
        return matches

    def scrape_jacks_casino(self) -> List[Dict]:
        """
        🎰 JACK'S CASINO SCRAPER (Placeholder)
        """
        print("\n🎰 SCRAPING JACK'S CASINO... (Not Implemented)")
        self._random_delay(1,2)
        return []
    
    def scrape_holland_casino(self) -> List[Dict]:
        """
        🎲 HOLLAND CASINO SCRAPER (Placeholder)
        """
        print("\n🎲 SCRAPING HOLLAND CASINO... (Not Implemented)")
        self._random_delay(1,2)
        return []
    
    def scrape_unibet(self) -> List[Dict]:
        """
        🎯 UNIBET SCRAPER (Placeholder)
        """
        print("\n🎯 SCRAPING UNIBET... (Not Implemented)")
        self._random_delay(1,2)
        return []
    
    def scrape_all_bookmakers(self) -> Dict:
        """
        🎯 MASTER SCRAPER
        
        Scrape alle bookmakers en combineer de data.
        """
        print("\n" + "="*80)
        print("🎯 DUTCH BOOKMAKERS SCRAPER - SNIPER MODE (SELENIUM)")
        print("="*80)
        
        self.results['timestamp'] = datetime.now().isoformat()
        
        # Scrape elk platform
        toto_matches = self.scrape_toto()
        jacks_matches = self.scrape_jacks_casino()
        holland_matches = self.scrape_holland_casino()
        unibet_matches = self.scrape_unibet()
        
        # Combineer alle matches
        all_matches = toto_matches + jacks_matches + holland_matches + unibet_matches
        
        # Organiseer per wedstrijd
        matches_dict = {}
        for match in all_matches:
            key = f"{match['home_team']} vs {match['away_team']}"
            if key not in matches_dict:
                matches_dict[key] = {
                    'home_team': match['home_team'],
                    'away_team': match['away_team'],
                    'bookmakers': {}
                }
            
            matches_dict[key]['bookmakers'][match['bookmaker']] = match['odds']
        
        self.results['matches'] = list(matches_dict.values())
        self.results['bookmakers'] = {
            'Toto': len(toto_matches),
            'Jacks_Casino': len(jacks_matches),
            'Holland_Casino': len(holland_matches),
            'Unibet': len(unibet_matches)
        }
        
        print("\n" + "="*80)
        print(f"✅ SCRAPING COMPLETE!")
        print(f"   Totaal: {len(all_matches)} odds van {len(matches_dict)} unieke wedstrijden")
        print(f"   Toto: {len(toto_matches)}")
        print(f"   Jack's: {len(jacks_matches)}")
        print(f"   Holland Casino: {len(holland_matches)}")
        print(f"   Unibet: {len(unibet_matches)}")
        print("="*80)
        
        return self.results
    
    def save_results(self, filename: str = 'dutch_bookmakers_odds.json'):
        """Sla scraping resultaten op."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Resultaten opgeslagen in: {filename}")
    
    def get_best_odds(self) -> List[Dict]:
        """
        🎯 BEST ODDS FINDER
        
        Vind de beste odds voor elke wedstrijd across alle bookmakers.
        Perfect voor arbitrage opportunities!
        """
        best_odds = []
        
        for match in self.results['matches']:
            if not match['bookmakers']:
                continue
            
            best_home = {'bookmaker': None, 'odd': 0}
            best_draw = {'bookmaker': None, 'odd': 0}
            best_away = {'bookmaker': None, 'odd': 0}
            
            for bookmaker, odds in match['bookmakers'].items():
                if odds.get('home_win', 0) > best_home['odd']:
                    best_home = {'bookmaker': bookmaker, 'odd': odds['home_win']}
                if odds.get('draw', 0) > best_draw['odd']:
                    best_draw = {'bookmaker': bookmaker, 'odd': odds['draw']}
                if odds.get('away_win', 0) > best_away['odd']:
                    best_away = {'bookmaker': bookmaker, 'odd': odds['away_win']}
            
            best_odds.append({
                'match': f"{match['home_team']} vs {match['away_team']}",
                'best_odds': {
                    'home_win': best_home,
                    'draw': best_draw,
                    'away_win': best_away
                },
                'arbitrage_possible': self._check_arbitrage(best_home['odd'], best_draw['odd'], best_away['odd'])
            })
        
        return best_odds
    
    def _check_arbitrage(self, home_odd: float, draw_odd: float, away_odd: float) -> bool:
        """Check of er een arbitrage opportunity is (sure bet)."""
        if home_odd == 0 or draw_odd == 0 or away_odd == 0:
            return False
        
        # Bereken implied probability
        implied_prob = (1/home_odd) + (1/draw_odd) + (1/away_odd)
        
        # Als < 1.0, is er arbitrage mogelijk!
        return implied_prob < 1.0


def main():
    """Test de scraper."""
    scraper = DutchBookmakersScraper()
    
    # Scrape alle bookmakers
    results = scraper.scrape_all_bookmakers()
    
    # Sla op
    scraper.save_results('data/dutch_bookmakers_odds.json')
    
    # Vind beste odds
    best_odds = scraper.get_best_odds()
    
    print("\n🎯 BESTE ODDS PER WEDSTRIJD:")
    for match in best_odds[:5]:  # Top 5
        print(f"\n{match['match']}")
        print(f"   Home: {match['best_odds']['home_win']['odd']} ({match['best_odds']['home_win']['bookmaker']})")
        print(f"   Draw: {match['best_odds']['draw']['odd']} ({match['best_odds']['draw']['bookmaker']})")
        print(f"   Away: {match['best_odds']['away_win']['odd']} ({match['best_odds']['away_win']['bookmaker']})")
        if match['arbitrage_possible']:
            print(f"   🔥 ARBITRAGE OPPORTUNITY!")


if __name__ == '__main__':
    main()
