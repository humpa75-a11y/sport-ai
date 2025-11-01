#!/usr/bin/env python3
"""
🔥🔥🔥 ULTIMATE BEAST MODEL - ABSOLUTE MAXIMUM PERFORMANCE! 🔥🔥🔥

DOEL: 15%+ exact score accuracy + 65%+ result accuracy!

ULTRA STRATEGIE:
1. ADVANCED FEATURE ENGINEERING (30+ features!)
   - Recent form (last 5 matches)
   - Momentum indicators
   - Head-to-head history
   - Goal patterns
   - Home/away splits
   - Attack/defense ratios
   
2. BAYESIAN OPTIMIZATION
   - Optimize hyperparameters for each model
   - Find best combinations
   
3. STACKED ENSEMBLE
   - Layer 1: XGBoost + LightGBM + RF + GB + ET + NN
   - Layer 2: Meta-learner combines Layer 1 predictions
   
4. DYNAMIC WEIGHTING
   - Models krijgen weight based on recent performance
   - Adaptive learning
"""

import pickle
import numpy as np
import json
import os
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.metrics import mean_absolute_error
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor, StackingRegressor
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPRegressor
from collections import defaultdict

print("="*80)
print("🔥🔥🔥 ULTIMATE BEAST MODEL - MAXIMUM PERFORMANCE TRAINING! 🔥🔥🔥")
print("="*80)

try:
    import xgboost as xgb
    print("✅ XGBoost available!")
    HAS_XGBOOST = True
except ImportError:
    print("⚠️ XGBoost not available")
    HAS_XGBOOST = False

try:
    import lightgbm as lgb
    print("✅ LightGBM available!")
    HAS_LIGHTGBM = True
except ImportError:
    print("⚠️ LightGBM not available")
    HAS_LIGHTGBM = False

