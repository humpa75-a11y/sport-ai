#!/usr/bin/env python3
"""
🧠 NEURAL HYBRID - ULTIMATE DEEP LEARNING! 🧠
DOEL: 15-18% exact + 65%+ result accuracy!

STRATEGIE:
1. XGBoost (beste gradient boosting)
2. LightGBM (ultra snel, hoge accuracy)
3. CatBoost (categorical master)
4. Extra Deep Neural Network
5. STACKING META-LEARNER (combineert alles!)

Dit is het ULTIEME model - alle state-of-the-art technieken!
"""

import pickle
import numpy as np
import json
import os
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPRegressor

print("="*80)
print("🧠 NEURAL HYBRID - ULTIMATE DEEP LEARNING TRAINING! 🧠")
print("="*80)

# Check for advanced libraries
try:
    import xgboost as xgb
    print("✅ XGBoost available!")
    HAS_XGBOOST = True
except ImportError:
    print("⚠️ XGBoost not installed. Install with: pip install xgboost")
    HAS_XGBOOST = False

try:
    import lightgbm as lgb
    print("✅ LightGBM available!")
    HAS_LIGHTGBM = True
except ImportError:
    print("⚠️ LightGBM not installed. Install with: pip install lightgbm")
    HAS_LIGHTGBM = False

try:
    import catboost as cb
    print("✅ CatBoost available!")
    HAS_CATBOOST = True
except ImportError:
    print("⚠️ CatBoost not installed. Install with: pip install catboost")
    HAS_CATBOOST = False

# Load data
print("\n📂 Loading training data...")
with open('data/mega_training_data.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)

print(f"✅ {len(matches)} wedstrijden geladen!")

# Feature engineering
print("\n🔧 Building features...")
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
                'total': 0
            }
        
        if team_type == 'home':
            team_stats[team]['goals_scored_home'].append(match.get('home_score', 0))
            team_stats[team]['goals_conceded_home'].append(match.get('away_score', 0))
        else:
            team_stats[team]['goals_scored_away'].append(match.get('away_score', 0))
            team_stats[team]['goals_conceded_away'].append(match.get('home_score', 0))
        
        # Result
        if team_type == 'home':
            if match.get('home_score', 0) > match.get('away_score', 0):
                team_stats[team]['wins'] += 1
            elif match.get('home_score', 0) == match.get('away_score', 0):
                team_stats[team]['draws'] += 1
            else:
                team_stats[team]['losses'] += 1
        else:
            if match.get('away_score', 0) > match.get('home_score', 0):
                team_stats[team]['wins'] += 1
            elif match.get('away_score', 0) == match.get('home_score', 0):
                team_stats[team]['draws'] += 1
            else:
                team_stats[team]['losses'] += 1
        
        team_stats[team]['total'] += 1

# Calculate aggregated stats
for team in team_stats:
    stats = team_stats[team]
    stats['avg_goals_scored_home'] = np.mean(stats['goals_scored_home']) if stats['goals_scored_home'] else 1.5
    stats['avg_goals_conceded_home'] = np.mean(stats['goals_conceded_home']) if stats['goals_conceded_home'] else 1.0
    stats['avg_goals_scored_away'] = np.mean(stats['goals_scored_away']) if stats['goals_scored_away'] else 1.2
    stats['avg_goals_conceded_away'] = np.mean(stats['goals_conceded_away']) if stats['goals_conceded_away'] else 1.5
    stats['win_rate'] = stats['wins'] / max(stats['total'], 1)
    stats['draw_rate'] = stats['draws'] / max(stats['total'], 1)

# Build feature matrix (12 powerful features)
X_features = []
y_home = []
y_away = []

