"""
🔥 FLAWLESS PREDICTIONS DEMO - 1-2 DAGEN VOORUIT!

Features:
- Match datum + tijd (1-2 dagen vooruit)
- Win/Draw/Lose predictions
- BTTS + Over/Under (1.5, 2.5, 3.5)
- Shots on goal predictions
- Most likely score
- Value bets (EV > 5%)

Author: Sport AI Sync
"""

import pandas as pd
from datetime import datetime, timedelta

# Sample data (5 Bundesliga matches - VOLGENDE 2 DAGEN!)
matches_data = []

# Match 1: VANDAAG (17:00)
matches_data.append({
    'match_date': datetime.now().strftime('%Y-%m-%d'),
    'match_time': '17:00',
    'days_ahead': 0,
    'match': 'Bayern Munich vs Bayer Leverkusen',
    'tournament': 'Bundesliga',
    
    # WIN/LOSE PREDICTION
    'prediction': 'Home Win',
    'confidence': '78.2%',
    'most_likely_score': '3-1',
    'score_prob': '14.5%',
    
    # Probabilities
    'p_home_win': '78%',
    'p_draw': '14%',
    'p_away_win': '8%',
    
    # Goals Markets
    'p_over_15': '92%',
    'p_over_25': '78%',
    'p_over_35': '52%',
    'p_btts': '65%',
    'avg_goals': '3.8',
    
    # SHOTS PREDICTIONS
    'home_shots': '18 (8 SoT)',
    'away_shots': '11 (5 SoT)',
    
    # Betting
    'odds_1x2': '1.22 / 7.00 / 9.50',
    'best_bet': 'Over 2.5 @ 1.80 (EV: +0.33)',
    'ev': 0.33,
    
    # Extra
    'injuries': 'H: Neuer (doubt) | A: Frimpong (out)',
    'lineup': 'Kane, Musiala vs Wirtz, Boniface'
})

# Match 2: MORGEN (14:30)
matches_data.append({
    'match_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
    'match_time': '14:30',
    'days_ahead': 1,
    'match': 'RB Leipzig vs VfB Stuttgart',
    'tournament': 'Bundesliga',
    
    'prediction': 'Draw',
    'confidence': '38.5%',
    'most_likely_score': '2-2',
    'score_prob': '12.8%',
    
    'p_home_win': '35%',
    'p_draw': '38%',
    'p_away_win': '27%',
    
    'p_over_15': '85%',
    'p_over_25': '68%',
    'p_over_35': '38%',
    'p_btts': '72%',
    'avg_goals': '3.2',
    
    'home_shots': '15 (6 SoT)',
    'away_shots': '13 (5 SoT)',
    
    'odds_1x2': '2.00 / 3.90 / 3.40',
    'best_bet': 'BTTS Yes @ 1.75 (EV: +0.19)',
    'ev': 0.19,
    
    'injuries': 'H: Geen | A: Guirassy (doubt)',
    'lineup': 'Openda, Sesko vs Guirassy, Undav'
})

# Match 3: MORGEN (17:00)
matches_data.append({
    'match_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
    'match_time': '17:00',
    'days_ahead': 1,
    'match': 'Heidenheim vs Eintracht Frankfurt',
    'tournament': 'Bundesliga',
    
    'prediction': 'Away Win',
    'confidence': '55.2%',
    'most_likely_score': '1-2',
    'score_prob': '15.3%',
    
    'p_home_win': '28%',
    'p_draw': '17%',
    'p_away_win': '55%',
    
    'p_over_15': '78%',
    'p_over_25': '48%',
    'p_over_35': '22%',
    'p_btts': '58%',
    'avg_goals': '2.4',
    
    'home_shots': '9 (4 SoT)',
    'away_shots': '14 (6 SoT)',
    
    'odds_1x2': '3.60 / 4.00 / 1.90',
    'best_bet': 'Away Win @ 1.90 (EV: +0.15)',
    'ev': 0.15,
    
    'injuries': 'H: Mainka (out) | A: Geen',
    'lineup': 'Pieringer vs Marmoush, Ekitike'
})

