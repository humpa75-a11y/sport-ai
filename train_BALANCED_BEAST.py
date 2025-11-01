#!/usr/bin/env python3
"""
⚖️ BALANCED BEAST! ⚖️
PERFECT 50/50 MIX: Premier League + Eredivisie

ONTDEKKING: Oude HYPER (10.69%) had 50% PL + 50% Eredivisie!
- Premier League: Defensief, structured, predictable
- Eredivisie: Offensief, wild, doelpunten!
- SAMEN: Perfect balance!

STRATEGIE:
- Gebruik ALLE 3,292 Eredivisie matches
- Gebruik ALLE 4,180 Premier League matches (ongeveer gelijk!)
- TOTAL: 7,472 matches met PERFECT BALANCE!
"""

import pickle
import numpy as np
import json
import os
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

print("="*80)
print("⚖️ BALANCED BEAST - 50/50 PREMIER LEAGUE + EREDIVISIE! ⚖️")
print("="*80)

# Load data
with open('data/mega_training_data.json', 'r', encoding='utf-8') as f:
    all_matches = json.load(f)

# FILTER Premier League + Eredivisie ONLY!
matches = [m for m in all_matches if m.get('league') in ['Premier League', 'Eredivisie']]

# Count per league
pl_count = len([m for m in matches if m.get('league') == 'Premier League'])
eredivisie_count = len([m for m in matches if m.get('league') == 'Eredivisie'])

print(f"✅ {len(all_matches)} totale wedstrijden geladen!")
print(f"✅ {len(matches)} matches gefilterd:")
print(f"   🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League: {pl_count} matches ({pl_count/len(matches)*100:.1f}%)")
print(f"   🇳🇱 Eredivisie: {eredivisie_count} matches ({eredivisie_count/len(matches)*100:.1f}%)")
print(f"   ⚖️ BALANCE: {abs(pl_count - eredivisie_count)} verschil (PERFECT!)")

# Feature engineering (same 12 features as HYPER!)
team_stats = {}

for match in matches:
    for team_type in ['home', 'away']:
        team = match.get(f'{team_type}_team', '')
        if not team:
            continue
        
        if team not in team_stats:
            team_stats[team] = {
                'goals_scored_home': [],
                'goals_conceded_home': [],
                'goals_scored_away': [],
                'goals_conceded_away': [],
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'matches': 0
            }
        
        score = match.get(f'{team_type}_score', 0)
        opp_type = 'away' if team_type == 'home' else 'home'
        opp_score = match.get(f'{opp_type}_score', 0)
        
        team_stats[team][f'goals_scored_{team_type}'].append(score)
        team_stats[team][f'goals_conceded_{team_type}'].append(opp_score)
        team_stats[team]['matches'] += 1
        
        if score > opp_score:
            team_stats[team]['wins'] += 1
        elif score == opp_score:
            team_stats[team]['draws'] += 1
        else:
            team_stats[team]['losses'] += 1

# Calculate aggregate stats
for team in team_stats:
    for location in ['home', 'away']:
        scored = team_stats[team][f'goals_scored_{location}']
        conceded = team_stats[team][f'goals_conceded_{location}']
        team_stats[team][f'avg_goals_scored_{location}'] = np.mean(scored) if scored else 0
        team_stats[team][f'avg_goals_conceded_{location}'] = np.mean(conceded) if conceded else 0

# Build feature matrix (SAME 12 FEATURES AS HYPER!)
X = []
y_home = []
y_away = []

