"""
🔥 DEMO: Multi-Source Data Aggregator

Test run met sample Bundesliga data
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.multi_source_aggregator import *
import pandas as pd

# =============================================
# DEMO DATA: Bundesliga Speelronde 10
# =============================================
def get_demo_bundesliga_matches():
    """Sample Bundesliga matches voor demo"""
    return pd.DataFrame([
        {
            'home': 'Bayern Munich',
            'away': 'Bayer Leverkusen',
            'time': '15:30',
            'tournament': 'Bundesliga',
            'home_xg': 2.8,
            'away_xg': 1.2,
            'form_home': 'W-W-W-D-W',
            'form_away': 'W-D-W-W-L'
        },
        {
            'home': 'RB Leipzig',
            'away': 'VfB Stuttgart',
            'time': '18:30',
            'tournament': 'Bundesliga',
            'home_xg': 2.1,
            'away_xg': 1.8,
            'form_home': 'W-W-D-L-W',
            'form_away': 'D-W-W-L-D'
        },
        {
            'home': 'Union Berlin',
            'away': 'SC Freiburg',
            'time': '15:30',
            'tournament': 'Bundesliga',
            'home_xg': 1.6,
            'away_xg': 1.4,
            'form_home': 'L-D-W-L-D',
            'form_away': 'W-D-D-W-L'
        },
        {
            'home': 'Heidenheim',
            'away': 'Eintracht Frankfurt',
            'time': '18:30',
            'tournament': 'Bundesliga',
            'home_xg': 1.2,
            'away_xg': 2.3,
            'form_home': 'L-L-D-W-L',
            'form_away': 'W-W-W-D-W'
        },
        {
            'home': 'Borussia Dortmund',
            'away': 'FC Koln',
            'time': '15:30',
            'tournament': 'Bundesliga',
            'home_xg': 2.5,
            'away_xg': 1.1,
            'form_home': 'W-D-W-W-L',
            'form_away': 'L-L-D-L-W'
        }
    ])

# =============================================
# RUN DEMO
# =============================================
print("="*80)
print("🎮 DEMO MODE: Multi-Source Aggregator")
print("="*80)
print("Test met 5 Bundesliga wedstrijden\n")

# Get sample matches
df = get_demo_bundesliga_matches()

results = []
for idx, row in df.iterrows():
    match = f"{row['home']} vs {row['away']}"
    print(f"📊 Analyseren: {match} | {row['time']} CET")
    
    # Haal data van alle bronnen
    odds = get_flashscore_odds(match)
    pred = get_predictz_prediction(match)
    stats = get_footystats_stats(match)
    lineup = get_whoscored_lineup(match)
    inj_home = get_espn_injuries(row['home'])
    inj_away = get_espn_injuries(row['away'])
    fb_xg = get_fbref_xg(match)
    
    # Simulatie
    sim = simulate_match(fb_xg[0], fb_xg[1], runs=100)  # 100 runs voor demo
    
    # EV calculations
    ev_home = calculate_ev(sim['p_home_win'], odds[0])
    ev_draw = calculate_ev(sim['p_draw'], odds[1])
    ev_away = calculate_ev(sim['p_away_win'], odds[2])
    ev_over = calculate_ev(sim['p_over_25'], 1.80)
    ev_btts = calculate_ev(sim['p_btts'], 1.75)
    
    # Beste bet
    max_ev = max(ev_home, ev_draw, ev_away, ev_over, ev_btts)
    bet = "Geen value"
    
    if max_ev > 0.05:
        if max_ev == ev_home:
            bet = f"Home Win @ {odds[0]} (EV: +{ev_home:.2f})"
        elif max_ev == ev_draw:
            bet = f"Draw @ {odds[1]} (EV: +{ev_draw:.2f})"
        elif max_ev == ev_away:
            bet = f"Away Win @ {odds[2]} (EV: +{ev_away:.2f})"
        elif max_ev == ev_over:
            bet = f"Over 2.5 @ 1.80 (EV: +{ev_over:.2f})"
        elif max_ev == ev_btts:
            bet = f"BTTS Yes @ 1.75 (EV: +{ev_btts:.2f})"
    
    print(f"   Odds: {odds[0]:.2f} / {odds[1]:.2f} / {odds[2]:.2f}")
    print(f"   Sim:  {sim['p_home_win']:.0%} / {sim['p_draw']:.0%} / {sim['p_away_win']:.0%}")
    print(f"   💎 Best Bet: {bet}")
    print()
    
    results.append({
        'match': match,
        'time': row['time'],
        'odds': f"{odds[0]}/{odds[1]}/{odds[2]}",
        'sim_result': f"{sim['p_home_win']:.0%}/{sim['p_draw']:.0%}/{sim['p_away_win']:.0%}",
        'btts': f"{sim['p_btts']:.0%}",
        'over25': f"{sim['p_over_25']:.0%}",
        'best_bet': bet,
        'ev': max_ev,
        'injuries': f"H:{inj_home} / A:{inj_away}"
    })

result_df = pd.DataFrame(results)

# =============================================
# 4-FOLD ACCUMULATOR
# =============================================
print("="*80)
print("🎯 VALUE BETS & ACCUMULATOR")
print("="*80)

value_bets = result_df[result_df['ev'] > 0.05].sort_values('ev', ascending=False)

if len(value_bets) >= 4:
    print("\n💰 TOP 4-FOLD ACCUMULATOR:")
    top_4 = value_bets.head(4)
    total_odds = 1.0
    combined_prob = 1.0
    
    for idx, bet in enumerate(top_4.iterrows(), 1):
        _, row = bet
        bet_str = row['best_bet']
        
        # Extract odds
        if '@' in bet_str:
            try:
                odds_val = float(bet_str.split('@')[1].split('(')[0].strip())
                total_odds *= odds_val
                
                # Estimate hit prob
                sim_probs = row['sim_result'].split('/')
                if 'Home Win' in bet_str:
                    prob = float(sim_probs[0].strip('%')) / 100
                elif 'Away Win' in bet_str:
                    prob = float(sim_probs[2].strip('%')) / 100
                elif 'Draw' in bet_str:
                    prob = float(sim_probs[1].strip('%')) / 100
                elif 'Over' in bet_str:
                    prob = float(row['over25'].strip('%')) / 100
                elif 'BTTS' in bet_str:
                    prob = float(row['btts'].strip('%')) / 100
                else:
                    prob = 0.5
                
                combined_prob *= prob
                
                print(f"  {idx}. {row['match']}")
                print(f"     → {bet_str}")
            except:
                pass
    
    print(f"\n  📊 Combined Odds: {total_odds:.2f}x")
    print(f"  🎯 Hit Probability: {combined_prob:.1%}")
    print(f"  💵 €10 stake → €{total_odds * 10:.2f}")
    print(f"  📈 Expected Return: €{(total_odds * combined_prob * 10):.2f}")
    print(f"  💎 Net EV: €{(total_odds * combined_prob * 10) - 10:.2f}")

print("\n" + "="*80)
print("📋 COMPLETE RESULTS:")
print("="*80)
print(result_df[['match', 'time', 'odds', 'best_bet']].to_string(index=False))

print("\n✅ DEMO COMPLEET - Data van 7 bronnen geaggregeerd!")
print("="*80)
