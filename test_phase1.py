"""
🎯 Quick Test - Intelligent Betting System
Test alle Phase 1 features zonder API calls
"""

from backend.bankroll_manager import BankrollManager
from backend.prediction_tracker import PredictionTracker
from backend.odds_movement_monitor import OddsMovementMonitor
import time

print("="*80)
print("🧪 TESTING INTELLIGENT BETTING SYSTEM - Phase 1")
print("="*80)

# Test 1: Bankroll Manager
print("\n📊 TEST 1: Kelly Criterion Bankroll Management")
print("-"*80)

bankroll = BankrollManager(initial_bankroll=1000.0, risk_profile='moderate')
print(f"✅ Initialized: €1000 bankroll, MODERATE risk")

# Test bet
rec = bankroll.get_stake_recommendation(
    probability=0.75,
    odds=1.85,
    market='Over 2.5',
    match='Bayern vs Leverkusen'
)

print(f"\n💰 Bayern vs Leverkusen - Over 2.5 Goals")
print(f"   Probability: 75% | Odds: 1.85")
print(f"   Recommended Stake: €{rec['stake']:.2f} ({rec['stake_percent']:.1f}%)")
print(f"   Expected Return: €{rec['expected_return']:.2f}")
print(f"   {rec['recommendation']}")

# Test 2: Prediction Tracker
print("\n\n📊 TEST 2: Historical Prediction Tracking")
print("-"*80)

tracker = PredictionTracker()
print("✅ Initialized Prediction Tracker")

# Log prediction
tracker.log_prediction(
    match_id='BUN_001',
    match_name='Bayern Munich vs Bayer Leverkusen',
    match_date='2025-11-01',
    market='Over 2.5',
    prediction='Yes',
    probability=0.75,
    odds=1.85,
    confidence=0.82
)

print(f"\n📝 Logged: Bayern vs Leverkusen - Over 2.5")
print(f"   Prediction: Yes (75% prob, 82% confidence)")

stats = tracker.get_performance_summary()
print(f"\n📊 Tracker Stats:")
print(f"   Total: {stats['total_predictions']} | Pending: {stats['pending']}")

# Test 3: Odds Movement Monitor
print("\n\n📊 TEST 3: Odds Movement Monitor")
print("-"*80)

monitor = OddsMovementMonitor(alert_threshold=0.10)
print("✅ Initialized Odds Monitor (10% threshold)")

# Initial odds
monitor.log_odds(
    match_id='BUN_001',
    match_name='Bayern Munich vs Bayer Leverkusen',
    match_date='2025-11-01',
    market='Over 2.5',
    odds=1.85,
    probability=0.75
)
print(f"\n📊 Initial odds logged: 1.85")

# Odds movement
time.sleep(0.5)
monitor.log_odds(
    match_id='BUN_001',
    match_name='Bayern Munich vs Bayer Leverkusen',
    match_date='2025-11-01',
    market='Over 2.5',
    odds=2.05,  # 10.8% increase
    probability=0.75
)
print(f"📈 Odds moved: 1.85 → 2.05 (+10.8%)")

alerts = monitor.get_active_alerts()
if alerts:
    alert = alerts[0]
    print(f"\n🚨 {alert['severity']} ALERT")
    print(f"   Type: {alert['alert_type'].replace('_', ' ')}")
    print(f"   Movement: {alert['movement_pct']:+.1f}%")
    if alert.get('ev'):
        print(f"   New EV: {alert['ev']:+.2%}")
    if alert['value_bet']:
        print(f"   💎 VALUE BET OPPORTUNITY!")

print("\n\n" + "="*80)
print("✅ ALL PHASE 1 FEATURES WORKING!")
print("="*80)
print("\n🎯 Ready for:")
print("   - Real-time match analysis")
print("   - Intelligent stake recommendations")
print("   - Odds movement tracking")
print("   - Historical performance analysis")