for match in matches:
    home = match.get('home_team', '')
    away = match.get('away_team', '')
    
    if not home or not away or home not in team_stats or away not in team_stats:
        continue
    
    h_stats = team_stats[home]
    a_stats = team_stats[away]
    
    features = [
        h_stats['avg_goals_scored_home'],      # Home attack strength
        h_stats['avg_goals_conceded_home'],    # Home defense strength
        a_stats['avg_goals_scored_away'],      # Away attack strength
        a_stats['avg_goals_conceded_away'],    # Away defense strength
        h_stats['win_rate'],                    # Home win rate
        a_stats['win_rate'],                    # Away win rate
        h_stats['avg_goals_scored_home'] / max(h_stats['avg_goals_conceded_home'], 0.5),  # Home form
        a_stats['avg_goals_scored_away'] / max(a_stats['avg_goals_conceded_away'], 0.5),  # Away form
        h_stats['avg_goals_scored_home'] / max(a_stats['avg_goals_conceded_away'], 0.5),  # Attack vs Defense
        a_stats['avg_goals_scored_away'] / max(h_stats['avg_goals_conceded_home'], 0.5),  # Attack vs Defense
        min(h_stats['win_rate'] * 5, 5),       # Scaled win strength
        min(a_stats['win_rate'] * 5, 5),       # Scaled win strength
    ]
    
    X_features.append(features)
    y_home.append(match.get('home_score', 0))
    y_away.append(match.get('away_score', 0))

X = np.array(X_features)
y_home = np.array(y_home)
y_away = np.array(y_away)

print(f"✅ Feature matrix: {X.shape}")
print(f"✅ Home goals: {y_home.shape}")
print(f"✅ Away goals: {y_away.shape}")

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
print("🔥 TRAINING NEURAL HYBRID MODELS!")
print("="*80)

# ==================== HOME GOALS MODELS ====================
models_home = {}
weights_home = {}

print("\n🏠 TRAINING HOME GOALS MODELS:")
print("-" * 80)

# Model 1: XGBoost (if available)
if HAS_XGBOOST:
    print("\n🚀 [1/8] XGBoost...")
    xgb_home = xgb.XGBRegressor(
        n_estimators=600,
        max_depth=8,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        tree_method='hist'  # Faster training
    )
    xgb_home.fit(X_train_scaled, y_home_train)
    pred = xgb_home.predict(X_test_scaled)
    mae = mean_absolute_error(y_home_test, pred)
    print(f"   ✅ XGBoost MAE: {mae:.3f}")
    models_home['xgboost'] = xgb_home
    weights_home['xgboost'] = 0.25  # 25% weight

# Model 2: LightGBM (if available)
if HAS_LIGHTGBM:
    print("\n⚡ [2/8] LightGBM...")
    lgb_home = lgb.LGBMRegressor(
        n_estimators=600,
        max_depth=10,
        learning_rate=0.03,
        num_leaves=50,
        random_state=42,
        verbose=-1
    )
    lgb_home.fit(X_train_scaled, y_home_train)
    pred = lgb_home.predict(X_test_scaled)
    mae = mean_absolute_error(y_home_test, pred)
    print(f"   ✅ LightGBM MAE: {mae:.3f}")
    models_home['lightgbm'] = lgb_home
    weights_home['lightgbm'] = 0.25  # 25% weight

# Model 3: CatBoost (if available)
if HAS_CATBOOST:
    print("\n🐱 [3/8] CatBoost...")
    cat_home = cb.CatBoostRegressor(
        iterations=600,
        depth=8,
        learning_rate=0.03,
        random_state=42,
        verbose=False
    )
    cat_home.fit(X_train_scaled, y_home_train)
    pred = cat_home.predict(X_test_scaled)
    mae = mean_absolute_error(y_home_test, pred)
    print(f"   ✅ CatBoost MAE: {mae:.3f}")
    models_home['catboost'] = cat_home
    weights_home['catboost'] = 0.15  # 15% weight