for match in matches:
    home = match.get('home_team', '')
    away = match.get('away_team', '')
    
    if home not in team_stats or away not in team_stats:
        continue
    
    features = [
        # Home team stats (6 features)
        team_stats[home]['avg_goals_scored_home'],
        team_stats[home]['avg_goals_conceded_home'],
        team_stats[home]['wins'] / max(team_stats[home]['matches'], 1),
        team_stats[home]['draws'] / max(team_stats[home]['matches'], 1),
        team_stats[home]['losses'] / max(team_stats[home]['matches'], 1),
        team_stats[home]['matches'],
        
        # Away team stats (6 features)
        team_stats[away]['avg_goals_scored_away'],
        team_stats[away]['avg_goals_conceded_away'],
        team_stats[away]['wins'] / max(team_stats[away]['matches'], 1),
        team_stats[away]['draws'] / max(team_stats[away]['matches'], 1),
        team_stats[away]['losses'] / max(team_stats[away]['matches'], 1),
        team_stats[away]['matches'],
    ]
    
    X.append(features)
    y_home.append(match.get('home_score', 0))
    y_away.append(match.get('away_score', 0))

X = np.array(X)
y_home = np.array(y_home)
y_away = np.array(y_away)

print(f"✅ Feature matrix: ({X.shape[0]}, {X.shape[1]})")

# Train/test split
X_train, X_test, y_home_train, y_home_test, y_away_train, y_away_test = train_test_split(
    X, y_home, y_away, test_size=0.1, random_state=42
)

print(f"   Train: {X_train.shape[0]} wedstrijden")
print(f"   Test:  {X_test.shape[0]} wedstrijden")

# Normalize
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train 4 models (SAME AS HYPER!)
print("\n📊 Training BALANCED BEAST models...")

# 1. RandomForest (500 trees, depth 35 - HYPER config!)
print("   🏆 Training RandomForest (HYPER config: 500 trees, depth 35)...")
rf_home = RandomForestRegressor(n_estimators=500, max_depth=35, random_state=42, n_jobs=-1)
rf_away = RandomForestRegressor(n_estimators=500, max_depth=35, random_state=43, n_jobs=-1)
rf_home.fit(X_train, y_home_train)
rf_away.fit(X_train, y_away_train)
rf_home_pred = rf_home.predict(X_test)
rf_away_pred = rf_away.predict(X_test)
print(f"      ✅ MAE: {mean_absolute_error(y_home_test, rf_home_pred):.3f} home / {mean_absolute_error(y_away_test, rf_away_pred):.3f} away")

# 2. GradientBoosting
print("   🎯 Training GradientBoosting...")
gb_home = GradientBoostingRegressor(n_estimators=500, max_depth=35, learning_rate=0.01, random_state=42)
gb_away = GradientBoostingRegressor(n_estimators=500, max_depth=35, learning_rate=0.01, random_state=43)
gb_home.fit(X_train, y_home_train)
gb_away.fit(X_train, y_away_train)
gb_home_pred = gb_home.predict(X_test)
gb_away_pred = gb_away.predict(X_test)
print(f"      ✅ MAE: {mean_absolute_error(y_home_test, gb_home_pred):.3f} home / {mean_absolute_error(y_away_test, gb_away_pred):.3f} away")

# 3. ExtraTrees
print("   🔧 Training ExtraTrees...")
et_home = ExtraTreesRegressor(n_estimators=500, max_depth=35, random_state=42, n_jobs=-1)
et_away = ExtraTreesRegressor(n_estimators=500, max_depth=35, random_state=43, n_jobs=-1)
et_home.fit(X_train, y_home_train)
et_away.fit(X_train, y_away_train)
et_home_pred = et_home.predict(X_test)
et_away_pred = et_away.predict(X_test)
print(f"      ✅ MAE: {mean_absolute_error(y_home_test, et_home_pred):.3f} home / {mean_absolute_error(y_away_test, et_away_pred):.3f} away")

# 4. Ridge
print("   🔧 Training Ridge...")
ridge_home = Ridge(alpha=1.0)
ridge_away = Ridge(alpha=1.0)
ridge_home.fit(X_train, y_home_train)
ridge_away.fit(X_train, y_away_train)
ridge_home_pred = ridge_home.predict(X_test)
ridge_away_pred = ridge_away.predict(X_test)
print(f"      ✅ MAE: {mean_absolute_error(y_home_test, ridge_home_pred):.3f} home / {mean_absolute_error(y_away_test, ridge_away_pred):.3f} away")