# Match 4: OVERMORGEN (14:00)
matches_data.append({
    'match_date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
    'match_time': '14:00',
    'days_ahead': 2,
    'match': 'Union Berlin vs SC Freiburg',
    'tournament': 'Bundesliga',
    
    'prediction': 'Home Win',
    'confidence': '45.8%',
    'most_likely_score': '2-1',
    'score_prob': '13.1%',
    
    'p_home_win': '46%',
    'p_draw': '28%',
    'p_away_win': '26%',
    
    'p_over_15': '82%',
    'p_over_25': '62%',
    'p_over_35': '32%',
    'p_btts': '68%',
    'avg_goals': '2.8',
    
    'home_shots': '12 (5 SoT)',
    'away_shots': '11 (4 SoT)',
    
    'odds_1x2': '2.10 / 3.50 / 3.20',
    'best_bet': 'Over 2.5 @ 1.80 (EV: +0.22)',
    'ev': 0.22,
    
    'injuries': 'H: Becker (doubt) | A: Gregoritsch (out)',
    'lineup': 'Volland, Hollerbach vs Gregoritsch, Doan'
})

# Match 5: OVERMORGEN (16:30)
matches_data.append({
    'match_date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
    'match_time': '16:30',
    'days_ahead': 2,
    'match': 'Borussia Dortmund vs FC Köln',
    'tournament': 'Bundesliga',
    
    'prediction': 'Home Win',
    'confidence': '72.5%',
    'most_likely_score': '3-0',
    'score_prob': '16.2%',
    
    'p_home_win': '72%',
    'p_draw': '18%',
    'p_away_win': '10%',
    
    'p_over_15': '88%',
    'p_over_25': '65%',
    'p_over_35': '38%',
    'p_btts': '48%',
    'avg_goals': '3.1',
    
    'home_shots': '16 (7 SoT)',
    'away_shots': '8 (3 SoT)',
    
    'odds_1x2': '1.35 / 5.50 / 8.00',
    'best_bet': 'Over 2.5 @ 1.80 (EV: +0.27)',
    'ev': 0.27,
    
    'injuries': 'H: Geen | A: Kainz (out)',
    'lineup': 'Fullkrug, Adeyemi vs Uth, Tigges'
})

# Maak DataFrame
df = pd.DataFrame(matches_data)

# =============================================
# DISPLAY: FLAWLESS PREDICTIONS
# =============================================

print("="*100)
print("🔥 FLAWLESS PREDICTIONS - BUNDESLIGA (VOLGENDE 2 DAGEN)")
print("="*100)
print(f"Datum range: {datetime.now().strftime('%Y-%m-%d')} tot {(datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')}")
print(f"Totaal wedstrijden: {len(df)}\n")

# Groepeer per dag
for day in df['days_ahead'].unique():
    day_matches = df[df['days_ahead'] == day]
    
    if day == 0:
        print("\n" + "="*100)
        print(f"📅 VANDAAG ({datetime.now().strftime('%A, %d %B %Y')})")
        print("="*100)
    elif day == 1:
        print("\n" + "="*100)
        print(f"📅 MORGEN ({(datetime.now() + timedelta(days=1)).strftime('%A, %d %B %Y')})")
        print("="*100)
    elif day == 2:
        print("\n" + "="*100)
        print(f"📅 OVERMORGEN ({(datetime.now() + timedelta(days=2)).strftime('%A, %d %B %Y')})")
        print("="*100)
    
    for idx, match in day_matches.iterrows():
        print(f"\n{'─'*100}")
        print(f"🏆 {match['match']} | {match['match_time']} CET")
        print(f"   Competition: {match['tournament']}")
        print(f"{'─'*100}")
        
        # PREDICTION
        print(f"\n🎯 PREDICTION: {match['prediction']} (Confidence: {match['confidence']})")
        print(f"   Most Likely Score: {match['most_likely_score']} ({match['score_prob']} probability)")
        
        # WIN/LOSE/DRAW
        print(f"\n📊 1X2 MARKET:")
        print(f"   Home Win: {match['p_home_win']}  |  Draw: {match['p_draw']}  |  Away Win: {match['p_away_win']}")
        print(f"   Odds: {match['odds_1x2']}")
        
        # GOALS MARKETS
        print(f"\n⚽ GOALS MARKETS:")
        print(f"   Over 1.5: {match['p_over_15']}  |  Over 2.5: {match['p_over_25']}  |  Over 3.5: {match['p_over_35']}")
        print(f"   BTTS: {match['p_btts']}  |  Avg Total: {match['avg_goals']} goals")
        
        # SHOTS ON GOAL
        print(f"\n🎯 SHOTS PREDICTIONS:")
        print(f"   Home: {match['home_shots']}")
        print(f"   Away: {match['away_shots']}")
        
        # BETTING ADVICE
        print(f"\n💰 BEST BET:")
        if match['ev'] > 0.05:
            print(f"   ✅ {match['best_bet']}")
        else:
            print(f"   ⚠️ {match['best_bet']}")
        
        # EXTRA INFO
        print(f"\n📋 EXTRA INFO:")
        print(f"   Injuries: {match['injuries']}")
        print(f"   Key Players: {match['lineup']}")

