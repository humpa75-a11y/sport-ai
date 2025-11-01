"""
🎯 TEST VALUE BETTING ENGINE - Demonstratie
=============================================
Test de nieuwe Poisson Value Engine met PROFESSOR DE MEESTER

Dit script test:
1. Single match value analyse
2. Batch analyse (meerdere wedstrijden)
3. Accumulator suggesties
4. Expected Value berekeningen
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def print_section(title):
    """Print mooie sectie header"""
    print("\n" + "="*80)
    print(f"🎯 {title}")
    print("="*80)


def test_single_match_value_betting():
    """Test 1: Single Match Value Analyse"""
    print_section("TEST 1: SINGLE MATCH VALUE BETTING")
    
    # Ajax vs PSV met live odds
    match_data = {
        "home_team": "Ajax",
        "away_team": "PSV",
        "odds_1x2": [2.10, 3.50, 3.20],  # Home, Draw, Away
        "odds_markets": {
            "over_2_5": 1.80,
            "btts": 1.75,
            "over_1_5": 1.35,
            "under_2_5": 2.00,
            "over_3_5": 2.50
        },
        "speelronde": 12
    }
    
    print("\n📊 MATCH DATA:")
    print(f"   {match_data['home_team']} vs {match_data['away_team']}")
    print(f"   Odds: {match_data['odds_1x2'][0]} | {match_data['odds_1x2'][1]} | {match_data['odds_1x2'][2]}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/value-betting", json=match_data)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ ANALYSE COMPLEET!")
            print(f"\n🎓 PROFESSOR VOORSPELLING:")
            pred = result['professor_prediction']
            print(f"   Expected Goals: {pred['home_goals']:.2f} - {pred['away_goals']:.2f}")
            print(f"   Total Goals: {pred['total_goals']:.2f}")
            
            print(f"\n🎲 SIMULATIE STATISTIEKEN (100 runs):")
            sim = result['simulation_stats']
            print(f"   Home Win: {sim['p_home_win']*100:.1f}%")
            print(f"   Draw: {sim['p_draw']*100:.1f}%")
            print(f"   Away Win: {sim['p_away_win']*100:.1f}%")
            print(f"   Over 2.5: {sim['p_over_2_5']*100:.1f}%")
            print(f"   BTTS: {sim['p_btts_yes']*100:.1f}%")
            
            print(f"\n💎 VALUE BETS GEVONDEN: {len(result['value_bets'])}")
            for i, bet in enumerate(result['value_bets'][:5], 1):
                print(f"   {i}. {bet['bet']} @ {bet['odds']} → EV: +{bet['ev_percentage']:.1f}% ({bet['probability']*100:.1f}% kans)")
            
            if result.get('best_accumulator'):
                acca = result['best_accumulator']
                print(f"\n🎰 BESTE ACCUMULATOR ({acca['num_bets']}-fold):")
                print(f"   Total Odds: {acca['total_odds']}x")
                print(f"   Win Kans: {acca['win_probability_pct']:.2f}%")
                print(f"   €10 → €{acca['potential_win']:.2f}")
            
            print(f"\n💡 BETTING ADVIES:")
            advice = result['betting_advice']
            print(f"   {advice['advice']}")
            print(f"   Risk: {advice['risk_level']}")
            print(f"   Beste Bet: {advice['best_bet']}")
            print(f"   Strategie: {advice['strategy']}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False
    
    except Exception as e:
        print(f"❌ FOUT: {e}")
        return False


def test_batch_value_betting():
    """Test 2: Batch Analyse (hele speeldag)"""
    print_section("TEST 2: BATCH VALUE BETTING - EREDIVISIE SPEELRONDE")
    
    # Eredivisie speelronde met live odds
    batch_data = {
        "matches": [
            {
                "home_team": "Ajax",
                "away_team": "PSV",
                "odds_1x2": [2.10, 3.50, 3.20]
            },
            {
                "home_team": "Feyenoord",
                "away_team": "AZ",
                "odds_1x2": [1.80, 3.60, 4.20]
            },
            {
                "home_team": "FC Twente",
                "away_team": "FC Utrecht",
                "odds_1x2": [2.00, 3.40, 3.80]
            },
            {
                "home_team": "SC Heerenveen",
                "away_team": "Go Ahead Eagles",
                "odds_1x2": [1.90, 3.50, 4.00]
            }
        ],
        "speelronde": 12
    }
    
    print(f"\n📊 ANALYSEREN VAN {len(batch_data['matches'])} WEDSTRIJDEN...")
    
    try:
        response = requests.post(f"{BASE_URL}/api/value-betting/batch", json=batch_data)
        
        if response.status_code == 200:
            report = response.json()
            
            print(f"\n✅ BATCH RAPPORT GEGENEREERD!")
            print(f"\n📈 SAMENVATTING:")
            summary = report['summary']
            print(f"   Matches Analyzed: {report['total_matches_analyzed']}")
            print(f"   Value Bets Found: {report['total_value_bets_found']}")
            print(f"   Average EV: +{summary['average_ev']*100:.1f}%")
            print(f"   Markets Covered: {summary['total_markets_covered']}")
            
            print(f"\n💎 TOP 5 SINGLE BETS:")
            for i, bet in enumerate(report['top_single_bets'][:5], 1):
                print(f"   {i}. {bet['match']}")
                print(f"      → {bet['bet']} @ {bet['odds']} | EV: +{bet['ev_percentage']:.1f}% | Kans: {bet['probability']*100:.1f}%")
            
            print(f"\n🎰 AANBEVOLEN ACCUMULATORS:")
            for i, acca in enumerate(report['recommended_accumulators'][:3], 1):
                print(f"\n   {i}. {acca['type']} Accumulator:")
                print(f"      Total Odds: {acca['total_odds']}x | Win Kans: {acca['win_probability_pct']:.2f}%")
                print(f"      €10 → €{acca['potential_win']:.2f} (Expected: €{acca['expected_return']:.2f})")
                print(f"      Bets:")
                for bet in acca['bets']:
                    print(f"         • {bet['match']}: {bet['bet']} @ {bet['odds']}")
            
            if summary.get('best_ev_bet'):
                best = summary['best_ev_bet']
                print(f"\n🏆 BESTE VALUE BET VAN DE RONDE:")
                print(f"   {best['match']}")
                print(f"   → {best['bet']} @ {best['odds']}")
                print(f"   → EV: +{best['ev_percentage']:.1f}% | Kans: {best['probability']*100:.1f}%")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False
    
    except Exception as e:
        print(f"❌ FOUT: {e}")
        return False


def test_bundesliga_example():
    """Test 3: Reproduceer de Duitse Bundesliga analyse"""
    print_section("TEST 3: BUNDESLIGA 30 OKT 2025 (uit jouw voorbeeld)")
    
    bundesliga_data = {
        "matches": [
            {
                "home_team": "RB Leipzig",
                "away_team": "VfB Stuttgart",
                "odds_1x2": [2.00, 3.90, 3.40]
            },
            {
                "home_team": "Heidenheim",
                "away_team": "Eintracht Frankfurt",
                "odds_1x2": [3.60, 4.00, 1.90]
            },
            {
                "home_team": "Union Berlin",
                "away_team": "SC Freiburg",
                "odds_1x2": [2.50, 3.30, 2.75]
            },
            {
                "home_team": "Mainz",
                "away_team": "Werder Bremen",
                "odds_1x2": [1.95, 3.90, 3.50]
            }
        ],
        "speelronde": 8
    }
    
    print(f"\n📊 ANALYSEREN VAN {len(bundesliga_data['matches'])} BUNDESLIGA WEDSTRIJDEN...")
    print("   (Vergelijkbaar met jouw originele Python script)")
    
    try:
        response = requests.post(f"{BASE_URL}/api/value-betting/batch", json=bundesliga_data)
        
        if response.status_code == 200:
            report = response.json()
            
            print(f"\n✅ BUNDESLIGA ANALYSE COMPLEET!")
            print(f"\n🎯 BESTE 4-FOLD ACCUMULATOR:")
            
            # Zoek de 4-fold
            acca_4 = next((a for a in report['recommended_accumulators'] if a['type'] == '4-Fold'), None)
            if acca_4:
                print(f"   Total Odds: {acca_4['total_odds']}x")
                print(f"   Win Kans: {acca_4['win_probability_pct']:.2f}%")
                print(f"   €10 → €{acca_4['potential_win']:.0f}")
                print(f"\n   Bets:")
                for bet in acca_4['bets']:
                    print(f"      • {bet['match']}: {bet['bet']} @ {bet['odds']} ({bet['probability']*100:.1f}% kans)")
            
            print(f"\n🔥 MONSTER 7-FOLD:")
            acca_7 = next((a for a in report['recommended_accumulators'] if a['type'] == '7-Fold'), None)
            if acca_7:
                print(f"   Total Odds: {acca_7['total_odds']}x")
                print(f"   Win Kans: {acca_7['win_probability_pct']:.2f}%")
                print(f"   €1 → €{acca_7['potential_win']:.0f}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ FOUT: {e}")
        return False


def main():
    """Run alle tests"""
    print("\n" + "="*80)
    print("🎯 POISSON VALUE ENGINE - TEST SUITE")
    print("="*80)
    print("\nDeze test demonstreert de nieuwe value betting functionaliteit")
    print("Zorg dat de Flask backend draait op http://127.0.0.1:5000\n")
    
    # Check server
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code != 200:
            print("❌ Server niet bereikbaar! Start eerst: python backend/app.py")
            return
    except:
        print("❌ Server niet bereikbaar! Start eerst: python backend/app.py")
        return
    
    results = []
    
    # Test 1: Single Match
    results.append(("Single Match Value Betting", test_single_match_value_betting()))
    
    # Test 2: Batch Analysis
    results.append(("Batch Value Betting", test_batch_value_betting()))
    
    # Test 3: Bundesliga Example
    results.append(("Bundesliga Example", test_bundesliga_example()))
    
    # Summary
    print_section("TEST RESULTATEN")
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {status} - {test_name}")
    
    print("\n" + "="*80)
    print("🎉 TEST SUITE COMPLEET!")
    print("="*80)
    
    if all(r[1] for r in results):
        print("\n✅ ALLE TESTS GESLAAGD - VALUE ENGINE WERKT PERFECT!")
        print("\n💡 GEBRUIK:")
        print("   • /api/value-betting → Single match analyse")
        print("   • /api/value-betting/batch → Meerdere matches tegelijk")
        print("\n🎯 INTEGRATIE MET PROFESSOR DE MEESTER:")
        print("   De value engine gebruikt PROFESSOR voorspellingen voor Expected Goals")
        print("   Combineert Poisson simulaties met Expected Value berekeningen")
        print("   Detecteert automatisch value bets (EV > 0.05)")
    else:
        print("\n⚠️ SOMMIGE TESTS GEFAALD - Check de errors hierboven")


if __name__ == '__main__':
    main()
