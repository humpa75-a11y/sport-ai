"""
📈 ODDS MOVEMENT MONITOR - Real-Time Odds Tracking & Alerts

Features:
- Track odds changes over time
- Alert bij significante movements (>10%)
- Detect value bet opportunities
- Market sentiment analysis
- Steam moves detection

Author: Sport AI Sync
Date: November 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd


class OddsMovementMonitor:
    """
    Monitor odds changes en genereer alerts
    
    Features:
    - Odds history tracking
    - Movement detection (>10% = significant)
    - Value bet alerts (odds up + good prediction)
    - Steam moves (odds down = smart money)
    - Market sentiment
    """
    
    def __init__(self, alert_threshold: float = 0.10):
        """
        Initialize Odds Movement Monitor
        
        Args:
            alert_threshold: Movement threshold for alerts (default: 10%)
        """
        self.alert_threshold = alert_threshold
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.odds_file = os.path.join(self.data_dir, 'odds_movements.json')
        self.odds_history = []
        self.alerts = []
        
        self._load_data()
    
    def log_odds(self, match_id: str, match_name: str, match_date: str,
                market: str, odds: float, probability: Optional[float] = None) -> None:
        """
        Log current odds for a match/market
        
        Args:
            match_id: Unique match identifier
            match_name: "Team A vs Team B"
            match_date: YYYY-MM-DD
            market: Market type (Home, Draw, Away, Over 2.5, etc.)
            odds: Current decimal odds
            probability: Optional model probability for value calculation
        """
        entry = {
            'match_id': match_id,
            'match_name': match_name,
            'match_date': match_date,
            'market': market,
            'odds': odds,
            'probability': probability,
            'timestamp': datetime.now().isoformat()
        }
        
        self.odds_history.append(entry)
        
        # Check for movement (compare with previous)
        self._check_movement(match_id, market, odds, probability)
        
        self._save_data()
    
    def _check_movement(self, match_id: str, market: str, current_odds: float,
                       probability: Optional[float] = None) -> None:
        """
        Check voor significante odds movements
        
        Args:
            match_id: Match identifier
            market: Market type
            current_odds: Current odds
            probability: Optional probability
        """
        # Find previous odds for this match/market
        previous_entries = [
            entry for entry in self.odds_history
            if entry['match_id'] == match_id and entry['market'] == market
            and entry['odds'] != current_odds  # Skip current entry
        ]
        
        if not previous_entries:
            return  # No previous data
        
        # Get most recent previous odds
        previous = sorted(previous_entries, key=lambda x: x['timestamp'])[-1]
        previous_odds = previous['odds']
        
        # Calculate movement
        movement = (current_odds - previous_odds) / previous_odds
        movement_pct = movement * 100
        
        # Check if significant
        if abs(movement) >= self.alert_threshold:
            alert = self._create_alert(
                match_id, previous['match_name'], previous['match_date'],
                market, previous_odds, current_odds, movement_pct,
                probability
            )
            self.alerts.append(alert)
    
    def _create_alert(self, match_id: str, match_name: str, match_date: str,
                     market: str, old_odds: float, new_odds: float,
                     movement_pct: float, probability: Optional[float]) -> Dict:
        """
        Create an odds movement alert
        
        Args:
            match_id: Match identifier
            match_name: Match name
            match_date: Match date
            market: Market type
            old_odds: Previous odds
            new_odds: Current odds
            movement_pct: Movement percentage
            probability: Optional model probability
        
        Returns:
            Alert dict
        """
        # Determine alert type
        if movement_pct > 0:
            direction = "UP"
            alert_type = "VALUE_OPPORTUNITY"  # Odds increased = bookies less confident
            emoji = "📈"
        else:
            direction = "DOWN"
            alert_type = "STEAM_MOVE"  # Odds decreased = smart money
            emoji = "📉"
        
        # Calculate value if probability available
        ev = None
        value_bet = False
        
        if probability:
            ev = (probability * (new_odds - 1)) - (1 - probability)
            value_bet = ev > 0.05  # 5% EV threshold
        
        alert = {
            'timestamp': datetime.now().isoformat(),
            'match_id': match_id,
            'match_name': match_name,
            'match_date': match_date,
            'market': market,
            'old_odds': old_odds,
            'new_odds': new_odds,
            'movement_pct': round(movement_pct, 2),
            'direction': direction,
            'alert_type': alert_type,
            'emoji': emoji,
            'ev': round(ev, 4) if ev else None,
            'value_bet': value_bet,
            'severity': (
                'HIGH' if abs(movement_pct) > 15
                else 'MEDIUM' if abs(movement_pct) > 10
                else 'LOW'
            )
        }
        
        return alert
    
    def get_active_alerts(self, hours: int = 24) -> List[Dict]:
        """
        Get recent alerts (last N hours)
        
        Args:
            hours: Timeframe in hours (default: 24)
        
        Returns:
            List of recent alerts
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']) > cutoff
        ]
        
        # Sort by severity and timestamp
        severity_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        recent_alerts.sort(
            key=lambda x: (severity_order[x['severity']], x['timestamp']),
            reverse=True
        )
        
        return recent_alerts
    
    def get_value_opportunities(self, min_ev: float = 0.05) -> List[Dict]:
        """
        Get current value bet opportunities (odds UP + good EV)
        
        Args:
            min_ev: Minimum EV threshold (default: 5%)
        
        Returns:
            List of value opportunities
        """
        opportunities = [
            alert for alert in self.alerts
            if alert['alert_type'] == 'VALUE_OPPORTUNITY'
            and alert['value_bet']
            and alert.get('ev', 0) >= min_ev
        ]
        
        # Sort by EV descending
        opportunities.sort(key=lambda x: x.get('ev', 0), reverse=True)
        
        return opportunities
    
    def get_steam_moves(self, min_movement: float = 10) -> List[Dict]:
        """
        Get steam moves (odds DOWN = smart money)
        
        Args:
            min_movement: Minimum movement % (default: 10%)
        
        Returns:
            List of steam moves
        """
        steam_moves = [
            alert for alert in self.alerts
            if alert['alert_type'] == 'STEAM_MOVE'
            and abs(alert['movement_pct']) >= min_movement
        ]
        
        # Sort by movement size descending
        steam_moves.sort(key=lambda x: abs(x['movement_pct']), reverse=True)
        
        return steam_moves
    
    def get_odds_history(self, match_id: str, market: str) -> pd.DataFrame:
        """
        Get odds history for a specific match/market
        
        Args:
            match_id: Match identifier
            market: Market type
        
        Returns:
            DataFrame with odds history
        """
        history = [
            entry for entry in self.odds_history
            if entry['match_id'] == match_id and entry['market'] == market
        ]
        
        if not history:
            return pd.DataFrame()
        
        df = pd.DataFrame(history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        return df
    
    def get_market_sentiment(self, match_id: str) -> Dict:
        """
        Analyse market sentiment voor een match (alle markets)
        
        Args:
            match_id: Match identifier
        
        Returns:
            Sentiment analysis dict
        """
        match_odds = [
            entry for entry in self.odds_history
            if entry['match_id'] == match_id
        ]
        
        if not match_odds:
            return {'message': 'No odds data for this match'}
        
        # Group by market
        df = pd.DataFrame(match_odds)
        
        sentiment = {}
        for market in df['market'].unique():
            market_df = df[df['market'] == market].sort_values('timestamp')
            
            if len(market_df) < 2:
                continue
            
            # Calculate overall trend
            first_odds = market_df.iloc[0]['odds']
            last_odds = market_df.iloc[-1]['odds']
            movement = (last_odds - first_odds) / first_odds * 100
            
            sentiment[market] = {
                'initial_odds': first_odds,
                'current_odds': last_odds,
                'movement_pct': round(movement, 2),
                'trend': '📈 UP' if movement > 5 else '📉 DOWN' if movement < -5 else '➡️ STABLE',
                'data_points': len(market_df)
            }
        
        return sentiment
    
    def generate_alert_summary(self) -> str:
        """
        Generate text summary of active alerts
        
        Returns:
            Formatted string summary
        """
        recent_alerts = self.get_active_alerts(hours=24)
        
        if not recent_alerts:
            return "✅ No significant odds movements in last 24 hours"
        
        summary = f"🚨 {len(recent_alerts)} ODDS ALERTS (Last 24h)\n\n"
        
        for alert in recent_alerts[:10]:  # Top 10
            summary += f"{alert['emoji']} {alert['severity']} - {alert['match_name']}\n"
            summary += f"   Market: {alert['market']}\n"
            summary += f"   Movement: {alert['old_odds']} → {alert['new_odds']} ({alert['movement_pct']:+.1f}%)\n"
            
            if alert.get('ev'):
                summary += f"   EV: {alert['ev']:+.2%}\n"
            
            summary += f"   Type: {alert['alert_type'].replace('_', ' ')}\n\n"
        
        return summary
    
    def _save_data(self) -> None:
        """Save odds history and alerts to file"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        data = {
            'odds_history': self.odds_history,
            'alerts': self.alerts,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.odds_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_data(self) -> None:
        """Load odds history and alerts from file"""
        if os.path.exists(self.odds_file):
            with open(self.odds_file, 'r') as f:
                data = json.load(f)
                self.odds_history = data.get('odds_history', [])
                self.alerts = data.get('alerts', [])


# =============================================
# DEMO / TEST
# =============================================
if __name__ == "__main__":
    print("="*80)
    print("📈 ODDS MOVEMENT MONITOR - Real-Time Tracking Demo")
    print("="*80)
    
    monitor = OddsMovementMonitor(alert_threshold=0.10)
    
    # Simulate odds movements
    print("\n📊 Simulating odds movements...\n")
    
    # Match 1: Bayern vs Leverkusen - Over 2.5
    # Initial odds
    monitor.log_odds(
        match_id='BUN_001',
        match_name='Bayern Munich vs Bayer Leverkusen',
        match_date='2025-11-01',
        market='Over 2.5',
        odds=1.80,
        probability=0.78
    )
    
    print("✅ Initial odds logged: Over 2.5 @ 1.80")
    
    # Odds dropped (steam move - smart money)
    import time
    time.sleep(0.5)
    monitor.log_odds(
        match_id='BUN_001',
        match_name='Bayern Munich vs Bayer Leverkusen',
        match_date='2025-11-01',
        market='Over 2.5',
        odds=1.65,  # 8.3% drop
        probability=0.78
    )
    
    print("📉 Odds moved: 1.80 → 1.65 (STEAM MOVE!)")
    
    # Match 2: Heidenheim vs Frankfurt - Away Win
    # Initial odds
    monitor.log_odds(
        match_id='BUN_002',
        match_name='Heidenheim vs Eintracht Frankfurt',
        match_date='2025-11-01',
        market='Away Win',
        odds=1.90,
        probability=0.55
    )
    
    print("✅ Initial odds logged: Away Win @ 1.90")
    
    # Odds increased (value opportunity)
    time.sleep(0.5)
    monitor.log_odds(
        match_id='BUN_002',
        match_name='Heidenheim vs Eintracht Frankfurt',
        match_date='2025-11-01',
        market='Away Win',
        odds=2.15,  # 13.2% increase
        probability=0.55
    )
    
    print("📈 Odds moved: 1.90 → 2.15 (VALUE OPPORTUNITY!)")
    
    # Get alerts
    print("\n" + "="*80)
    print("🚨 ACTIVE ALERTS")
    print("="*80)
    
    alerts = monitor.get_active_alerts()
    
    for alert in alerts:
        print(f"\n{alert['emoji']} {alert['severity']} ALERT - {alert['match_name']}")
        print(f"   Market: {alert['market']}")
        print(f"   Movement: {alert['old_odds']} → {alert['new_odds']} ({alert['movement_pct']:+.1f}%)")
        print(f"   Type: {alert['alert_type'].replace('_', ' ')}")
        
        if alert.get('ev'):
            print(f"   Expected Value: {alert['ev']:+.2%}")
        
        if alert['value_bet']:
            print(f"   💎 VALUE BET OPPORTUNITY!")
    
    print("\n" + "="*80)
    print("✅ Odds Movement Monitor Ready!")
    print("="*80)