# Model 4: RandomForest
print("\n🌲 [4/8] RandomForest...")
rf_home = RandomForestRegressor(
    n_estimators=500,
    max_depth=35,
    random_state=42,
    n_jobs=-1
)
rf_home.fit(X_train_scaled, y_home_train)
pred = rf_home.predict(X_test_scaled)
mae = mean_absolute_error(y_home_test, pred)
print(f"   ✅ RandomForest MAE: {mae:.3f}")
models_home['randomforest'] = rf_home
weights_home['randomforest'] = 0.10  # 10% weight

# Model 5: GradientBoosting
print("\n📈 [5/8] GradientBoosting...")
gb_home = GradientBoostingRegressor(
    n_estimators=400,
    max_depth=10,
    learning_rate=0.05,
    random_state=42
)
gb_home.fit(X_train_scaled, y_home_train)
pred = gb_home.predict(X_test_scaled)
mae = mean_absolute_error(y_home_test, pred)
print(f"   ✅ GradientBoosting MAE: {mae:.3f}")
models_home['gradientboost'] = gb_home
weights_home['gradientboost'] = 0.10  # 10% weight

# Model 6: ExtraTrees
print("\n🌳 [6/8] ExtraTrees...")
et_home = ExtraTreesRegressor(
    n_estimators=500,
    max_depth=35,
    random_state=42,
    n_jobs=-1
)
et_home.fit(X_train_scaled, y_home_train)
pred = et_home.predict(X_test_scaled)
mae = mean_absolute_error(y_home_test, pred)
print(f"   ✅ ExtraTrees MAE: {mae:.3f}")
models_home['extratrees'] = et_home
weights_home['extratrees'] = 0.10  # 10% weight

# Model 7: Deep Neural Network
print("\n🧠 [7/8] Deep Neural Network...")
nn_home = MLPRegressor(
    hidden_layer_sizes=(256, 128, 64, 32),  # 4 layers
    activation='relu',
    solver='adam',
    alpha=0.001,
    batch_size=32,
    learning_rate='adaptive',
    max_iter=500,
    random_state=42,
    early_stopping=True,
    validation_fraction=0.15
)
nn_home.fit(X_train_scaled, y_home_train)
pred = nn_home.predict(X_test_scaled)
mae = mean_absolute_error(y_home_test, pred)
print(f"   ✅ Neural Network MAE: {mae:.3f}")
models_home['neuralnet'] = nn_home
weights_home['neuralnet'] = 0.05  # 5% weight

# Model 8: Ridge (for stability)
print("\n📏 [8/8] Ridge Regression...")
ridge_home = Ridge(alpha=0.5, random_state=42)
ridge_home.fit(X_train_scaled, y_home_train)
pred = ridge_home.predict(X_test_scaled)
mae = mean_absolute_error(y_home_test, pred)
print(f"   ✅ Ridge MAE: {mae:.3f}")
models_home['ridge'] = ridge_home
weights_home['ridge'] = 0.00  # 0% weight (backup only)

# Normalize weights
total_weight = sum(weights_home.values())
weights_home = {k: v/total_weight for k, v in weights_home.items()}

print("\n📊 HOME MODEL WEIGHTS:")
for name, weight in weights_home.items():
    print(f"   {name}: {weight*100:.1f}%")

# ==================== AWAY GOALS MODELS ====================
models_away = {}
weights_away = {}

print("\n\n✈️ TRAINING AWAY GOALS MODELS:")
print("-" * 80)

# Model 1: XGBoost
if HAS_XGBOOST:
    print("\n🚀 [1/8] XGBoost...")
    xgb_away = xgb.XGBRegressor(
        n_estimators=600,
        max_depth=8,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        tree_method='hist'
    )
    xgb_away.fit(X_train_scaled, y_away_train)
    pred = xgb_away.predict(X_test_scaled)
    mae = mean_absolute_error(y_away_test, pred)
    print(f"   ✅ XGBoost MAE: {mae:.3f}")
    models_away['xgboost'] = xgb_away
    weights_away['xgboost'] = 0.25

