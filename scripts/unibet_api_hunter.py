"""
🎯 UNIBET API HUNTER 🎯
Direct hun API aanspreken - VEEL sneller en efficiënter dan scraping!

Strategy:
1. Find their API endpoints (usually kambi API for odds data)
2. Intercept their requests
3. Parse JSON responses
4. Store for AI training

VEEL BETER dan scraping JavaScript pagina's!
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time
import os
from typing import List, Dict, Any
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnibetAPIHunter:
    """
    🎯 Unibet API Hunter
    Vindt en gebruikt hun backend API endpoints voor odds data
    """
    
    def __init__(self):
        """Initialize API hunter"""
        # Unibet gebruikt Kambi API (UPDATED - CORRECT DOMAIN!)
        self.kambi_api_base = "https://eu1.offering-api.kambicdn.com/offering/v2018/ubnl"
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'nl-NL,nl;q=0.9,en;q=0.8',
            'Referer': 'https://www.unibet.nl/',
            'Origin': 'https://www.unibet.nl',
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_football_events(self, league_filter="all"):
        """
        Haal voetbal evenementen op
        
        Args:
            league_filter: "premier_league", "eredivisie", "all", etc.
        
        Returns:
            List van matches
        """
        logger.info(f"🔍 Fetching football events (filter: {league_filter})...")
        
        # Use simpler group API
        url = f"{self.kambi_api_base}/group.json"
        params = {
            'lang': 'nl_NL',
            'market': 'NL',
            'client_id': '2',
            'channel_id': '1',
            'includeLive': 'true'
        }
        
        logger.info(f"📡 Trying: {url}")
        
        all_matches = []
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Got response! Status: {response.status_code}")
                
                # Parse matches
                matches = self._parse_kambi_response(data)
                
                if matches:
                    logger.info(f"🎉 Found {len(matches)} matches!")
                    all_matches.extend(matches)
                
                # Save raw response voor debugging
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                raw_file = f'../data/unibet_raw_group_{timestamp}.json'
                os.makedirs(os.path.dirname(raw_file), exist_ok=True)
                
                with open(raw_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logger.info(f"💾 Saved raw: {raw_file}")
            
            else:
                logger.warning(f"⚠️ Status {response.status_code}: {url}")
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
        
        return all_matches
    
    def _parse_kambi_response(self, data):
        """Parse Kambi API response voor matches"""
        matches = []
        
        try:
            # Kambi structuur: events in events array
            if 'events' in data:
                events = data['events']
                logger.info(f"📦 Processing {len(events)} events...")
                
                for event in events:
                    try:
                        match = self._extract_match_from_event(event)
                        if match:
                            matches.append(match)
                    except Exception as e:
                        logger.debug(f"Could not parse event: {e}")
                        continue
            
            # Also check groups
            if 'group' in data:
                group = data['group']
                if 'events' in group:
                    for event in group['events']:
                        try:
                            match = self._extract_match_from_event(event)
                            if match:
                                matches.append(match)
                        except:
                            continue
        
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
        
        return matches
    
    def _extract_match_from_event(self, event):
        """Extract match data from event"""
        try:
            # Event naam (bijv. "Manchester City - Arsenal")
            event_name = event.get('event', {}).get('name', '')
            
            if ' - ' in event_name:
                teams = event_name.split(' - ')
                home_team = teams[0].strip()
                away_team = teams[1].strip()
            else:
                return None
            
            # Odds extractie
            betoffers = event.get('betOffers', [])
            
            odds_1 = None
            odds_x = None
            odds_2 = None
            
            # Zoek naar "Match Result" / "1X2" market
            for betoffer in betoffers:
                criterion = betoffer.get('criterion', {}).get('label', '').lower()
                
                if 'match result' in criterion or '1x2' in criterion or 'wedstrijdresultaat' in criterion:
                    outcomes = betoffer.get('outcomes', [])
                    
                    for outcome in outcomes:
                        label = outcome.get('label', '').lower()
                        odds = outcome.get('odds')
                        
                        if odds:
                            odds_decimal = odds / 1000  # Kambi gebruikt odds * 1000
                            
                            if '1' in label or home_team.lower() in label:
                                odds_1 = odds_decimal
                            elif 'x' in label or 'draw' in label or 'gelijk' in label:
                                odds_x = odds_decimal
                            elif '2' in label or away_team.lower() in label:
                                odds_2 = odds_decimal
            
            # Match start tijd
            start_time = event.get('event', {}).get('start')
            
            # Match data
            match = {
                'home_team': home_team,
                'away_team': away_team,
                'odds_1': odds_1,
                'odds_x': odds_x,
                'odds_2': odds_2,
                'start_time': start_time,
                'event_id': event.get('event', {}).get('id'),
                'league': event.get('event', {}).get('path', [{}])[0].get('name') if event.get('event', {}).get('path') else None,
                'timestamp': datetime.now().isoformat(),
                'source': 'unibet.nl (Kambi API)',
                'extraction_method': 'api_direct'
            }
            
            # Only return if we have odds
            if odds_1 and odds_2:
                return match
            
            return None
        
        except Exception as e:
            return None
    
    def save_matches(self, matches):
        """Save matches voor AI training"""
        if not matches:
            logger.warning("⚠️ No matches to save!")
            return None, None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # DataFrame
        df = pd.DataFrame(matches)
        
        # Add features voor AI
        if 'odds_1' in df.columns and df['odds_1'].notna().any():
            df['implied_prob_home'] = 1 / df['odds_1']
            df['implied_prob_draw'] = 1 / df['odds_x'].fillna(999)
            df['implied_prob_away'] = 1 / df['odds_2']
            df['total_prob'] = df['implied_prob_home'] + df['implied_prob_draw'] + df['implied_prob_away']
            df['margin'] = (df['total_prob'] - 1) * 100
            df['odds_ratio'] = df['odds_1'] / df['odds_2']
        
        # Save CSV
        csv_file = f'../data/unibet_api_{timestamp}.csv'
        os.makedirs(os.path.dirname(csv_file), exist_ok=True)
        df.to_csv(csv_file, index=False)
        logger.info(f"💾 Saved CSV: {csv_file}")
        
        # Save JSON
        json_file = f'../data/unibet_api_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'scrape_time': timestamp,
                    'total_matches': len(matches),
                    'source': 'unibet.nl (Kambi API)',
                    'method': 'api_direct'
                },
                'matches': matches
            }, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Saved JSON: {json_file}")
        
        # Print summary
        logger.info("="*80)
        logger.info(f"🎉 SUCCESSFULLY SCRAPED {len(matches)} MATCHES VIA API!")
        
        if not df.empty and 'odds_1' in df.columns:
            logger.info(f"📊 Average odds: 1={df['odds_1'].mean():.2f} X={df['odds_x'].mean():.2f} 2={df['odds_2'].mean():.2f}")
            logger.info(f"💰 Average margin: {df['margin'].mean():.2f}%")
        
        logger.info("="*80)
        
        return csv_file, json_file
    
    def run(self):
        """Main execution"""
        logger.info("="*80)
        logger.info("🎯🎯🎯 UNIBET API HUNTER GESTART! 🎯🎯🎯")
        logger.info("="*80)
        
        # Fetch matches
        matches = self.get_football_events()
        
        if matches:
            # Save
            files = self.save_matches(matches)
            logger.info("✅ Data ready for AI training!")
            return matches
        else:
            logger.warning("⚠️ No matches found via API")
            logger.info("💡 This could mean:")
            logger.info("  1. API endpoint changed")
            logger.info("  2. Need authentication")
            logger.info("  3. Rate limited")
            return None


if __name__ == '__main__':
    print("="*80)
    print("🎯 UNIBET API HUNTER")
    print("Direct API access - NO browser needed!")
    print("="*80)
    
    try:
        hunter = UnibetAPIHunter()
        matches = hunter.run()
        
        if matches:
            print(f"\n✅ SUCCESS! Got {len(matches)} matches!")
            print("🎯 Data ready to feed to AI!")
            
            # Show sample
            if matches:
                print("\n📋 Sample match:")
                sample = matches[0]
                print(f"   {sample['home_team']} vs {sample['away_team']}")
                print(f"   Odds: {sample['odds_1']} - {sample['odds_x']} - {sample['odds_2']}")
        else:
            print("\n⚠️ No matches found")
            print("API might need authentication or endpoints changed")
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
