"""
💰 MARKET ROI ANALYZER - Track Profitability per Market

Analyze which markets are most profitable:
- ROI per market type (1X2, Over/Under, BTTS, etc.)
- Win rate per market
- Average odds per market
- Best/worst performing markets
- Trend analysis

Author: Sport AI Sync
Date: November 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np


class MarketROIAnalyzer:
    """
    Track and analyze ROI per market type
    
    Markets:
    - 1X2 (Home/Draw/Away)
    - Over/Under (1.5, 2.5, 3.5)
    - BTTS (Yes/No)
    - Double Chance
    - Asian Handicap
    - Correct Score
    """
    
    def __init__(self):
        """Initialize market ROI analyzer"""
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.roi_file = os.path.join(self.data_dir, 'market_roi_data.json')
        self.bets = []
        
        self._load_data()
    
    def log_bet(self, market: str, stake: float, odds: float, 
                won: bool = None, match: str = None, date: str = None) -> None:
        """
        Log a bet for ROI tracking
        
        Args:
            market: Market type ('Home Win', 'Over 2.5', 'BTTS Yes', etc.)
            stake: Stake amount
            odds: Decimal odds
            won: Did bet win? (None = pending)
            match: Match name (optional)
            date: Match date (optional)
        """
        bet = {
            'market': market,
            'stake': stake,
            'odds': odds,
            'won': won,
            'profit': (stake * odds - stake) if won else (-stake if won is False else 0),
            'match': match,
            'date': date or datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'status': 'won' if won is True else 'lost' if won is False else 'pending'
        }
        
        self.bets.append(bet)
        self._save_data()
    
    def settle_bet(self, bet_index: int, won: bool) -> None:
        """
        Settle a pending bet
        
        Args:
            bet_index: Index in bets list
            won: Did bet win?
        """
        if bet_index < len(self.bets):
            bet = self.bets[bet_index]
            bet['won'] = won
            bet['profit'] = (bet['stake'] * bet['odds'] - bet['stake']) if won else -bet['stake']
            bet['status'] = 'won' if won else 'lost'
            self._save_data()
    
    def get_roi_by_market(self, include_pending: bool = False) -> Dict:
        """
        Calculate ROI for each market type
        
        Args:
            include_pending: Include pending bets in calculation
        
        Returns:
            Dict with ROI per market
        """
        # Filter settled bets
        settled = [b for b in self.bets if b['won'] is not None] if not include_pending else self.bets
        
        if not settled:
            return {'message': 'No settled bets yet'}
        
        df = pd.DataFrame(settled)
        
        # Group by market
        market_stats = {}
        
        for market in df['market'].unique():
            market_bets = df[df['market'] == market]
            
            total_stake = market_bets['stake'].sum()
            total_profit = market_bets['profit'].sum()
            
            wins = len(market_bets[market_bets['won'] == True])
            losses = len(market_bets[market_bets['won'] == False])
            total = wins + losses
            
            roi = (total_profit / total_stake * 100) if total_stake > 0 else 0
            win_rate = (wins / total * 100) if total > 0 else 0
            
            avg_odds = market_bets['odds'].mean()
            avg_stake = market_bets['stake'].mean()
            
            market_stats[market] = {
                'total_bets': total,
                'wins': wins,
                'losses': losses,
                'win_rate': win_rate,
                'total_staked': total_stake,
                'total_profit': total_profit,
                'roi': roi,
                'avg_odds': avg_odds,
                'avg_stake': avg_stake,
                'status': '✅ PROFITABLE' if roi > 0 else '❌ LOSING' if roi < 0 else '➖ BREAK EVEN'
            }
        
        # Sort by ROI descending
        sorted_markets = dict(sorted(market_stats.items(), 
                                    key=lambda x: x[1]['roi'], 
                                    reverse=True))
        
        return sorted_markets
    
    def get_best_markets(self, min_bets: int = 10, top_n: int = 5) -> List[Dict]:
        """
        Get best performing markets
        
        Args:
            min_bets: Minimum bets required
            top_n: Number of top markets to return
        
        Returns:
            List of best markets
        """
        roi_data = self.get_roi_by_market()
        
        if isinstance(roi_data, dict) and 'message' in roi_data:
            return []
        
        # Filter by minimum bets
        qualified = {
            market: stats for market, stats in roi_data.items()
            if stats['total_bets'] >= min_bets
        }
        
        # Sort by ROI
        sorted_markets = sorted(qualified.items(), 
                              key=lambda x: x[1]['roi'], 
                              reverse=True)
        
        return [{'market': m, **stats} for m, stats in sorted_markets[:top_n]]
    
    def get_worst_markets(self, min_bets: int = 10, bottom_n: int = 5) -> List[Dict]:
        """
        Get worst performing markets
        
        Args:
            min_bets: Minimum bets required
            bottom_n: Number of bottom markets to return
        
        Returns:
            List of worst markets
        """
        roi_data = self.get_roi_by_market()
        
        if isinstance(roi_data, dict) and 'message' in roi_data:
            return []
        
        # Filter by minimum bets
        qualified = {
            market: stats for market, stats in roi_data.items()
            if stats['total_bets'] >= min_bets
        }
        
        # Sort by ROI ascending
        sorted_markets = sorted(qualified.items(), 
                              key=lambda x: x[1]['roi'])
        
        return [{'market': m, **stats} for m, stats in sorted_markets[:bottom_n]]
    
    def get_market_trends(self, market: str, last_n: int = 20) -> Dict:
        """
        Analyze trends for a specific market
        
        Args:
            market: Market type
            last_n: Last N bets to analyze
        
        Returns:
            Trend analysis dict
        """
        market_bets = [b for b in self.bets if b['market'] == market and b['won'] is not None]
        
        if not market_bets:
            return {'message': f'No settled bets for {market}'}
        
        # Sort by timestamp
        market_bets = sorted(market_bets, key=lambda x: x['timestamp'])
        
        # Get recent bets
        recent = market_bets[-last_n:]
        
        # Calculate rolling ROI
        rolling_roi = []
        cumulative_profit = 0
        cumulative_stake = 0
        
        for bet in recent:
            cumulative_profit += bet['profit']
            cumulative_stake += bet['stake']
            roi = (cumulative_profit / cumulative_stake * 100) if cumulative_stake > 0 else 0
            rolling_roi.append(roi)
        
        # Trend direction
        if len(rolling_roi) >= 2:
            recent_trend = rolling_roi[-1] - rolling_roi[0]
            trend_direction = '📈 IMPROVING' if recent_trend > 5 else '📉 DECLINING' if recent_trend < -5 else '➡️ STABLE'
        else:
            trend_direction = '➡️ INSUFFICIENT DATA'
        
        return {
            'market': market,
            'recent_bets': len(recent),
            'recent_wins': sum(1 for b in recent if b['won']),
            'recent_win_rate': sum(1 for b in recent if b['won']) / len(recent) * 100,
            'recent_roi': rolling_roi[-1] if rolling_roi else 0,
            'trend': trend_direction,
            'rolling_roi': rolling_roi
        }
    
    def get_overall_summary(self) -> Dict:
        """
        Get overall ROI summary
        
        Returns:
            Summary dict
        """
        settled = [b for b in self.bets if b['won'] is not None]
        
        if not settled:
            return {'message': 'No settled bets yet'}
        
        total_stake = sum(b['stake'] for b in settled)
        total_profit = sum(b['profit'] for b in settled)
        
        wins = sum(1 for b in settled if b['won'])
        losses = sum(1 for b in settled if not b['won'])
        
        roi = (total_profit / total_stake * 100) if total_stake > 0 else 0
        win_rate = (wins / len(settled) * 100) if settled else 0
        
        # Best single bet
        best_bet = max(settled, key=lambda x: x['profit'])
        worst_bet = min(settled, key=lambda x: x['profit'])
        
        return {
            'total_bets': len(settled),
            'pending_bets': len([b for b in self.bets if b['won'] is None]),
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'total_staked': total_stake,
            'total_profit': total_profit,
            'roi': roi,
            'best_bet': {
                'match': best_bet['match'],
                'market': best_bet['market'],
                'profit': best_bet['profit']
            },
            'worst_bet': {
                'match': worst_bet['match'],
                'market': worst_bet['market'],
                'profit': worst_bet['profit']
            }
        }
    
    def export_to_csv(self, filename: str = 'market_roi_report.csv') -> str:
        """
        Export ROI data to CSV
        
        Args:
            filename: Output filename
        
        Returns:
            Path to file
        """
        roi_data = self.get_roi_by_market()
        
        if isinstance(roi_data, dict) and 'message' in roi_data:
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(roi_data, orient='index')
        df.index.name = 'Market'
        
        filepath = os.path.join(self.data_dir, filename)
        os.makedirs(self.data_dir, exist_ok=True)
        
        df.to_csv(filepath)
        
        return filepath
    
    def _save_data(self) -> None:
        """Save data to file"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        data = {
            'bets': self.bets,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.roi_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_data(self) -> None:
        """Load data from file"""
        if os.path.exists(self.roi_file):
            with open(self.roi_file, 'r') as f:
                data = json.load(f)
                self.bets = data.get('bets', [])


