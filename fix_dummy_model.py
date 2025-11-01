"""
Creëer een werkend dummy model met echte voorspellingsfunctionaliteit
"""
import pickle
import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor

print("🔧 Creëren van een werkend dummy model...")

# Maak dummy data voor training
X_dummy = np.random.rand(100, 50)  # 100 samples, 50 features
y_home = np.random.randint(0, 4, 100)  # Home goals 0-3
y_away = np.random.randint(0, 4, 100)  # Away goals 0-3

# Train simpele modellen
model_home = RandomForestRegressor(n_estimators=10, random_state=42)
model_away = RandomForestRegressor(n_estimators=10, random_state=42)

model_home.fit(X_dummy, y_home)
model_away.fit(X_dummy, y_away)

# Creëer model dictionary
model_data = {
    'home_model': model_home,
    'away_model': model_away,
    'feature_names': [f'feature_{i}' for i in range(50)],
    'version': '1.0_dummy',
    'trained': True
}

# Sla op
model_path = 'data/de_meester.pkl'
os.makedirs('data', exist_ok=True)

with open(model_path, 'wb') as f:
    pickle.dump(model_data, f)

print(f"✅ Werkend dummy model opgeslagen in {model_path}")
print("   - Home goals model: READY")
print("   - Away goals model: READY")
print("   - Features: 50")
print("\n🎉 Model is nu klaar voor voorspellingen!")
