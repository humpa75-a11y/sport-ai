# Gebruik de 'wire' versie van de standaard Chrome driver
from seleniumwire.webdriver import Chrome as WireChrome
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
import json

class DutchBookmakersScraper:
    def __init__(self):
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """
        Stelt een PURE selenium-wire driver in, zonder undetected-chromedriver.
        De hoop is dat de proxy-configuratie alleen voldoende is.
        """
        print("🚀 [PURIST] Initializing PURE selenium-wire driver...")

        options = ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--user-agent={self.get_random_user_agent()}')
        port = 8080
        options.add_argument(f'--proxy-server=127.0.0.1:{port}')
        options.add_argument('--ignore-certificate-errors')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        seleniumwire_options = {
            'addr': '127.0.0.1',
            'port': port,
            'disable_encoding': True,
            'ws_capture_enabled': True,
        }
        
        try:
            self.driver = WireChrome(
                options=options,
                seleniumwire_options=seleniumwire_options
            )
            
            def interceptor(request):
                pass
            self.driver.ws_request_interceptor = interceptor
            
            print(f"   - Proxy luistert op: 127.0.0.1:{port}")
            self.driver.set_window_size(1920, 1080)
            print("✅ [PURIST] Driver geïnitialiseerd. WebSocket-jacht kan beginnen.")
        except Exception as e:
            print(f"❌ Fout bij het initialiseren van de 'PURIST' driver: {e}")
            raise

    def get_random_user_agent(self):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        ]
        return random.choice(user_agents)

    def scrape_toto(self):
        """
        FASE 22: De Backend-Ingang.
        We hebben via introspectie het 'backend' attribuut gevonden. We proberen nu
        de websocket-berichten te lezen via `self.driver.backend.storage`.
        """
        url = "https://sport.toto.nl/wedden/11/voetbal/wedstrijden"
        print(f"🌐 [DE BACKEND-INGANG] Navigeren naar: {url}")
        
        try:
            # Zorg ervoor dat we met een schone lei beginnen
            del self.driver.requests
            
            self.driver.get(url)

            print("⏳ Wachten voor 25 seconden om de WebSocket-berichten te vangen...")
            time.sleep(25)

            print("\n--- DE BACKEND-INGANG RAPPORT ---")
            # De cruciale aanpassing: we kijken in het .backend.storage object!
            messages = self.driver.backend.storage.ws_messages

            if not messages:
                print("❌ Geen WebSocket-berichten onderschept via de backend. De pagina is mogelijk geblokkeerd.")
                self.driver.save_screenshot('backend_failed.png')
                return pd.DataFrame()

            print(f"✅ {len(messages)} WebSocket-berichten gevonden via de backend!")
            
            log_filename = "BACKEND_WEBSOCKET_MESSAGES.json"
            all_message_data = []
            potential_data_messages = []

            for i, message in enumerate(messages):
                if message.direction == 'inbound':
                    try:
                        content = message.content
                        if isinstance(content, str) and content.endswith(''):
                            cleaned_content = content.strip().rstrip('')
                            json_objects = cleaned_content.split('')
                            
                            for json_str in json_objects:
                                if not json_str: continue
                                data = json.loads(json_str)
                                all_message_data.append({'id': i, 'direction': 'inbound', 'data': data})
                                
                                if 'arguments' in data and isinstance(data['arguments'], list) and len(data['arguments']) > 0:
                                    arg = data['arguments'][0]
                                    if isinstance(arg, list) and len(arg) > 0 and isinstance(arg[0], dict) and 'homeTeam' in arg[0]:
                                        print(f"   🎯 GOUD! Data gevonden in bericht {i}! Aantal events: {len(arg)}")
                                        potential_data_messages.append(arg)
                    except (json.JSONDecodeError, TypeError, AttributeError):
                        continue
            
            with open(log_filename, 'w', encoding='utf-8') as f:
                json.dump(all_message_data, f, indent=2)
            print(f"   💾 Alle inbound JSON-berichten opgeslagen in '{log_filename}'.")

            if not potential_data_messages:
                print("⚠️ Wel WebSocket-berichten, maar geen met de verwachte 'events'-structuur.")
                return pd.DataFrame()

            full_event_list = []
            for msg_content in potential_data_messages:
                full_event_list.extend(msg_content)
            
            print(f"   -> Totaal {len(full_event_list)} events verzameld uit {len(potential_data_messages)} berichten.")
            
            return self.parse_websocket_data(full_event_list)

        except Exception as e:
            print(f"❌ Toto 'De Backend-Ingang' catastrofaal mislukt: {e}")
            import traceback
            traceback.print_exc()
            self.driver.save_screenshot('toto_backend_error.png')
            return pd.DataFrame()

    def parse_websocket_data(self, events_data):
        print("\n🛠️  Bezig met het parsen van de WebSocket-data...")
        all_matches = []
        seen_matches = set()

        if not isinstance(events_data, list):
            print("⚠️ De aangeleverde data is geen lijst. Kan niet parsen.")
            return pd.DataFrame()

        for event in events_data:
            if isinstance(event, dict) and event.get('sport', {}).get('name') == 'Voetbal' and event.get('homeTeam') and event.get('awayTeam'):
                home_team = event.get('homeTeam', {}).get('name', 'N/A')
                away_team = event.get('awayTeam', {}).get('name', 'N/A')
                
                match_id = f"{home_team} vs {away_team}"
                if match_id in seen_matches:
                    continue
                seen_matches.add(match_id)

                odds = ['N/A', 'N/A', 'N/A']
                main_bet_offer = event.get('mainBetOffer')
                if main_bet_offer and 'outcomes' in main_bet_offer:
                    outcomes = sorted(main_bet_offer['outcomes'], key=lambda x: x.get('type', ''))
                    if len(outcomes) == 3:
                        odds = [o.get('odds', 0) / 1000.0 for o in outcomes]

                all_matches.append({
                    'Bookmaker': 'Toto',
                    'Home Team': home_team,
                    'Away Team': away_team,
                    'Odds 1': odds[0],
                    'Odds X': odds[1],
                    'Odds 2': odds[2],
                })

        if not all_matches:
            print("⚠️ Events gevonden in WebSocket, maar geen unieke voetbalwedstrijden kunnen parsen.")
            return pd.DataFrame()

        print(f"🎉 {len(all_matches)} unieke wedstrijden succesvol geëxtraheerd uit de WebSocket-stroom!")
        return pd.DataFrame(all_matches)

    def close_driver(self):
        if self.driver:
            self.driver.quit()
            print("✅ Driver afgesloten.")

def main():
    scraper = None
    try:
        scraper = DutchBookmakersScraper()
        
        # Voer 'De Backend-Ingang' fase uit voor Toto
        toto_odds = scraper.scrape_toto()
        if not toto_odds.empty:
            print("\n--- Toto Odds (via De Backend-Ingang) ---")
            print(toto_odds.head())
            toto_odds.to_csv("toto_odds.csv", index=False)
            print("\n💾 Toto odds opgeslagen in toto_odds.csv")
        else:
            print("\n⚠️ Geen odds ontvangen van de Toto 'De Backend-Ingang' scraper.")

    except Exception as e:
        print(f"❌ Een onverwachte fout is opgetreden in main: {e}")
    finally:
        if scraper:
            scraper.close_driver()

if __name__ == "__main__":
    main()
