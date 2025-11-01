"""
🎯 TOTO.NL COMPLETE SCRAPER - VREET HUN DATA ALS ONBIJT! 🎯
====================================================================
Discovered API: sport-api.toto.nl/live/information
Extracts: Football matches, odds (1X2, O/U, BTTS), live events
Purpose: Feed Master AI Professor for 100% SNIPER ACCURACY
====================================================================
"""

import requests
import json
import pandas as pd
from datetime import datetime
import logging
from typing import Dict, List, Optional
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

class TOTOScraper:
    """TOTO.nl Football Odds Scraper - API Discovery Implementation"""
    
    def __init__(self):
        self.base_url = "https://sport-api.toto.nl"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'nl-NL,nl;q=0.9,en;q=0.8',
            'Origin': 'https://sport.toto.nl',
            'Referer': 'https://sport.toto.nl/'
        })
        
    def get_live_information(self) -> Dict:
        """
        Get live information from TOTO API
        Returns raw API response with all available data
        """
        try:
            url = f"{self.base_url}/live/information"
            logger.info(f"🌐 Requesting: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ API Response received: {len(str(data))} bytes")
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error getting live information: {e}")
            return {}
    
    def get_cms_skeleton(self, form_factor: str = "desktop") -> Dict:
        """
        Get CMS skeleton data (site structure with sports/markets)
        """
        try:
            url = f"{self.base_url}/cms/skeleton"
            params = {"formFactor": form_factor}
            
            logger.info(f"🌐 Requesting: {url}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ CMS Skeleton received: {len(str(data))} bytes")
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error getting CMS skeleton: {e}")
            return {}
    
    def extract_football_matches(self, data: Dict) -> List[Dict]:
        """
        Extract football matches from TOTO API response
        Adaptable structure - will analyze whatever comes back
        """
        matches = []
        
        try:
            # TOTO API structure discovery
            logger.info("🔍 Analyzing TOTO API structure...")
            
            # Check various possible locations for match data
            possible_keys = [
                'events', 'matches', 'competitions', 'sports',
                'fixtures', 'data', 'items', 'results', 'games'
            ]
            
            for key in possible_keys:
                if key in data:
                    logger.info(f"✅ Found key: '{key}'")
                    value = data[key]
                    
                    if isinstance(value, list):
                        logger.info(f"   → Contains {len(value)} items")
                        # Process list items
                        for item in value[:3]:  # Show first 3 samples
                            logger.info(f"   → Sample keys: {list(item.keys())[:10]}")
                    elif isinstance(value, dict):
                        logger.info(f"   → Dict with keys: {list(value.keys())}")
            
            # Try to extract football-specific data
            # This is adaptive - will work with whatever structure TOTO uses
            if 'events' in data:
                for event in data.get('events', []):
                    if self._is_football_event(event):
                        match_data = self._parse_toto_event(event)
                        if match_data:
                            matches.append(match_data)
            
            logger.info(f"✅ Extracted {len(matches)} football matches")
            
        except Exception as e:
            logger.error(f"❌ Error extracting matches: {e}")
        
        return matches
    
    def _is_football_event(self, event: Dict) -> bool:
        """Check if event is football/soccer"""
        sport_indicators = ['football', 'soccer', 'voetbal', '11']
        event_str = json.dumps(event).lower()
        return any(indicator in event_str for indicator in sport_indicators)
    
    def _parse_toto_event(self, event: Dict) -> Optional[Dict]:
        """
        Parse a TOTO event into standardized match data
        Adaptive parsing based on available fields
        """
        try:
            # Extract basic info (adapt based on actual structure)
            match_data = {
                'event_id': event.get('id') or event.get('eventId') or event.get('matchId'),
                'home_team': None,
                'away_team': None,
                'competition': None,
                'start_time': None,
                'odds_1': None,
                'odds_x': None,
                'odds_2': None,
                'odds_over': None,
                'odds_under': None,
                'odds_btts_yes': None,
                'odds_btts_no': None
            }
            
            # Extract team names (multiple possible structures)
            if 'participants' in event:
                participants = event['participants']
                if isinstance(participants, list) and len(participants) >= 2:
                    match_data['home_team'] = participants[0].get('name')
                    match_data['away_team'] = participants[1].get('name')
            
            if 'homeTeam' in event:
                match_data['home_team'] = event['homeTeam'].get('name')
            if 'awayTeam' in event:
                match_data['away_team'] = event['awayTeam'].get('name')
            
            # Extract competition
            if 'competition' in event:
                match_data['competition'] = event['competition'].get('name')
            elif 'league' in event:
                match_data['competition'] = event['league'].get('name')
            
            # Extract start time
            for time_key in ['startTime', 'kickoffTime', 'scheduledStartTime', 'startDate']:
                if time_key in event:
                    match_data['start_time'] = event[time_key]
                    break
            
            # Extract odds (check multiple market structures)
            if 'markets' in event:
                markets = event['markets']
                match_data.update(self._extract_odds_from_markets(markets))
            elif 'odds' in event:
                match_data.update(self._extract_odds_direct(event['odds']))
            
            # Only return if we have basic match info
            if match_data['home_team'] and match_data['away_team']:
                return match_data
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error parsing event: {e}")
            return None
    
    def _extract_odds_from_markets(self, markets: List[Dict]) -> Dict:
        """Extract odds from markets structure"""
        odds = {}
        
        for market in markets:
            market_type = market.get('type', '').lower()
            selections = market.get('selections', [])
            
            # 1X2 Market
            if '1x2' in market_type or 'match result' in market_type:
                for selection in selections:
                    name = selection.get('name', '').lower()
                    odd = selection.get('odds') or selection.get('decimal')
                    
                    if '1' in name or 'home' in name:
                        odds['odds_1'] = odd
                    elif 'x' in name or 'draw' in name:
                        odds['odds_x'] = odd
                    elif '2' in name or 'away' in name:
                        odds['odds_2'] = odd
            
            # Over/Under Market
            if 'over' in market_type or 'under' in market_type or 'goals' in market_type:
                for selection in selections:
                    name = selection.get('name', '').lower()
                    odd = selection.get('odds') or selection.get('decimal')
                    
                    if 'over' in name:
                        odds['odds_over'] = odd
                    elif 'under' in name:
                        odds['odds_under'] = odd
            
            # BTTS Market
            if 'btts' in market_type or 'both teams' in market_type:
                for selection in selections:
                    name = selection.get('name', '').lower()
                    odd = selection.get('odds') or selection.get('decimal')
                    
                    if 'yes' in name:
                        odds['odds_btts_yes'] = odd
                    elif 'no' in name:
                        odds['odds_btts_no'] = odd
        
        return odds
    
    def _extract_odds_direct(self, odds_obj: Dict) -> Dict:
        """Extract odds from direct odds object"""
        odds = {}
        
        # Try different possible structures
        if '1' in odds_obj:
            odds['odds_1'] = odds_obj['1']
        if 'x' in odds_obj:
            odds['odds_x'] = odds_obj['x']
        if '2' in odds_obj:
            odds['odds_2'] = odds_obj['2']
        
        return odds
    
    def scrape_football_odds(self) -> pd.DataFrame:
        """
        Main scraping function - gets all football odds from TOTO
        Returns DataFrame with standardized format
        """
        logger.info("=" * 80)
        logger.info("🎲 TOTO.NL FOOTBALL SCRAPER - VREET HUN DATA ALS ONBIJT!")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        # Get live information
        live_data = self.get_live_information()
        
        # Get CMS skeleton for additional context
        cms_data = self.get_cms_skeleton()
        
        # Save raw responses for analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with open(f'data/toto_live_raw_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(live_data, f, indent=2, ensure_ascii=False)
        logger.info(f"📄 Raw live data saved")
        
        with open(f'data/toto_cms_raw_{timestamp}.json', 'w', encoding='utf-8') as f:
            json.dump(cms_data, f, indent=2, ensure_ascii=False)
        logger.info(f"📄 Raw CMS data saved")
        
        # Extract matches
        matches = self.extract_football_matches(live_data)
        
        # If no matches in live data, try CMS data
        if not matches:
            logger.info("⚠️ No matches in live data, trying CMS data...")
            matches = self.extract_football_matches(cms_data)
        
        # Create DataFrame
        if matches:
            df = pd.DataFrame(matches)
            
            # Add metadata
            df['bookmaker'] = 'TOTO.nl'
            df['scrape_time'] = datetime.now()
            df['timestamp'] = timestamp
            
            # Calculate implied probabilities
            for market in ['1', 'x', '2', 'over', 'under', 'btts_yes', 'btts_no']:
                odds_col = f'odds_{market}'
                prob_col = f'implied_prob_{market}'
                
                if odds_col in df.columns:
                    df[prob_col] = df[odds_col].apply(
                        lambda x: round(1/x * 100, 2) if pd.notna(x) and x > 0 else None
                    )
            
            # Calculate margin
            df['margin'] = df.apply(
                lambda row: round(
                    (row.get('implied_prob_1', 0) or 0) +
                    (row.get('implied_prob_x', 0) or 0) +
                    (row.get('implied_prob_2', 0) or 0) - 100, 2
                ), axis=1
            )
            
            # Save to CSV
            csv_file = f'data/toto_odds_{timestamp}.csv'
            df.to_csv(csv_file, index=False, encoding='utf-8')
            
            elapsed = time.time() - start_time
            
            logger.info("=" * 80)
            logger.info(f"✅ TOTO SCRAPER COMPLETE!")
            logger.info(f"📊 Matches found: {len(df)}")
            logger.info(f"⚡ Time taken: {elapsed:.2f}s")
            logger.info(f"💾 Saved to: {csv_file}")
            logger.info("=" * 80)
            
            return df
        
        else:
            logger.warning("⚠️ No matches found in TOTO API response")
            logger.info("📄 Check raw JSON files for structure analysis")
            
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=[
                'event_id', 'home_team', 'away_team', 'competition', 'start_time',
                'odds_1', 'odds_x', 'odds_2', 'odds_over', 'odds_under',
                'odds_btts_yes', 'odds_btts_no', 'bookmaker', 'scrape_time'
            ])


def main():
    """Run TOTO scraper"""
    scraper = TOTOScraper()
    df = scraper.scrape_football_odds()
    
    # Display results
    if not df.empty:
        print("\n" + "=" * 80)
        print("🎯 TOTO.NL VOETBAL ODDS - SAMPLE")
        print("=" * 80)
        print(df[['home_team', 'away_team', 'odds_1', 'odds_x', 'odds_2']].head(10))
        print("=" * 80)
        print(f"\nTotal matches: {len(df)}")
        print(f"With 1X2 odds: {df['odds_1'].notna().sum()}")
        print(f"With O/U odds: {df['odds_over'].notna().sum()}")
        print(f"With BTTS odds: {df['odds_btts_yes'].notna().sum()}")
        print("=" * 80)
    else:
        print("\n⚠️ No data extracted - check logs and raw JSON files")
        print("🔍 API structure needs analysis")


if __name__ == "__main__":
    main()
