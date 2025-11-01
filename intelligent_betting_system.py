"""
🚀 INTELLIGENT BETTING SYSTEM - Complete Integration

Phase 1 Features:
✅ Kelly Criterion Bankroll Management
✅ Historical Prediction Tracking  
✅ Odds Movement Monitor

Complete workflow:
1. Fetch matches & predictions
2. Track odds movements
3. Calculate optimal stakes (Kelly)
4. Log predictions
5. Generate intelligent recommendations

Author: Sport AI Sync
Date: November 2025
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.multi_source_aggregator import MultiSourceAggregator
from backend.bankroll_manager import BankrollManager
from backend.prediction_tracker import PredictionTracker
from backend.odds_movement_monitor import OddsMovementMonitor

from datetime import datetime
from typing import Dict, List
import json


class IntelligentBettingSystem:
    """
    Complete betting system met alle Phase 1 features
    
    Workflow:
    1. Fetch predictions (1-2 days ahead)
    2. Monitor odds movements
    3. Calculate Kelly stakes
    4. Log predictions
    5. Generate recommendations
    """
    
    def __init__(self, initial_bankroll: float = 1000.0, 
                 risk_profile: str = 'moderate'):
        """
        Initialize complete system
        
        Args:
            initial_bankroll: Starting bankroll (€)
            risk_profile: 'conservative', 'moderate', or 'aggressive'
        """
        print("🚀 Initializing Intelligent Betting System...")
        
        self.aggregator = MultiSourceAggregator()
        self.bankroll = BankrollManager(initial_bankroll, risk_profile)
        self.tracker = PredictionTracker()
        self.odds_monitor = OddsMovementMonitor()
        
        print(f"✅ System ready! Bankroll: €{initial_bankroll:.2f} | Risk: {risk_profile.upper()}")
    
    def analyze_and_recommend(self, league: str = 'bundesliga', 
                             days_ahead: int = 2) -> Dict:
        """
        Complete analysis with intelligent recommendations
        
        Args:
            league: League to analyze
            days_ahead: Days ahead to predict (1-2)
        
        Returns:
            Complete analysis dict
        """
        print(f"\n{'='*80}")
        print(f"🎯 ANALYZING {league.upper()} - {days_ahead} days ahead")
        print(f"{'='*80}")
        
        # 1. Fetch predictions
        print("\n📊 Step 1: Fetching predictions...")
        results = self.aggregator.run_full_analysis(league, days_ahead)
        
        if 'error' in results:
            return results
        
        recommendations = []
        
        # 2. Process each match
        for match in results['matches']:
            match_id = f"{league}_{match['home_team']}_{match['away_team']}_{match['match_date']}"
            match_name = f"{match['home_team']} vs {match['away_team']}"
            
            print(f"\n{'='*80}")
            print(f"⚽ {match_name}")
            print(f"📅 {match['match_date']} {match['match_time']}")
            print(f"{'='*80}")
            
            # Process predictions for this match
            for prediction in match['predictions']:
                market = prediction['market']
                prob = prediction['probability']
                odds = prediction['odds']
                confidence = prediction['confidence']
                
                # 3. Monitor odds (log current odds)
                self.odds_monitor.log_odds(
                    match_id=match_id,
                    match_name=match_name,
                    match_date=match['match_date'],
                    market=market,
                    odds=odds,
                    probability=prob
                )
                
                # 4. Calculate Kelly stake
                stake_rec = self.bankroll.get_stake_recommendation(
                    probability=prob,
                    odds=odds,
                    market=market,
                    match=match_name
                )
                
                # 5. Log prediction
                self.tracker.log_prediction(
                    match_id=match_id,
                    match_name=match_name,
                    match_date=match['match_date'],
                    market=market,
                    prediction=prediction['prediction'],
                    probability=prob,
                    odds=odds,
                    confidence=confidence
                )
                
                # 6. Create recommendation
                rec = {
                    'match_name': match_name,
                    'match_date': match['match_date'],
                    'match_time': match['match_time'],
                    'market': market,
                    'prediction': prediction['prediction'],
                    'odds': odds,
                    'probability': prob,
                    'confidence': confidence,
                    'ev': prediction['ev'],
                    'ev_pct': prediction['ev_pct'],
                    'stake': stake_rec['stake'],
                    'stake_percent': stake_rec['stake_percent'],
                    'expected_return': stake_rec['expected_return'],
                    'recommendation': stake_rec['recommendation'],
                    'warnings': stake_rec['warnings']
                }
                
                recommendations.append(rec)
                
                # Print recommendation
                print(f"\n📊 {market}: {prediction['prediction']}")
                print(f"   Odds: {odds:.2f} | Probability: {prob:.1%} | Confidence: {confidence:.1%}")
                print(f"   EV: {prediction['ev_pct']:+.1f}%")
                print(f"   💰 Recommended Stake: €{stake_rec['stake']:.2f} ({stake_rec['stake_percent']:.1f}% of bankroll)")
                print(f"   📈 Expected Return: €{stake_rec['expected_return']:.2f}")
                print(f"   {stake_rec['recommendation']}")
                
                if stake_rec['warnings']:
                    for warning in stake_rec['warnings']:
                        print(f"   ⚠️ {warning}")
        
        # 7. Check for odds movements
        print(f"\n{'='*80}")
        print("🚨 ODDS MOVEMENT ALERTS")
        print(f"{'='*80}")
        
        alerts = self.odds_monitor.get_active_alerts(hours=24)
        
        if alerts:
            for alert in alerts[:5]:  # Top 5
                print(f"\n{alert['emoji']} {alert['severity']} - {alert['match_name']}")
                print(f"   Market: {alert['market']}")
                print(f"   Movement: {alert['old_odds']} → {alert['new_odds']} ({alert['movement_pct']:+.1f}%)")
                if alert.get('ev'):
                    print(f"   EV: {alert['ev']:+.2%}")
                if alert['value_bet']:
                    print(f"   💎 VALUE BET!")
        else:
            print("✅ No significant movements detected")
        
        # 8. Summary
        print(f"\n{'='*80}")
        print("📊 SYSTEM STATUS")
        print(f"{'='*80}")
        
        bankroll_stats = self.bankroll.get_statistics()
        print(f"\n💰 Bankroll: €{bankroll_stats['current_bankroll']:.2f}")
        print(f"   Total Bets: {bankroll_stats['total_bets']}")
        print(f"   Win Rate: {bankroll_stats['win_rate']:.1%}")
        print(f"   Total ROI: {bankroll_stats['roi']:.2%}")
        
        tracker_stats = self.tracker.get_performance_summary()
        print(f"\n📊 Predictions Tracked: {tracker_stats['total_predictions']}")
        print(f"   Pending: {tracker_stats['pending']}")
        print(f"   Settled: {tracker_stats['settled']}")
        
        return {
            'league': league,
            'days_ahead': days_ahead,
            'timestamp': datetime.now().isoformat(),
            'recommendations': recommendations,
            'odds_alerts': alerts,
            'bankroll_status': bankroll_stats,
            'prediction_status': tracker_stats
        }
    
    def get_best_bets(self, min_ev: float = 0.10, max_bets: int = 5) -> List[Dict]:
        """
        Get top value bets based on EV and stake recommendations
        
        Args:
            min_ev: Minimum EV threshold (default: 10%)
            max_bets: Maximum number of bets to return
        
        Returns:
            List of best bets
        """
        # This would aggregate from recent analyses
        # For now, placeholder
        return []
    
    def export_report(self, analysis: Dict, filename: str = None) -> str:
        """
        Export complete analysis to JSON
        
        Args:
            analysis: Analysis dict from analyze_and_recommend()
            filename: Optional custom filename
        
        Returns:
            Path to exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"intelligent_betting_report_{timestamp}.json"
        
        filepath = os.path.join('data', filename)
        os.makedirs('data', exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"\n💾 Report exported: {filepath}")
        return filepath


# =============================================
# DEMO
# =============================================
if __name__ == "__main__":
    print("="*80)
    print("🚀 INTELLIGENT BETTING SYSTEM - Phase 1 Complete Demo")
    print("="*80)
    print("\nFeatures:")
    print("✅ Multi-source predictions (7 APIs)")
    print("✅ Kelly Criterion stake sizing")
    print("✅ Historical tracking")
    print("✅ Odds movement monitoring")
    print("✅ Intelligent recommendations")
    
    # Initialize system
    system = IntelligentBettingSystem(
        initial_bankroll=1000.0,
        risk_profile='moderate'
    )
    
    # Run complete analysis
    analysis = system.analyze_and_recommend(
        league='bundesliga',
        days_ahead=2
    )
    
    # Export report
    if 'error' not in analysis:
        system.export_report(analysis)
    
    print("\n" + "="*80)
    print("✅ INTELLIGENT BETTING SYSTEM READY FOR PRODUCTION!")
    print("="*80)