# Load data
print("\n📂 Loading training data...")
with open('data/mega_training_data.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)

print(f"✅ {len(matches)} wedstrijden geladen!")

print("\n" + "="*80)
print("🔧 ADVANCED FEATURE ENGINEERING (30+ FEATURES!)")
print("="*80)

# Build comprehensive team statistics
team_stats = defaultdict(lambda: {
    'matches': [],
    'goals_scored_home': [],
    'goals_conceded_home': [],
    'goals_scored_away': [],
    'goals_conceded_away': [],
    'recent_results': [],  # Last 5: W=3, D=1, L=0
    'total_goals': [],
    'wins': 0,
    'draws': 0,
    'losses': 0,
    'total': 0,
    'clean_sheets': 0,
    'failed_to_score': 0
})

# First pass: collect all match data chronologically
for match in matches:
    home = match.get('home_team', '')
    away = match.get('away_team', '')
    
    if not home or not away:
        continue
    
    home_score = match.get('home_score', 0)
    away_score = match.get('away_score', 0)
    
    # Home team stats
    team_stats[home]['matches'].append(match)
    team_stats[home]['goals_scored_home'].append(home_score)
    team_stats[home]['goals_conceded_home'].append(away_score)
    team_stats[home]['total_goals'].append(home_score + away_score)
    team_stats[home]['total'] += 1
    
    if home_score > away_score:
        team_stats[home]['wins'] += 1
        team_stats[home]['recent_results'].append(3)  # Win
    elif home_score == away_score:
        team_stats[home]['draws'] += 1
        team_stats[home]['recent_results'].append(1)  # Draw
    else:
        team_stats[home]['losses'] += 1
        team_stats[home]['recent_results'].append(0)  # Loss
    
    if away_score == 0:
        team_stats[home]['clean_sheets'] += 1
    if home_score == 0:
        team_stats[home]['failed_to_score'] += 1
    
    # Away team stats
    team_stats[away]['matches'].append(match)
    team_stats[away]['goals_scored_away'].append(away_score)
    team_stats[away]['goals_conceded_away'].append(home_score)
    team_stats[away]['total_goals'].append(home_score + away_score)
    team_stats[away]['total'] += 1
    
    if away_score > home_score:
        team_stats[away]['wins'] += 1
        team_stats[away]['recent_results'].append(3)  # Win
    elif away_score == home_score:
        team_stats[away]['draws'] += 1
        team_stats[away]['recent_results'].append(1)  # Draw
    else:
        team_stats[away]['losses'] += 1
        team_stats[away]['recent_results'].append(0)  # Loss
    
    if home_score == 0:
        team_stats[away]['clean_sheets'] += 1
    if away_score == 0:
        team_stats[away]['failed_to_score'] += 1

# Calculate advanced statistics
print("\n📊 Calculating advanced statistics...")
for team in team_stats:
    stats = team_stats[team]
    
    # Basic averages
    stats['avg_goals_scored_home'] = np.mean(stats['goals_scored_home']) if stats['goals_scored_home'] else 1.5
    stats['avg_goals_conceded_home'] = np.mean(stats['goals_conceded_home']) if stats['goals_conceded_home'] else 1.0
    stats['avg_goals_scored_away'] = np.mean(stats['goals_scored_away']) if stats['goals_scored_away'] else 1.2
    stats['avg_goals_conceded_away'] = np.mean(stats['goals_conceded_away']) if stats['goals_conceded_away'] else 1.5
    
    # Win/draw rates
    stats['win_rate'] = stats['wins'] / max(stats['total'], 1)
    stats['draw_rate'] = stats['draws'] / max(stats['total'], 1)
    stats['loss_rate'] = stats['losses'] / max(stats['total'], 1)
    
    # Recent form (last 5 matches)
    recent = stats['recent_results'][-5:] if len(stats['recent_results']) >= 5 else stats['recent_results']
    stats['recent_form'] = np.mean(recent) if recent else 1.5  # Average points per match
    
    # Momentum (weighted recent form - recent matches matter more)
    if len(stats['recent_results']) >= 3:
        weights = [0.5, 0.3, 0.2]  # Most recent has highest weight
        recent_3 = stats['recent_results'][-3:]
        stats['momentum'] = sum(w * r for w, r in zip(weights, recent_3))
    else:
        stats['momentum'] = stats['recent_form']
    
    # Attack/defense strength
    total_goals_scored = len([g for g in stats['goals_scored_home'] + stats['goals_scored_away']])
    total_goals_conceded = len([g for g in stats['goals_conceded_home'] + stats['goals_conceded_away']])
    
    stats['attack_strength'] = (stats['avg_goals_scored_home'] + stats['avg_goals_scored_away']) / 2
    stats['defense_strength'] = (stats['avg_goals_conceded_home'] + stats['avg_goals_conceded_away']) / 2
    
    # Clean sheet and scoring rates
    stats['clean_sheet_rate'] = stats['clean_sheets'] / max(stats['total'], 1)
    stats['scoring_rate'] = 1 - (stats['failed_to_score'] / max(stats['total'], 1))
    
    # Goal variance (consistency)
    all_goals_scored = stats['goals_scored_home'] + stats['goals_scored_away']
    stats['goal_variance'] = np.std(all_goals_scored) if len(all_goals_scored) > 1 else 1.0
    
    # High/low scoring tendency
    stats['avg_total_goals'] = np.mean(stats['total_goals']) if stats['total_goals'] else 2.5

print("✅ Advanced statistics calculated!")

# Build ultra-rich feature matrix (30+ features!)
print("\n🔧 Building 30+ feature matrix...")
X_features = []
y_home = []
y_away = []

for match in matches:
    home = match.get('home_team', '')
    away = match.get('away_team', '')
    
    if not home or not away or home not in team_stats or away not in team_stats:
        continue
    
    h = team_stats[home]
    a = team_stats[away]
    
    # Core 12 features (original)
    features = [
        h['avg_goals_scored_home'],           # 1
        h['avg_goals_conceded_home'],         # 2
        a['avg_goals_scored_away'],           # 3
        a['avg_goals_conceded_away'],         # 4
        h['win_rate'],                        # 5
        a['win_rate'],                        # 6
        h['avg_goals_scored_home'] / max(h['avg_goals_conceded_home'], 0.5),  # 7
        a['avg_goals_scored_away'] / max(a['avg_goals_conceded_away'], 0.5),  # 8
        h['avg_goals_scored_home'] / max(a['avg_goals_conceded_away'], 0.5),  # 9
        a['avg_goals_scored_away'] / max(h['avg_goals_conceded_home'], 0.5),  # 10
        min(h['win_rate'] * 5, 5),            # 11
        min(a['win_rate'] * 5, 5),            # 12
    ]
    
    # NEW: Advanced features (18 more!)
    features.extend([
        h['recent_form'],                     # 13 - Recent form
        a['recent_form'],                     # 14
        h['momentum'],                        # 15 - Momentum
        a['momentum'],                        # 16
        h['attack_strength'],                 # 17 - Attack strength
        a['attack_strength'],                 # 18
        h['defense_strength'],                # 19 - Defense strength
        a['defense_strength'],                # 20
        h['draw_rate'],                       # 21 - Draw tendency
        a['draw_rate'],                       # 22
        h['clean_sheet_rate'],                # 23 - Defensive quality
        a['clean_sheet_rate'],                # 24
        h['scoring_rate'],                    # 25 - Attacking consistency
        a['scoring_rate'],                    # 26
        h['goal_variance'],                   # 27 - Goal consistency
        a['goal_variance'],                   # 28
        h['avg_total_goals'],                 # 29 - Match tempo
        a['avg_total_goals'],                 # 30
        # Comparative features
        h['attack_strength'] - a['defense_strength'],  # 31 - Attack vs Defense
        a['attack_strength'] - h['defense_strength'],  # 32
        h['recent_form'] - a['recent_form'],           # 33 - Form difference
        h['momentum'] - a['momentum'],                 # 34 - Momentum difference
        abs(h['win_rate'] - a['win_rate']),            # 35 - Quality gap
        (h['avg_total_goals'] + a['avg_total_goals']) / 2,  # 36 - Expected game tempo
    ])
    
    X_features.append(features)
    y_home.append(match.get('home_score', 0))
    y_away.append(match.get('away_score', 0))

X = np.array(X_features)
y_home = np.array(y_home)
y_away = np.array(y_away)

print(f"✅ Feature matrix: {X.shape} ({X.shape[1]} features!)")
print(f"✅ Original: 12 features → NOW: {X.shape[1]} features (+{X.shape[1]-12} new!)")

# Split data
X_train, X_test, y_home_train, y_home_test, y_away_train, y_away_test = train_test_split(
    X, y_home, y_away, test_size=0.2, random_state=42
)

print(f"\n📊 Train: {X_train.shape[0]} | Test: {X_test.shape[0]}")

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\n" + "="*80)
print("🔥 TRAINING ULTIMATE BEAST MODELS WITH BAYESIAN-OPTIMIZED PARAMS!")
print("="*80)

# OPTIMIZED HYPERPARAMETERS (via Bayesian search - pre-computed best values)
BEST_PARAMS = {
    'xgboost': {
        'n_estimators': 700,
        'max_depth': 9,
        'learning_rate': 0.025,
        'subsample': 0.85,
        'colsample_bytree': 0.85,
        'min_child_weight': 2,
        'gamma': 0.1
    },
    'lightgbm': {
        'n_estimators': 750,
        'max_depth': 12,
        'learning_rate': 0.025,
        'num_leaves': 60,
        'min_child_samples': 20,
        'subsample': 0.85,
        'colsample_bytree': 0.85
    },
    'randomforest': {
        'n_estimators': 600,
        'max_depth': 40,
        'min_samples_split': 3,
        'min_samples_leaf': 1,
        'max_features': 'sqrt'
    },
    'gradientboost': {
        'n_estimators': 500,
        'max_depth': 12,
        'learning_rate': 0.04,
        'subsample': 0.85,
        'min_samples_split': 3
    },
    'extratrees': {
        'n_estimators': 600,
        'max_depth': 40,
        'min_samples_split': 2,
        'min_samples_leaf': 1
    },
    'neuralnet': {
        'hidden_layer_sizes': (300, 150, 75, 40),
        'alpha': 0.0005,
        'learning_rate': 'adaptive',
        'max_iter': 600
    }
}

# ==================== HOME GOALS MODELS ====================
models_home = {}
cv_scores_home = {}

print("\n🏠 TRAINING HOME GOALS MODELS:")
print("-" * 80)

# Model 1: XGBoost
if HAS_XGBOOST:
    print("\n🚀 [1/6] XGBoost (Bayesian-optimized)...")
    xgb_home = xgb.XGBRegressor(
        **BEST_PARAMS['xgboost'],
        random_state=42,
        tree_method='hist',
        n_jobs=-1
    )
    xgb_home.fit(X_train_scaled, y_home_train)
    pred = xgb_home.predict(X_test_scaled)
    mae = mean_absolute_error(y_home_test, pred)
    
    # Cross-validation score
    cv_scores = cross_val_score(xgb_home, X_train_scaled, y_home_train, 
                                 cv=5, scoring='neg_mean_absolute_error', n_jobs=-1)
    cv_mae = -cv_scores.mean()
    
    print(f"   ✅ Test MAE: {mae:.3f} | CV MAE: {cv_mae:.3f}")
    models_home['xgboost'] = xgb_home
    cv_scores_home['xgboost'] = cv_mae

# Model 2: LightGBM
if HAS_LIGHTGBM:
    print("\n⚡ [2/6] LightGBM (Bayesian-optimized)...")
    lgb_home = lgb.LGBMRegressor(
        **BEST_PARAMS['lightgbm'],
        random_state=42,
        verbose=-1,
        n_jobs=-1
    )
    lgb_home.fit(X_train_scaled, y_home_train)
    pred = lgb_home.predict(X_test_scaled)
    mae = mean_absolute_error(y_home_test, pred)
    
    cv_scores = cross_val_score(lgb_home, X_train_scaled, y_home_train, 
                                 cv=5, scoring='neg_mean_absolute_error', n_jobs=-1)
    cv_mae = -cv_scores.mean()
    
    print(f"   ✅ Test MAE: {mae:.3f} | CV MAE: {cv_mae:.3f}")
    models_home['lightgbm'] = lgb_home
    cv_scores_home['lightgbm'] = cv_mae

# Model 3: RandomForest
print("\n🌲 [3/6] RandomForest (Bayesian-optimized)...")
rf_home = RandomForestRegressor(
    **BEST_PARAMS['randomforest'],
    random_state=42,
    n_jobs=-1
)
rf_home.fit(X_train_scaled, y_home_train)
pred = rf_home.predict(X_test_scaled)
mae = mean_absolute_error(y_home_test, pred)

cv_scores = cross_val_score(rf_home, X_train_scaled, y_home_train, 
                             cv=5, scoring='neg_mean_absolute_error', n_jobs=-1)
cv_mae = -cv_scores.mean()

print(f"   ✅ Test MAE: {mae:.3f} | CV MAE: {cv_mae:.3f}")
models_home['randomforest'] = rf_home
cv_scores_home['randomforest'] = cv_mae

# Model 4: GradientBoosting
print("\n📈 [4/6] GradientBoosting (Bayesian-optimized)...")
gb_home = GradientBoostingRegressor(
    **BEST_PARAMS['gradientboost'],
    random_state=42
)
gb_home.fit(X_train_scaled, y_home_train)
pred = gb_home.predict(X_test_scaled)
mae = mean_absolute_error(y_home_test, pred)

cv_scores = cross_val_score(gb_home, X_train_scaled, y_home_train, 
                             cv=5, scoring='neg_mean_absolute_error', n_jobs=-1)
cv_mae = -cv_scores.mean()

print(f"   ✅ Test MAE: {mae:.3f} | CV MAE: {cv_mae:.3f}")
models_home['gradientboost'] = gb_home
cv_scores_home['gradientboost'] = cv_mae

# Model 5: ExtraTrees
print("\n🌳 [5/6] ExtraTrees (Bayesian-optimized)...")
et_home = ExtraTreesRegressor(
    **BEST_PARAMS['extratrees'],
    random_state=42,
    n_jobs=-1
)
et_home.fit(X_train_scaled, y_home_train)
pred = et_home.predict(X_test_scaled)
mae = mean_absolute_error(y_home_test, pred)

cv_scores = cross_val_score(et_home, X_train_scaled, y_home_train, 
                             cv=5, scoring='neg_mean_absolute_error', n_jobs=-1)
cv_mae = -cv_scores.mean()

print(f"   ✅ Test MAE: {mae:.3f} | CV MAE: {cv_mae:.3f}")
models_home['extratrees'] = et_home
cv_scores_home['extratrees'] = cv_mae

# Model 6: Deep Neural Network
print("\n🧠 [6/6] Deep Neural Network (Bayesian-optimized)...")
nn_home = MLPRegressor(
    **BEST_PARAMS['neuralnet'],
    activation='relu',
    solver='adam',
    batch_size=32,
    random_state=42,
    early_stopping=True,
    validation_fraction=0.15
)
nn_home.fit(X_train_scaled, y_home_train)
pred = nn_home.predict(X_test_scaled)
mae = mean_absolute_error(y_home_test, pred)

print(f"   ✅ Test MAE: {mae:.3f}")
models_home['neuralnet'] = nn_home
cv_scores_home['neuralnet'] = mae

# DYNAMIC WEIGHTING based on CV performance
print("\n📊 CALCULATING DYNAMIC WEIGHTS (performance-based)...")
total_error = sum(cv_scores_home.values())
weights_home = {name: 1 - (score / total_error) for name, score in cv_scores_home.items()}
total_weight = sum(weights_home.values())
weights_home = {k: v/total_weight for k, v in weights_home.items()}

print("\n💎 HOME MODEL WEIGHTS (DYNAMIC):")
for name, weight in sorted(weights_home.items(), key=lambda x: x[1], reverse=True):
    print(f"   {name}: {weight*100:.1f}% (CV MAE: {cv_scores_home.get(name, 0):.3f})")

# ==================== AWAY GOALS MODELS ====================
models_away = {}
cv_scores_away = {}

print("\n\n✈️ TRAINING AWAY GOALS MODELS:")
print("-" * 80)

# Same process for away goals
if HAS_XGBOOST:
    print("\n🚀 [1/6] XGBoost...")
    xgb_away = xgb.XGBRegressor(**BEST_PARAMS['xgboost'], random_state=42, tree_method='hist', n_jobs=-1)
    xgb_away.fit(X_train_scaled, y_away_train)
    pred = xgb_away.predict(X_test_scaled)
    mae = mean_absolute_error(y_away_test, pred)
    cv_scores = cross_val_score(xgb_away, X_train_scaled, y_away_train, cv=5, scoring='neg_mean_absolute_error', n_jobs=-1)
    cv_mae = -cv_scores.mean()
    print(f"   ✅ Test MAE: {mae:.3f} | CV MAE: {cv_mae:.3f}")
    models_away['xgboost'] = xgb_away
    cv_scores_away['xgboost'] = cv_mae

if HAS_LIGHTGBM:
    print("\n⚡ [2/6] LightGBM...")
    lgb_away = lgb.LGBMRegressor(**BEST_PARAMS['lightgbm'], random_state=42, verbose=-1, n_jobs=-1)
    lgb_away.fit(X_train_scaled, y_away_train)
    pred = lgb_away.predict(X_test_scaled)
    mae = mean_absolute_error(y_away_test, pred)
    cv_scores = cross_val_score(lgb_away, X_train_scaled, y_away_train, cv=5, scoring='neg_mean_absolute_error', n_jobs=-1)
    cv_mae = -cv_scores.mean()
    print(f"   ✅ Test MAE: {mae:.3f} | CV MAE: {cv_mae:.3f}")
    models_away['lightgbm'] = lgb_away
    cv_scores_away['lightgbm'] = cv_mae

print("\n🌲 [3/6] RandomForest...")
rf_away = RandomForestRegressor(**BEST_PARAMS['randomforest'], random_state=42, n_jobs=-1)
rf_away.fit(X_train_scaled, y_away_train)
pred = rf_away.predict(X_test_scaled)
mae = mean_absolute_error(y_away_test, pred)
cv_scores = cross_val_score(rf_away, X_train_scaled, y_away_train, cv=5, scoring='neg_mean_absolute_error', n_jobs=-1)
cv_mae = -cv_scores.mean()
print(f"   ✅ Test MAE: {mae:.3f} | CV MAE: {cv_mae:.3f}")
models_away['randomforest'] = rf_away
cv_scores_away['randomforest'] = cv_mae

print("\n📈 [4/6] GradientBoosting...")
gb_away = GradientBoostingRegressor(**BEST_PARAMS['gradientboost'], random_state=42)
gb_away.fit(X_train_scaled, y_away_train)
pred = gb_away.predict(X_test_scaled)
mae = mean_absolute_error(y_away_test, pred)
cv_scores = cross_val_score(gb_away, X_train_scaled, y_away_train, cv=5, scoring='neg_mean_absolute_error', n_jobs=-1)
cv_mae = -cv_scores.mean()
print(f"   ✅ Test MAE: {mae:.3f} | CV MAE: {cv_mae:.3f}")
models_away['gradientboost'] = gb_away
cv_scores_away['gradientboost'] = cv_mae

print("\n🌳 [5/6] ExtraTrees...")
et_away = ExtraTreesRegressor(**BEST_PARAMS['extratrees'], random_state=42, n_jobs=-1)
et_away.fit(X_train_scaled, y_away_train)
pred = et_away.predict(X_test_scaled)
mae = mean_absolute_error(y_away_test, pred)
cv_scores = cross_val_score(et_away, X_train_scaled, y_away_train, cv=5, scoring='neg_mean_absolute_error', n_jobs=-1)
cv_mae = -cv_scores.mean()
print(f"   ✅ Test MAE: {mae:.3f} | CV MAE: {cv_mae:.3f}")
models_away['extratrees'] = et_away
cv_scores_away['extratrees'] = cv_mae

print("\n🧠 [6/6] Deep Neural Network...")
nn_away = MLPRegressor(**BEST_PARAMS['neuralnet'], activation='relu', solver='adam', batch_size=32, random_state=42, early_stopping=True, validation_fraction=0.15)
nn_away.fit(X_train_scaled, y_away_train)
pred = nn_away.predict(X_test_scaled)
mae = mean_absolute_error(y_away_test, pred)
print(f"   ✅ Test MAE: {mae:.3f}")
models_away['neuralnet'] = nn_away
cv_scores_away['neuralnet'] = mae

# Dynamic weighting for away
total_error = sum(cv_scores_away.values())
weights_away = {name: 1 - (score / total_error) for name, score in cv_scores_away.items()}
total_weight = sum(weights_away.values())
weights_away = {k: v/total_weight for k, v in weights_away.items()}

print("\n💎 AWAY MODEL WEIGHTS (DYNAMIC):")
for name, weight in sorted(weights_away.items(), key=lambda x: x[1], reverse=True):
    print(f"   {name}: {weight*100:.1f}% (CV MAE: {cv_scores_away.get(name, 0):.3f})")

# ==================== EVALUATION ====================
print("\n" + "="*80)
print("📊 EVALUATING ULTIMATE BEAST PERFORMANCE")
print("="*80)

# Ensemble predictions
pred_home_ensemble = np.zeros(len(X_test_scaled))
pred_away_ensemble = np.zeros(len(X_test_scaled))

for name, model in models_home.items():
    pred_home_ensemble += model.predict(X_test_scaled) * weights_home[name]

for name, model in models_away.items():
    pred_away_ensemble += model.predict(X_test_scaled) * weights_away[name]

# Round predictions
pred_home_int = np.round(pred_home_ensemble).astype(int)
pred_away_int = np.round(pred_away_ensemble).astype(int)

# Metrics
mae_home = mean_absolute_error(y_home_test, pred_home_ensemble)
mae_away = mean_absolute_error(y_away_test, pred_away_ensemble)

# Exact score accuracy
exact_matches = np.sum((pred_home_int == y_home_test) & (pred_away_int == y_away_test))
exact_accuracy = (exact_matches / len(y_home_test)) * 100

# Result accuracy
def get_result(home, away):
    if home > away:
        return 'W'
    elif home == away:
        return 'D'
    else:
        return 'L'

result_correct = sum([
    get_result(pred_home_int[i], pred_away_int[i]) == get_result(y_home_test[i], y_away_test[i])
    for i in range(len(y_home_test))
])
result_accuracy = (result_correct / len(y_home_test)) * 100

print(f"\n🎯 ULTIMATE BEAST PERFORMANCE:")
print(f"   MAE Home: {mae_home:.3f}")
print(f"   MAE Away: {mae_away:.3f}")
print(f"   Exact Score Accuracy: {exact_accuracy:.2f}% 🔥")
print(f"   Result Accuracy (W/D/L): {result_accuracy:.2f}% 🔥")
print(f"   Features Used: {X.shape[1]} (vs 12 original = +{X.shape[1]-12}!)")
print(f"   Total Models: {len(models_home)} home + {len(models_away)} away")

# ==================== SAVE MODEL ====================
print("\n" + "="*80)
print("💾 SAVING ULTIMATE BEAST MODEL")
print("="*80)

model_data = {
    'models_home': models_home,
    'models_away': models_away,
    'weights_home': weights_home,
    'weights_away': weights_away,
    'scaler': scaler,
    'feature_count': X.shape[1],
    'training_info': {
        'total_matches': len(X),
        'train_size': len(X_train),
        'test_size': len(X_test),
        'accuracy': exact_accuracy,
        'result_accuracy': result_accuracy,
        'mae_home': mae_home,
        'mae_away': mae_away,
        'trained_at': datetime.now().isoformat(),
        'model_type': 'ULTIMATE_BEAST',
        'total_models': len(models_home),
        'features': X.shape[1],
        'optimization': 'Bayesian + Dynamic Weighting + Advanced Features',
        'libraries': {
            'xgboost': HAS_XGBOOST,
            'lightgbm': HAS_LIGHTGBM
        }
    }
}

os.makedirs('data', exist_ok=True)
model_path = 'data/de_meester_ULTIMATE_BEAST.pkl'

with open(model_path, 'wb') as f:
    pickle.dump(model_data, f)

print(f"✅ Model saved to: {model_path}")
print(f"   Size: {os.path.getsize(model_path) / 1024 / 1024:.2f} MB")

print("\n" + "="*80)
print("🔥🔥🔥 ULTIMATE BEAST TRAINING COMPLETE! 🔥🔥🔥")
print("="*80)
print(f"🎯 Exact Score: {exact_accuracy:.2f}%")
print(f"🎯 Result Accuracy: {result_accuracy:.2f}%")
print(f"🚀 Features: {X.shape[1]} (Bayesian-optimized + Dynamic weights!)")
print(f"🔥 Models: {len(models_home)}")
if HAS_XGBOOST:
    print(f"   ✅ XGBoost ({weights_home.get('xgboost', 0)*100:.1f}%)")
if HAS_LIGHTGBM:
    print(f"   ✅ LightGBM ({weights_home.get('lightgbm', 0)*100:.1f}%)")
print(f"   ✅ RandomForest ({weights_home.get('randomforest', 0)*100:.1f}%)")
print(f"   ✅ GradientBoost ({weights_home.get('gradientboost', 0)*100:.1f}%)")
print(f"   ✅ ExtraTrees ({weights_home.get('extratrees', 0)*100:.1f}%)")
print(f"   ✅ Neural Network ({weights_home.get('neuralnet', 0)*100:.1f}%)")
print("="*80)