# =============================================
# DEMO
# =============================================
if __name__ == "__main__":
    print("="*80)
    print("💰 MARKET ROI ANALYZER - Demo")
    print("="*80)
    
    analyzer = MarketROIAnalyzer()
    
    print("\n📝 Simulating 50 bets across different markets...")
    print("-"*80)
    
    # Simulate bets with realistic outcomes
    np.random.seed(42)
    
    markets = {
        'Over 2.5': {'win_rate': 0.62, 'avg_odds': 1.80},
        'BTTS Yes': {'win_rate': 0.58, 'avg_odds': 1.85},
        'Home Win': {'win_rate': 0.48, 'avg_odds': 2.20},
        'Away Win': {'win_rate': 0.35, 'avg_odds': 3.50},
        'Draw': {'win_rate': 0.25, 'avg_odds': 3.80},
        'Over 3.5': {'win_rate': 0.40, 'avg_odds': 2.80},
    }
    
    for i in range(50):
        market = np.random.choice(list(markets.keys()))
        market_data = markets[market]
        
        stake = np.random.uniform(10, 100)
        odds = np.random.normal(market_data['avg_odds'], 0.2)
        won = np.random.random() < market_data['win_rate']
        
        analyzer.log_bet(
            market=market,
            stake=stake,
            odds=odds,
            won=won,
            match=f"Match {i+1}",
            date=(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        )
    
    print("✅ 50 bets simulated")
    
    # ROI by market
    print("\n" + "="*80)
    print("💰 ROI BY MARKET")
    print("="*80)
    
    roi_data = analyzer.get_roi_by_market()
    
    print(f"\n{'Market':<15} {'Bets':<8} {'Win%':<10} {'ROI':<12} {'Profit':<12} Status")
    print("-"*80)
    
    for market, stats in roi_data.items():
        print(f"{market:<15} {stats['total_bets']:<8} {stats['win_rate']:>6.1f}%  "
              f"{stats['roi']:>10.1f}%  €{stats['total_profit']:>9.2f}  {stats['status']}")
    
    # Best markets
    print("\n" + "="*80)
    print("🌟 TOP 3 BEST MARKETS")
    print("="*80)
    
    best = analyzer.get_best_markets(min_bets=5, top_n=3)
    
    for i, market_data in enumerate(best, 1):
        print(f"\n{i}. {market_data['market']}")
        print(f"   ROI: {market_data['roi']:+.1f}% | Win Rate: {market_data['win_rate']:.1f}%")
        print(f"   Bets: {market_data['total_bets']} | Profit: €{market_data['total_profit']:.2f}")
    
    # Worst markets
    print("\n" + "="*80)
    print("❌ BOTTOM 3 WORST MARKETS")
    print("="*80)
    
    worst = analyzer.get_worst_markets(min_bets=5, bottom_n=3)
    
    for i, market_data in enumerate(worst, 1):
        print(f"\n{i}. {market_data['market']}")
        print(f"   ROI: {market_data['roi']:+.1f}% | Win Rate: {market_data['win_rate']:.1f}%")
        print(f"   Bets: {market_data['total_bets']} | Loss: €{market_data['total_profit']:.2f}")
    
    # Overall summary
    print("\n" + "="*80)
    print("📊 OVERALL SUMMARY")
    print("="*80)
    
    summary = analyzer.get_overall_summary()
    
    print(f"\nTotal Bets: {summary['total_bets']}")
    print(f"Win Rate: {summary['win_rate']:.1f}%")
    print(f"Total Staked: €{summary['total_staked']:.2f}")
    print(f"Total Profit: €{summary['total_profit']:+.2f}")
    print(f"Overall ROI: {summary['roi']:+.1f}%")
    
    print(f"\nBest Bet:")
    print(f"  {summary['best_bet']['match']} - {summary['best_bet']['market']}")
    print(f"  Profit: €{summary['best_bet']['profit']:+.2f}")
    
    # Trend analysis
    print("\n" + "="*80)
    print("📈 TREND ANALYSIS - Over 2.5 Goals")
    print("="*80)
    
    trend = analyzer.get_market_trends('Over 2.5', last_n=10)
    
    if 'message' not in trend:
        print(f"\nRecent Performance (Last {trend['recent_bets']} bets):")
        print(f"  Win Rate: {trend['recent_win_rate']:.1f}%")
        print(f"  ROI: {trend['recent_roi']:+.1f}%")
        print(f"  Trend: {trend['trend']}")
    
    # Export
    print("\n" + "="*80)
    print("💾 Exporting to CSV...")
    filepath = analyzer.export_to_csv()
    if filepath:
        print(f"✅ Exported to: {filepath}")
    
    print("\n" + "="*80)
    print("✅ Market ROI Analyzer Ready!")
    print("="*80)
