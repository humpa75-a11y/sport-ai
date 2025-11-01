"""
🔥🔥🔥 ULTIMATE ODDS SCRAPER 🔥🔥🔥
Scrapes odds from BEIDE Unibet & Jacks.nl
Combines data voor beste AI training!

Features:
- Scrapes beide bookmakers tegelijkertijd
- Vergelijkt odds
- Detecteert value bets
- Comprehensive data voor AI
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time
import os
from typing import List, Dict, Any
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedOddsScraper:
    """Scrapes odds from multiple bookmakers"""
    
    def __init__(self):
        self.base_url = "https://eu1.offering-api.kambicdn.com/offering/v2018"
        self.football_group_id = "1000093190"
        
        self.bookmakers = {
            'unibet': {
                'code': 'ubnl',
                'name': 'Unibet.nl',
                'color': '🟢'
            },
            'jacks': {
                'code': 'jvh',
                'name': 'Jacks.nl',
                'color': '🔵'
            }
        }
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'nl-NL,nl;q=0.9',
        })
    
    def scrape_bookmaker(self, bookie_key: str) -> List[Dict]:
        """Scrape odds from one bookmaker"""
        bookie = self.bookmakers[bookie_key]
        logger.info(f"{bookie['color']} Scraping {bookie['name']}...")
        
        url = f"{self.base_url}/{bookie['code']}/betoffer/group/{self.football_group_id}.json"
        params = {'lang': 'nl_NL', 'market': 'NL'}
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                matches = self._parse_kambi_data(data, bookie_key)
                logger.info(f"{bookie['color']} {bookie['name']}: {len(matches)} matches scraped")
                return matches
            else:
                logger.error(f"{bookie['color']} {bookie['name']}: API error {response.status_code}")
                return []
        
        except Exception as e:
            logger.error(f"{bookie['color']} {bookie['name']}: Error - {e}")
            return []
    
    def _parse_kambi_data(self, data: Dict, bookie_key: str) -> List[Dict]:
        """Parse Kambi API response"""
        if 'events' not in data:
            return []
        
        events = data['events']
        betoffers = {bo['id']: bo for bo in data.get('betOffers', [])}
        
        matches = []
        for event in events:
            try:
                match = self._parse_event(event, betoffers, bookie_key)
                if match:
                    matches.append(match)
            except:
                continue
        
        return matches
    
    def _parse_event(self, event: Dict, betoffers: Dict, bookie_key: str) -> Dict:
        """Parse een enkele event"""
        event_id = event.get('id')
        home_team = event.get('homeName', '')
        away_team = event.get('awayName', '')
        
        if not home_team or not away_team:
            return None
        
        # Normalize team names for matching
        home_norm = self._normalize_team_name(home_team)
        away_norm = self._normalize_team_name(away_team)
        
        match = {
            'event_id': event_id,
            'home_team': home_team,
            'away_team': away_team,
            'home_norm': home_norm,
            'away_norm': away_norm,
            'league': event.get('group', 'Unknown'),
            'start_time': event.get('start'),
            'bookmaker': bookie_key,
            'odds_1': None,
            'odds_x': None,
            'odds_2': None,
            'over_2_5': None,
            'under_2_5': None,
            'btts_yes': None,
            'btts_no': None,
        }
        
        # Find betoffers for this event
        event_betoffers = [bo for bo in betoffers.values() if bo.get('eventId') == event_id]
        
        for betoffer in event_betoffers:
            criterion = betoffer.get('criterion', {}).get('label', '').lower()
            
            # 1X2 odds
            if any(kw in criterion for kw in ['reguliere speeltijd', 'wedstrijd', '1x2']):
                for outcome in betoffer.get('outcomes', []):
                    label = outcome.get('label', '').lower()
                    odds = outcome.get('odds')
                    
                    if odds:
                        odds_decimal = odds / 1000
                        if label == '1': match['odds_1'] = odds_decimal
                        elif label == 'x': match['odds_x'] = odds_decimal
                        elif label == '2': match['odds_2'] = odds_decimal
            
            # Over/Under
            elif ('aantal doelpunten' in criterion or 'over/under' in criterion) and '2.5' in criterion:
                for outcome in betoffer.get('outcomes', []):
                    label = outcome.get('label', '').lower()
                    odds = outcome.get('odds')
                    
                    if odds:
                        odds_decimal = odds / 1000
                        if 'over' in label: match['over_2_5'] = odds_decimal
                        elif 'under' in label: match['under_2_5'] = odds_decimal
            
            # BTTS
            elif 'beide teams scoren' in criterion:
                for outcome in betoffer.get('outcomes', []):
                    label = outcome.get('label', '').lower()
                    odds = outcome.get('odds')
                    
                    if odds:
                        odds_decimal = odds / 1000
                        if 'ja' in label: match['btts_yes'] = odds_decimal
                        elif 'nee' in label: match['btts_no'] = odds_decimal
        
        # Only return if we have 1X2 odds
        if match['odds_1'] and match['odds_2']:
            return match
        
        return None
    
    def _normalize_team_name(self, name: str) -> str:
        """Normalize team name for matching"""
        return name.lower().strip().replace('.', '').replace('  ', ' ')
    
    def scrape_all(self) -> Dict[str, List[Dict]]:
        """Scrape all bookmakers"""
        logger.info("="*80)
        logger.info("🔥🔥🔥 ULTIMATE ODDS SCRAPER 🔥🔥🔥")
        logger.info("="*80)
        
        results = {}
        
        # Scrape in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(self.scrape_bookmaker, bookie): bookie 
                for bookie in self.bookmakers.keys()
            }
            
            for future in as_completed(futures):
                bookie = futures[future]
                try:
                    matches = future.result()
                    results[bookie] = matches
                except Exception as e:
                    logger.error(f"Error scraping {bookie}: {e}")
                    results[bookie] = []
        
        return results
    
    def combine_odds(self, results: Dict[str, List[Dict]]) -> pd.DataFrame:
        """Combine odds from all bookmakers"""
        logger.info("\n📊 Combining odds from all bookmakers...")
        
        all_matches = []
        
        for bookie, matches in results.items():
            for match in matches:
                all_matches.append(match)
        
        if not all_matches:
            logger.warning("No matches found!")
            return pd.DataFrame()
        
        df = pd.DataFrame(all_matches)
        
        # Group by match (normalized team names)
        logger.info("🔗 Matching events across bookmakers...")
        
        # Create unified dataset
        unified = []
        
        # Get unique matches
        unibet_matches = df[df['bookmaker'] == 'unibet'].copy()
        jacks_matches = df[df['bookmaker'] == 'jacks'].copy()
        
        # Match events
        for _, unibet_match in unibet_matches.iterrows():
            # Find corresponding Jacks match
            jacks_match = jacks_matches[
                (jacks_matches['home_norm'] == unibet_match['home_norm']) &
                (jacks_matches['away_norm'] == unibet_match['away_norm'])
            ]
            
            unified_match = {
                'home_team': unibet_match['home_team'],
                'away_team': unibet_match['away_team'],
                'league': unibet_match['league'],
                'start_time': unibet_match['start_time'],
                
                # Unibet odds
                'unibet_1': unibet_match['odds_1'],
                'unibet_x': unibet_match['odds_x'],
                'unibet_2': unibet_match['odds_2'],
                'unibet_over_2_5': unibet_match['over_2_5'],
                'unibet_under_2_5': unibet_match['under_2_5'],
                
                # Jacks odds (if found)
                'jacks_1': jacks_match.iloc[0]['odds_1'] if len(jacks_match) > 0 else None,
                'jacks_x': jacks_match.iloc[0]['odds_x'] if len(jacks_match) > 0 else None,
                'jacks_2': jacks_match.iloc[0]['odds_2'] if len(jacks_match) > 0 else None,
                'jacks_over_2_5': jacks_match.iloc[0]['over_2_5'] if len(jacks_match) > 0 else None,
                'jacks_under_2_5': jacks_match.iloc[0]['under_2_5'] if len(jacks_match) > 0 else None,
            }
            
            # Calculate best odds
            odds_1_list = [x for x in [unified_match['unibet_1'], unified_match['jacks_1']] if x]
            odds_x_list = [x for x in [unified_match['unibet_x'], unified_match['jacks_x']] if x]
            odds_2_list = [x for x in [unified_match['unibet_2'], unified_match['jacks_2']] if x]
            
            unified_match['best_odds_1'] = max(odds_1_list) if odds_1_list else None
            unified_match['best_odds_x'] = max(odds_x_list) if odds_x_list else None
            unified_match['best_odds_2'] = max(odds_2_list) if odds_2_list else None
            
            unified.append(unified_match)
        
        # Also add Jacks-only matches
        for _, jacks_match in jacks_matches.iterrows():
            if jacks_match['home_norm'] not in unibet_matches['home_norm'].values:
                unified.append({
                    'home_team': jacks_match['home_team'],
                    'away_team': jacks_match['away_team'],
                    'league': jacks_match['league'],
                    'start_time': jacks_match['start_time'],
                    
                    'unibet_1': None, 'unibet_x': None, 'unibet_2': None,
                    'unibet_over_2_5': None, 'unibet_under_2_5': None,
                    
                    'jacks_1': jacks_match['odds_1'],
                    'jacks_x': jacks_match['odds_x'],
                    'jacks_2': jacks_match['odds_2'],
                    'jacks_over_2_5': jacks_match['over_2_5'],
                    'jacks_under_2_5': jacks_match['under_2_5'],
                    
                    'best_odds_1': jacks_match['odds_1'],
                    'best_odds_x': jacks_match['odds_x'],
                    'best_odds_2': jacks_match['odds_2'],
                })
        
        unified_df = pd.DataFrame(unified)
        
        # Calculate AI features
        unified_df['implied_prob_home'] = 1 / unified_df['best_odds_1']
        unified_df['implied_prob_draw'] = 1 / unified_df['best_odds_x'].fillna(999)
        unified_df['implied_prob_away'] = 1 / unified_df['best_odds_2']
        unified_df['total_prob'] = unified_df['implied_prob_home'] + unified_df['implied_prob_draw'] + unified_df['implied_prob_away']
        unified_df['margin'] = (unified_df['total_prob'] - 1) * 100
        
        # Odds differences (arbitrage opportunities)
        unified_df['odds_diff_1'] = unified_df.apply(
            lambda r: abs(r['unibet_1'] - r['jacks_1']) if r['unibet_1'] and r['jacks_1'] else 0, axis=1
        )
        unified_df['odds_diff_2'] = unified_df.apply(
            lambda r: abs(r['unibet_2'] - r['jacks_2']) if r['unibet_2'] and r['jacks_2'] else 0, axis=1
        )
        
        return unified_df
    
    def save_combined_data(self, df: pd.DataFrame):
        """Save combined data"""
        if df.empty:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        os.makedirs('data', exist_ok=True)
        
        # CSV
        csv_file = f'data/unified_odds_{timestamp}.csv'
        df.to_csv(csv_file, index=False)
        logger.info(f"💾 CSV saved: {csv_file}")
        
        # JSON
        json_file = f'data/unified_odds_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'scrape_time': timestamp,
                    'total_matches': len(df),
                    'sources': ['unibet.nl', 'jacks.nl'],
                    'method': 'unified_scraper'
                },
                'matches': df.to_dict('records')
            }, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 JSON saved: {json_file}")
        
        # Stats
        logger.info("\n" + "="*80)
        logger.info(f"🎉 TOTAL: {len(df)} unique matches!")
        logger.info(f"📊 Leagues: {df['league'].nunique()}")
        logger.info(f"📊 Average best odds: 1={df['best_odds_1'].mean():.2f} X={df['best_odds_x'].mean():.2f} 2={df['best_odds_2'].mean():.2f}")
        logger.info(f"💰 Average margin: {df['margin'].mean():.2f}%")
        
        # Matches on both bookmakers
        both = df[(df['unibet_1'].notna()) & (df['jacks_1'].notna())]
        logger.info(f"\n🔗 {len(both)} matches found on BOTH bookmakers")
        
        if len(both) > 0:
            logger.info(f"📊 Average odds difference:")
            logger.info(f"   Home win: {both['odds_diff_1'].mean():.3f}")
            logger.info(f"   Away win: {both['odds_diff_2'].mean():.3f}")
        
        logger.info("="*80)
    
    def run(self):
        """Main execution"""
        # Scrape all
        results = self.scrape_all()
        
        # Combine
        df = self.combine_odds(results)
        
        if not df.empty:
            # Save
            self.save_combined_data(df)
            
            logger.info("\n✅ Data ready for AI training!")
            return df
        else:
            logger.warning("⚠️ No data collected")
            return None


if __name__ == '__main__':
    print("="*80)
    print("🔥🔥🔥 ULTIMATE ODDS SCRAPER 🔥🔥🔥")
    print("Scraping Unibet + Jacks.nl")
    print("="*80)
    
    try:
        scraper = UnifiedOddsScraper()
        df = scraper.run()
        
        if df is not None:
            print(f"\n✅ SUCCESS! {len(df)} matches scraped!")
            print("\n📋 Sample matches:")
            for i, row in df.head(5).iterrows():
                print(f"\n{i+1}. {row['home_team']} vs {row['away_team']}")
                print(f"   League: {row['league']}")
                print(f"   Best odds: {row['best_odds_1']:.2f} - {row['best_odds_x']:.2f} - {row['best_odds_2']:.2f}")
                if pd.notna(row['unibet_1']) and pd.notna(row['jacks_1']):
                    print(f"   🟢 Unibet: {row['unibet_1']:.2f} - {row['unibet_x']:.2f} - {row['unibet_2']:.2f}")
                    print(f"   🔵 Jacks:  {row['jacks_1']:.2f} - {row['jacks_x']:.2f} - {row['jacks_2']:.2f}")
        else:
            print("\n⚠️ No data")
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
