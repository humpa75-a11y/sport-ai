"""
🎯 INTELLIGENT BETTING SYSTEM - Production Version

Complete werkende versie met:
- Real API calls waar mogelijk
- Graceful fallback to realistic estimates
- Error handling overal
- Data validation

Author: Sport AI Sync
Date: November 2025
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend import multi_source_aggregator as aggregator
from backend.ensemble_predictor import EnsemblePredictor
from backend.bankroll_manager import BankrollManager
from backend.prediction_tracker import PredictionTracker
from backend.odds_movement_monitor import OddsMovementMonitor
from backend.market_roi_analyzer import MarketROIAnalyzer

from datetime import datetime
import json


def test_system_components():
    """Test alle system components"""
    print("="*80)
    print("🧪 TESTING ALL SYSTEM COMPONENTS")
    print("="*80)
    
    # Test 1: Aggregator
    print("\n1️⃣ Testing Multi-Source Aggregator...")
    try:
        df = aggregator.run_full_analysis("bundesliga", days_ahead=2)
        if not df.empty:
            print(f"   ✅ Aggregator works! Found {len(df)} matches")
        else:
            print("   ⚠️ No matches found (might be off-season)")
    except Exception as e:
        print(f"   ❌ Aggregator error: {e}")
    
    # Test 2: Ensemble
    print("\n2️⃣ Testing Ensemble Predictor...")
    try:
        ensemble = EnsemblePredictor()
        result = ensemble.predict_ensemble(
            home_xg=2.1,
            away_xg=1.8,
            home_form={'recent_goals': 2.4, 'win_rate': 0.75, 'recent_conceded': 0.8, 'form_points': 2.5},
            away_form={'recent_goals': 2.0, 'win_rate': 0.65, 'recent_conceded': 1.2, 'form_points': 2.2},
            odds={'home': 1.80, 'draw': 3.80, 'away': 4.50, 'over_2.5': 1.65},
            h2h_data=[{'home_score': 2, 'away_score': 1, 'date': '2024-09-01'}]
        )
        if 'ensemble' in result:
            print(f"   ✅ Ensemble works! Confidence: {result['confidence']:.1%}")
        else:
            print(f"   ❌ Ensemble error: {result}")
    except Exception as e:
        print(f"   ❌ Ensemble error: {e}")
    
    # Test 3: Bankroll
    print("\n3️⃣ Testing Bankroll Manager...")
    try:
        bankroll = BankrollManager(1000, 'moderate')
        rec = bankroll.get_stake_recommendation(
            probability=0.75,
            odds=1.85,
            market='Over 2.5',
            match='Test Match'
        )
        if 'stake' in rec:
            print(f"   ✅ Bankroll works! Recommends €{rec['stake']:.2f} stake")
        else:
            print(f"   ❌ Bankroll error: {rec}")
    except Exception as e:
        print(f"   ❌ Bankroll error: {e}")
    
    # Test 4: Tracker
    print("\n4️⃣ Testing Prediction Tracker...")
    try:
        tracker = PredictionTracker()
        tracker.log_prediction(
            match_id='TEST_001',
            match_name='Test Match',
            match_date='2025-11-01',
            market='Over 2.5',
            prediction='Yes',
            probability=0.75,
            odds=1.85,
            confidence=0.82
        )
        stats = tracker.get_performance_summary()
        print(f"   ✅ Tracker works! Total predictions: {stats['total_predictions']}")
    except Exception as e:
        print(f"   ❌ Tracker error: {e}")
    
    # Test 5: Odds Monitor
    print("\n5️⃣ Testing Odds Monitor...")
    try:
        monitor = OddsMovementMonitor()
        monitor.log_odds(
            match_id='TEST_001',
            match_name='Test Match',
            match_date='2025-11-01',
            market='Over 2.5',
            odds=1.85,
            probability=0.75
        )
        alerts = monitor.get_active_alerts(hours=24)
        print(f"   ✅ Monitor works! Active alerts: {len(alerts)}")
    except Exception as e:
        print(f"   ❌ Monitor error: {e}")
    
    # Test 6: ROI Analyzer
    print("\n6️⃣ Testing ROI Analyzer...")
    try:
        roi = MarketROIAnalyzer()
        roi.log_bet(
            market='Over 2.5',
            stake=100,
            odds=1.85,
            won=True,
            match='Test Match'
        )
        summary = roi.get_overall_summary()
        if 'total_bets' in summary:
            print(f"   ✅ ROI Analyzer works! Total bets: {summary['total_bets']}")
        else:
            print(f"   ⚠️ ROI needs more data: {summary}")
    except Exception as e:
        print(f"   ❌ ROI error: {e}")
    
    print("\n" + "="*80)
    print("✅ COMPONENT TESTING COMPLETE")
    print("="*80)


def run_production_analysis(league='bundesliga', days_ahead=2):
    """Run full production analysis"""
    print("\n" + "="*80)
    print("🚀 RUNNING PRODUCTION ANALYSIS")
    print("="*80)
    
    try:
        # Get predictions
        df = aggregator.run_full_analysis(league, days_ahead)
        
        if df.empty:
            print("⚠️ No matches found. Try another league or check API status.")
            return None
        
        print(f"\n✅ Found {len(df)} matches!")
        
        # Initialize systems
        bankroll = BankrollManager(1000, 'moderate')
        tracker = PredictionTracker()
        odds_monitor = OddsMovementMonitor()
        roi_analyzer = MarketROIAnalyzer()
        
        recommendations = []
        
        for _, match in df.iterrows():
            match_id = f"{league}_{match['match']}_{match['match_date']}"
            
            # Get stake recommendation
            stake_rec = bankroll.get_stake_recommendation(
                probability=float(match['p_home_win'].strip('%')) / 100,
                odds=float(match['odds_1x2'].split(' / ')[0]),
                market='Home Win',
                match=match['match']
            )
            
            # Log to tracker
            tracker.log_prediction(
                match_id=match_id,
                match_name=match['match'],
                match_date=match['match_date'],
                market='Match Result',
                prediction=match['prediction'],
                probability=float(match['p_home_win'].strip('%')) / 100 if match['prediction'] == 'Home Win' else 
                           float(match['p_away_win'].strip('%')) / 100,
                odds=float(match['odds_1x2'].split(' / ')[0]) if match['prediction'] == 'Home Win' else
                     float(match['odds_1x2'].split(' / ')[2]),
                confidence=float(match['confidence'].strip('%')) / 100
            )
            
            # Monitor odds
            odds_monitor.log_odds(
                match_id=match_id,
                match_name=match['match'],
                match_date=match['match_date'],
                market='Home Win',
                odds=float(match['odds_1x2'].split(' / ')[0]),
                probability=float(match['p_home_win'].strip('%')) / 100
            )
            
            recommendations.append({
                'match': match['match'],
                'date': f"{match['match_date']} {match['match_time']}",
                'prediction': match['prediction'],
                'confidence': match['confidence'],
                'odds': match['odds_1x2'],
                'best_bet': match['best_bet'],
                'stake': f"€{stake_rec['stake']:.2f}",
                'expected_return': f"€{stake_rec['expected_return']:.2f}"
            })
        
        # Print recommendations
        print("\n" + "="*80)
        print("💰 INTELLIGENT BETTING RECOMMENDATIONS")
        print("="*80)
        
        for rec in recommendations:
            print(f"\n⚽ {rec['match']}")
            print(f"   📅 {rec['date']}")
            print(f"   🎯 {rec['prediction']} ({rec['confidence']} confidence)")
            print(f"   💎 {rec['best_bet']}")
            print(f"   💰 Recommended Stake: {rec['stake']}")
            print(f"   📈 Expected Return: {rec['expected_return']}")
        
        # Get alerts
        alerts = odds_monitor.get_active_alerts(hours=24)
        if alerts:
            print("\n" + "="*80)
            print("🚨 ACTIVE ALERTS")
            print("="*80)
            for alert in alerts[:5]:
                print(f"\n{alert['emoji']} {alert['match_name']}")
                print(f"   {alert['market']}: {alert['old_odds']} → {alert['new_odds']} ({alert['movement_pct']:+.1f}%)")
        
        # Bankroll status
        stats = bankroll.get_statistics()
        print("\n" + "="*80)
        print("💰 BANKROLL STATUS")
        print("="*80)
        print(f"Current: €{stats['current_bankroll']:.2f}")
        print(f"ROI: {stats['roi']:+.2%}")
        print(f"Win Rate: {stats['win_rate']:.1%}")
        
        # Export
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_data = {
            'timestamp': timestamp,
            'league': league,
            'recommendations': recommendations,
            'bankroll_status': stats
        }
        
        os.makedirs('data', exist_ok=True)
        with open(f'data/production_analysis_{timestamp}.json', 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"\n💾 Analysis exported to: data/production_analysis_{timestamp}.json")
        
        return export_data
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Test all components
    test_system_components()
    
    # Run production analysis
    print("\n" * 2)
    result = run_production_analysis('bundesliga', days_ahead=2)
    
    if result:
        print("\n" + "="*80)
        print("✅ SYSTEM READY FOR PRODUCTION!")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("⚠️ Check errors above and fix")
        print("="*80)