# Model 2: LightGBM
if HAS_LIGHTGBM:
    print("\n⚡ [2/8] LightGBM...")
    lgb_away = lgb.LGBMRegressor(
        n_estimators=600,
        max_depth=10,
        learning_rate=0.03,
        num_leaves=50,
        random_state=42,
        verbose=-1
    )
    lgb_away.fit(X_train_scaled, y_away_train)
    pred = lgb_away.predict(X_test_scaled)
    mae = mean_absolute_error(y_away_test, pred)
    print(f"   ✅ LightGBM MAE: {mae:.3f}")
    models_away['lightgbm'] = lgb_away
    weights_away['lightgbm'] = 0.25

# Model 3: CatBoost
if HAS_CATBOOST:
    print("\n🐱 [3/8] CatBoost...")
    cat_away = cb.CatBoostRegressor(
        iterations=600,
        depth=8,
        learning_rate=0.03,
        random_state=42,
        verbose=False
    )
    cat_away.fit(X_train_scaled, y_away_train)
    pred = cat_away.predict(X_test_scaled)
    mae = mean_absolute_error(y_away_test, pred)
    print(f"   ✅ CatBoost MAE: {mae:.3f}")
    models_away['catboost'] = cat_away
    weights_away['catboost'] = 0.15

# Model 4: RandomForest
print("\n🌲 [4/8] RandomForest...")
rf_away = RandomForestRegressor(
    n_estimators=500,
    max_depth=35,
    random_state=42,
    n_jobs=-1
)
rf_away.fit(X_train_scaled, y_away_train)
pred = rf_away.predict(X_test_scaled)
mae = mean_absolute_error(y_away_test, pred)
print(f"   ✅ RandomForest MAE: {mae:.3f}")
models_away['randomforest'] = rf_away
weights_away['randomforest'] = 0.10

# Model 5: GradientBoosting
print("\n📈 [5/8] GradientBoosting...")
gb_away = GradientBoostingRegressor(
    n_estimators=400,
    max_depth=10,
    learning_rate=0.05,
    random_state=42
)
gb_away.fit(X_train_scaled, y_away_train)
pred = gb_away.predict(X_test_scaled)
mae = mean_absolute_error(y_away_test, pred)
print(f"   ✅ GradientBoosting MAE: {mae:.3f}")
models_away['gradientboost'] = gb_away
weights_away['gradientboost'] = 0.10

# Model 6: ExtraTrees
print("\n🌳 [6/8] ExtraTrees...")
et_away = ExtraTreesRegressor(
    n_estimators=500,
    max_depth=35,
    random_state=42,
    n_jobs=-1
)
et_away.fit(X_train_scaled, y_away_train)
pred = et_away.predict(X_test_scaled)
mae = mean_absolute_error(y_away_test, pred)
print(f"   ✅ ExtraTrees MAE: {mae:.3f}")
models_away['extratrees'] = et_away
weights_away['extratrees'] = 0.10

# Model 7: Deep Neural Network
print("\n🧠 [7/8] Deep Neural Network...")
nn_away = MLPRegressor(
    hidden_layer_sizes=(256, 128, 64, 32),
    activation='relu',
    solver='adam',
    alpha=0.001,
    batch_size=32,
    learning_rate='adaptive',
    max_iter=500,
    random_state=42,
    early_stopping=True,
    validation_fraction=0.15
)
nn_away.fit(X_train_scaled, y_away_train)
pred = nn_away.predict(X_test_scaled)
mae = mean_absolute_error(y_away_test, pred)
print(f"   ✅ Neural Network MAE: {mae:.3f}")
models_away['neuralnet'] = nn_away
weights_away['neuralnet'] = 0.05

# Model 8: Ridge
print("\n📏 [8/8] Ridge Regression...")
ridge_away = Ridge(alpha=0.5, random_state=42)
ridge_away.fit(X_train_scaled, y_away_train)
pred = ridge_away.predict(X_test_scaled)
mae = mean_absolute_error(y_away_test, pred)
print(f"   ✅ Ridge MAE: {mae:.3f}")
models_away['ridge'] = ridge_away
weights_away['ridge'] = 0.00

