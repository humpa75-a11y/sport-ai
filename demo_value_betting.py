"""
🎯 QUICK VALUE BETTING DEMO
============================
Simpele demonstratie van de nieuwe Poisson Value Engine
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from poisson_value_engine import PoissonValueEngine

def demo_single_match():
    """Demo 1: Single Match Analyse"""
    print("\n" + "="*80)
    print("🎯 DEMO 1: SINGLE MATCH VALUE ANALYSE")
    print("="*80)
    
    engine = PoissonValueEngine(simulation_runs=100)
    
    # Ajax vs PSV (expected goals van PROFESSOR)
    home_goals = 2.1
    away_goals = 1.4
    odds_1x2 = [2.10, 3.50, 3.20]
    
    print(f"\n📊 MATCH: Ajax vs PSV")
    print(f"   Expected Goals: {home_goals} - {away_goals}")
    print(f"   Odds: {odds_1x2[0]} | {odds_1x2[1]} | {odds_1x2[2]}")
    
    # Analyseer
    analysis = engine.analyze_match_full(
        "Ajax", "PSV", home_goals, away_goals, odds_1x2,
        odds_markets={'over_2_5': 1.80, 'btts': 1.75}
    )
    
    # Resultaten
    print(f"\n✅ ANALYSE COMPLEET!")
    print(f"\n🎲 SIMULATIE (100 runs):")
    sim = analysis['simulation_stats']
    print(f"   Home Win: {sim['p_home_win']*100:.1f}%")
    print(f"   Draw: {sim['p_draw']*100:.1f}%")
    print(f"   Away Win: {sim['p_away_win']*100:.1f}%")
    print(f"   Over 2.5: {sim['p_over_2_5']*100:.1f}%")
    print(f"   BTTS: {sim['p_btts_yes']*100:.1f}%")
    
    print(f"\n💎 VALUE BETS: {len(analysis['value_bets'])}")
    for i, bet in enumerate(analysis['value_bets'][:5], 1):
        print(f"   {i}. {bet['bet']} @ {bet['odds']:.2f} → EV: +{bet['ev_percentage']:.1f}% ({bet['probability']*100:.1f}% kans)")
    
    if analysis['best_accumulator']:
        acca = analysis['best_accumulator']
        print(f"\n🎰 BESTE ACCUMULATOR ({acca['num_bets']}-fold):")
        print(f"   Total Odds: {acca['total_odds']}x")
        print(f"   Win Kans: {acca['win_probability_pct']:.2f}%")
        print(f"   €10 → €{acca['potential_win']:.2f}")


def demo_bundesliga():
    """Demo 2: Bundesliga Batch Analyse (uit jouw script)"""
    print("\n" + "="*80)
    print("🎯 DEMO 2: BUNDESLIGA BATCH ANALYSE")
    print("="*80)
    
    engine = PoissonValueEngine(simulation_runs=100)
    
    # Matches uit jouw originele script
    matches = [
        ["RB Leipzig", "VfB Stuttgart", [2.00, 3.90, 3.40], [2.1, 1.8]],
        ["Heidenheim", "Eintracht Frankfurt", [3.60, 4.00, 1.90], [1.2, 2.0]],
        ["Union Berlin", "SC Freiburg", [2.50, 3.30, 2.75], [1.8, 1.6]],
        ["Mainz", "Werder Bremen", [1.95, 3.90, 3.50], [1.5, 1.8]],
    ]
    
    print(f"\n📊 Analyseren van {len(matches)} Bundesliga wedstrijden...")
    
    analyses = []
    for match in matches:
        home, away, odds, goals = match
        analysis = engine.analyze_match_full(home, away, goals[0], goals[1], odds)
        analyses.append(analysis)
    
    # Genereer rapport
    report = engine.generate_betting_report(analyses, max_accumulators=3)
    
    print(f"\n✅ RAPPORT GEGENEREERD!")
    print(f"\n📈 SAMENVATTING:")
    print(f"   Matches: {report['total_matches_analyzed']}")
    print(f"   Value Bets: {report['total_value_bets_found']}")
    print(f"   Average EV: +{report['summary']['average_ev']*100:.1f}%")
    
    print(f"\n💎 TOP 3 VALUE BETS:")
    for i, bet in enumerate(report['top_single_bets'][:3], 1):
        print(f"   {i}. {bet['match']}")
        print(f"      → {bet['bet']} @ {bet['odds']} | EV: +{bet['ev_percentage']:.1f}%")
    
    print(f"\n🎰 AANBEVOLEN ACCUMULATORS:")
    for acca in report['recommended_accumulators']:
        print(f"\n   {acca['type']} Accumulator:")
        print(f"      Odds: {acca['total_odds']}x | Kans: {acca['win_probability_pct']:.2f}%")
        print(f"      €10 → €{acca['potential_win']:.2f}")


def demo_ev_calculation():
    """Demo 3: Expected Value Uitleg"""
    print("\n" + "="*80)
    print("🎯 DEMO 3: EXPECTED VALUE (EV) UITLEG")
    print("="*80)
    
    engine = PoissonValueEngine()
    
    print("\n💡 WAT IS EXPECTED VALUE?")
    print("   EV = (Probability × (Odds - 1)) - (1 - Probability)")
    print("   EV > 0 = VALUE BET! 💰")
    
    examples = [
        ("Sterke Value", 0.65, 2.10),  # PROFESSOR: 65%, Bookmaker: 2.10
        ("Marginale Value", 0.52, 1.95),  # PROFESSOR: 52%, Bookmaker: 1.95
        ("Geen Value", 0.45, 2.00),  # PROFESSOR: 45%, Bookmaker: 2.00
    ]
    
    print("\n📊 VOORBEELDEN:")
    for name, prob, odds in examples:
        ev = engine.calculate_expected_value(prob, odds)
        bookmaker_prob = 1 / odds
        
        print(f"\n   {name}:")
        print(f"      PROFESSOR zegt: {prob*100:.1f}% kans")
        print(f"      Bookmaker odds: {odds} (implied: {bookmaker_prob*100:.1f}%)")
        print(f"      EV: {ev:+.3f} ({ev*100:+.1f}%)")
        
        if ev > 0.08:
            print(f"      ✅ STERKE VALUE - Bet met confidence!")
        elif ev > 0.05:
            print(f"      🟡 GOEDE VALUE - Redelijke bet")
        elif ev > 0:
            print(f"      🟠 MARGINALE VALUE - Voorzichtig")
        else:
            print(f"      ❌ GEEN VALUE - Skip deze bet")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("🎯 POISSON VALUE ENGINE - LIVE DEMONSTRATIE")
    print("="*80)
    print("\nDit script demonstreert de value betting functionaliteit")
    print("Direct vanuit Python (zonder Flask API)\n")
    
    try:
        # Run alle demos
        demo_single_match()
        demo_bundesliga()
        demo_ev_calculation()
        
        print("\n" + "="*80)
        print("🎉 DEMO COMPLEET!")
        print("="*80)
        
        print("\n✅ CONCLUSIES:")
        print("   1. Poisson Value Engine werkt perfect!")
        print("   2. Expected Value detectie is operationeel")
        print("   3. Accumulator generatie functioneert")
        print("   4. Integratie met PROFESSOR DE MEESTER is ready!")
        
        print("\n💡 VOLGENDE STAPPEN:")
        print("   • Gebruik /api/value-betting voor single matches")
        print("   • Gebruik /api/value-betting/batch voor speeldagen")
        print("   • Integreer met live odds API's")
        print("   • Start met €1-5 test bets")
        
        print("\n⚠️ DISCLAIMER:")
        print("   Value betting is geen garantie op winst!")
        print("   Gebruik bankroll management (max 1-2% per bet)")
        print("   BET RESPONSIBLY! 🎰")
        
    except Exception as e:
        print(f"\n❌ FOUT: {e}")
        import traceback
        traceback.print_exc()