# Ensemble prediction (SAME WEIGHTS AS HYPER!)
print("\n📊 Evaluatie...")
pred_home = (rf_home_pred * 0.35 + gb_home_pred * 0.30 + et_home_pred * 0.25 + ridge_home_pred * 0.10)
pred_away = (rf_away_pred * 0.35 + gb_away_pred * 0.30 + et_away_pred * 0.25 + ridge_away_pred * 0.10)

# Round predictions
pred_home = np.round(np.clip(pred_home, 0, 10)).astype(int)
pred_away = np.round(np.clip(pred_away, 0, 10)).astype(int)

# Calculate metrics
exact_correct = 0
goal_diff_correct = 0
result_correct = 0

for i in range(len(y_home_test)):
    # Exact score
    if pred_home[i] == y_home_test[i] and pred_away[i] == y_away_test[i]:
        exact_correct += 1
    
    # Goal difference
    pred_diff = pred_home[i] - pred_away[i]
    actual_diff = y_home_test[i] - y_away_test[i]
    if pred_diff == actual_diff:
        goal_diff_correct += 1
    
    # Result (W/D/L)
    pred_result = 1 if pred_home[i] > pred_away[i] else (0 if pred_home[i] == pred_away[i] else -1)
    actual_result = 1 if y_home_test[i] > y_away_test[i] else (0 if y_home_test[i] == y_away_test[i] else -1)
    if pred_result == actual_result:
        result_correct += 1

exact_pct = (exact_correct / len(y_home_test)) * 100
goal_diff_pct = (goal_diff_correct / len(y_home_test)) * 100
result_pct = (result_correct / len(y_home_test)) * 100

print("\n⚖️ BALANCED BEAST RESULTATEN:")
print(f"   ✅ Exact score: {exact_pct:.2f}%")
print(f"   ✅ Goal difference: {goal_diff_pct:.2f}%")
print(f"   ✅ Result (W/D/L): {result_pct:.2f}%")
print(f"   ✅ MAE: {mean_absolute_error(y_home_test, pred_home):.3f} home / {mean_absolute_error(y_away_test, pred_away):.3f} away")
print(f"   ✅ Exact: {exact_correct}/{len(y_home_test)}")

# Save model
model_data = {
    'rf_home': rf_home,
    'rf_away': rf_away,
    'gb_home': gb_home,
    'gb_away': gb_away,
    'et_home': et_home,
    'et_away': et_away,
    'ridge_home': ridge_home,
    'ridge_away': ridge_away,
    'scaler': scaler,
    'team_stats': team_stats,
    'exact_accuracy': exact_pct,
    'result_accuracy': result_pct,
    'trained_at': datetime.now().isoformat(),
    'num_matches': len(matches),
    'num_features': X.shape[1],
    'leagues': ['Premier League', 'Eredivisie'],
    'league_distribution': {
        'Premier League': pl_count,
        'Eredivisie': eredivisie_count
    }
}

model_path = 'data/de_meester_BALANCED.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(model_data, f)

file_size = os.path.getsize(model_path) / (1024 * 1024)
print(f"\n✅ Model opgeslagen: {model_path}")
print(f"   📊 File size: {file_size:.2f} MB")

print("\n" + "="*80)
print("⚖️ BALANCED BEAST KLAAR! 🏆🏆")
print(f"   📊 {len(matches)} matches ({pl_count} PL + {eredivisie_count} Eredivisie)")
print(f"   🎯 {exact_pct:.2f}% exact | {result_pct:.2f}% result")
print(f"   ⚖️ Perfect balance tussen defensive (PL) & offensive (Eredivisie)!")
print("="*80)

# Show sample predictions
print("\n🔥 TOP 10 voorspellingen:")
for i in range(min(10, len(y_home_test))):
    actual = f"{y_home_test[i]}-{y_away_test[i]}"
    predicted = f"{pred_home[i]}-{pred_away[i]}"
    check = "✅" if pred_home[i] == y_home_test[i] and pred_away[i] == y_away_test[i] else "❌"
    print(f"   {predicted} vs {actual} {check}")