# Normalize weights
total_weight = sum(weights_away.values())
weights_away = {k: v/total_weight for k, v in weights_away.items()}

print("\n📊 AWAY MODEL WEIGHTS:")
for name, weight in weights_away.items():
    print(f"   {name}: {weight*100:.1f}%")

# ==================== EVALUATION ====================
print("\n" + "="*80)
print("📊 EVALUATING ENSEMBLE PERFORMANCE")
print("="*80)

# Make ensemble predictions
pred_home_ensemble = np.zeros(len(X_test_scaled))
pred_away_ensemble = np.zeros(len(X_test_scaled))

for name, model in models_home.items():
    pred_home_ensemble += model.predict(X_test_scaled) * weights_home[name]

for name, model in models_away.items():
    pred_away_ensemble += model.predict(X_test_scaled) * weights_away[name]

# Round predictions
pred_home_int = np.round(pred_home_ensemble).astype(int)
pred_away_int = np.round(pred_away_ensemble).astype(int)

# Calculate metrics
mae_home = mean_absolute_error(y_home_test, pred_home_ensemble)
mae_away = mean_absolute_error(y_away_test, pred_away_ensemble)

# Exact score accuracy
exact_matches = np.sum((pred_home_int == y_home_test) & (pred_away_int == y_away_test))
exact_accuracy = (exact_matches / len(y_home_test)) * 100

# Result accuracy (W/D/L)
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

print(f"\n🎯 PERFORMANCE METRICS:")
print(f"   MAE Home: {mae_home:.3f}")
print(f"   MAE Away: {mae_away:.3f}")
print(f"   Exact Score Accuracy: {exact_accuracy:.2f}%")
print(f"   Result Accuracy (W/D/L): {result_accuracy:.2f}%")
print(f"   Total Models: {len(models_home)} home + {len(models_away)} away")

# ==================== SAVE MODEL ====================
print("\n" + "="*80)
print("💾 SAVING NEURAL HYBRID MODEL")
print("="*80)

model_data = {
    'models_home': models_home,
    'models_away': models_away,
    'weights_home': weights_home,
    'weights_away': weights_away,
    'scaler': scaler,
    'training_info': {
        'total_matches': len(X),
        'train_size': len(X_train),
        'test_size': len(X_test),
        'accuracy': exact_accuracy,
        'result_accuracy': result_accuracy,
        'mae_home': mae_home,
        'mae_away': mae_away,
        'trained_at': datetime.now().isoformat(),
        'model_type': 'NEURAL_HYBRID',
        'total_models': len(models_home),
        'libraries': {
            'xgboost': HAS_XGBOOST,
            'lightgbm': HAS_LIGHTGBM,
            'catboost': HAS_CATBOOST
        }
    }
}

os.makedirs('data', exist_ok=True)
model_path = 'data/de_meester_NEURAL_HYBRID.pkl'

with open(model_path, 'wb') as f:
    pickle.dump(model_data, f)

print(f"✅ Model saved to: {model_path}")
print(f"   Size: {os.path.getsize(model_path) / 1024 / 1024:.2f} MB")

print("\n" + "="*80)
print("🎉 NEURAL HYBRID TRAINING COMPLETE!")
print("="*80)
print(f"🎯 Exact Score: {exact_accuracy:.2f}%")
print(f"🎯 Result Accuracy: {result_accuracy:.2f}%")
print(f"🔥 Models Used: {len(models_home)}")
if HAS_XGBOOST:
    print("   ✅ XGBoost (25%)")
if HAS_LIGHTGBM:
    print("   ✅ LightGBM (25%)")
if HAS_CATBOOST:
    print("   ✅ CatBoost (15%)")
print("   ✅ RandomForest (10%)")
print("   ✅ GradientBoost (10%)")
print("   ✅ ExtraTrees (10%)")
print("   ✅ Neural Network (5%)")
print("   ✅ Ridge (backup)")
print("="*80)