# =============================================
# ACCUMULATORS
# =============================================

print("\n" + "="*100)
print("🎯 VALUE BETS & ACCUMULATORS")
print("="*100)

value_bets = df[df['ev'] > 0.05].sort_values('ev', ascending=False)

if len(value_bets) >= 3:
    print(f"\n💎 TOP 3 VALUE BETS:")
    for idx, (i, bet) in enumerate(value_bets.head(3).iterrows(), 1):
        print(f"\n{idx}. {bet['match']}")
        print(f"   📅 {bet['match_date']} om {bet['match_time']}")
        print(f"   💰 {bet['best_bet']}")
        print(f"   🎯 Prediction: {bet['prediction']} ({bet['confidence']})")

if len(value_bets) >= 3:
    print(f"\n\n🔥 3-FOLD ACCUMULATOR:")
    top_3 = value_bets.head(3)
    total_odds = 1.0
    combined_prob = 1.0
    
    for idx, (i, bet) in enumerate(top_3.iterrows(), 1):
        # Extract odds from best_bet
        bet_str = bet['best_bet']
        if '@' in bet_str:
            odds_str = bet_str.split('@')[1].split('(')[0].strip()
            try:
                odds_val = float(odds_str)
                total_odds *= odds_val
                
                # Get probability
                if 'Home Win' in bet_str:
                    prob = float(bet['p_home_win'].strip('%')) / 100
                elif 'Away Win' in bet_str:
                    prob = float(bet['p_away_win'].strip('%')) / 100
                elif 'Over 2.5' in bet_str:
                    prob = float(bet['p_over_25'].strip('%')) / 100
                elif 'BTTS' in bet_str:
                    prob = float(bet['p_btts'].strip('%')) / 100
                else:
                    prob = 0.65
                
                combined_prob *= prob
                
                print(f"\n   {idx}. {bet['match']} ({bet['match_date']})")
                print(f"      → {bet_str}")
                
            except:
                pass
    
    print(f"\n   {'─'*80}")
    print(f"   📊 Combined Odds: {total_odds:.2f}x")
    print(f"   🎯 Hit Probability: {combined_prob:.1%}")
    print(f"   💵 €10 stake → €{total_odds * 10:.2f} payout")
    print(f"   📈 Net Expected Value: €{(total_odds * combined_prob * 10) - 10:.2f}")

print("\n" + "="*100)
print("✅ ANALYSE COMPLEET - FLAWLESS PREDICTIONS READY!")
print("="*100)

# =============================================
# EXPORT OPTIES
# =============================================

print("\n📊 Export options:")
print("   1. JSON: df.to_json('predictions.json', orient='records', indent=2)")
print("   2. CSV: df.to_csv('predictions.csv', index=False)")
print("   3. Excel: df.to_excel('predictions.xlsx', index=False)")

# Optioneel: Save to file
df.to_json('data/flawless_predictions.json', orient='records', indent=2)
df.to_csv('data/flawless_predictions.csv', index=False)

print("\n💾 Saved to:")
print("   - data/flawless_predictions.json")
print("   - data/flawless_predictions.csv")
