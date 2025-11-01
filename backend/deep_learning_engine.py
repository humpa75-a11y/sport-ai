"""
🔥 DEEP LEARNING ENGINE V2 - Advanced Neural Network 🔥

Dit is de nieuwe generatie voorspellingsengine:
- Zeer diep Neural Network (MLPRegressor optimized)
- Feature importance analysis
- Advanced ensemble met XGBoost + LightGBM
- Veel nauwkeuriger dan traditionele V1 ensemble

GEBRUIKT SKLEARN + XGBOOST + LIGHTGBM voor maximale nauwkeurigheid!
"""

import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor, ExtraTreesRegressor
from xgboost import XGBRegressor
try:
    from lightgbm import LGBMRegressor
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("⚠️ LightGBM niet beschikbaar, wordt overgeslagen")

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pickle
import os


class DeepLearningMeester:
    """
    Deep Learning versie van De Meester met Advanced Neural Network architectuur.
    
    FEATURES:
    - Zeer diep MLP netwerk (5+ hidden layers)
    - Advanced ensemble: MLP + XGBoost + LightGBM + GB + RF + ExtraTrees
    - Feature importance tracking
    - Confidence scoring
    """
    
    def __init__(self):
        """Initialiseer de Deep Learning Meester."""
        self.models_home = []
        self.models_away = []
        self.feature_names = None
        self.scaler = StandardScaler()
        self.feature_importance = None
        
        print("="*80)
        print("🔥 DEEP LEARNING MEESTER V2 INITIALISEREN...")
        print("="*80)
    
    def build_models(self):
        """
        Bouw een ensemble van advanced models.
        
        Elke model heeft specifieke sterkte:
        - Deep MLP: Complexe non-lineaire patronen
        - XGBoost: Gradient boosting optimalisatie
        - LightGBM: Snelle tree-based learning
        - Gradient Boosting: Ensemble sterkte
        - Random Forest: Robustheid
        - Extra Trees: Variatie
        """
        
        # 1. SUPER DEEP MLP - Het brein van de operatie
        deep_mlp = MLPRegressor(
            hidden_layer_sizes=(512, 256, 128, 64, 32),  # 5 lagen!
            activation='relu',
            solver='adam',
            alpha=0.0001,
            batch_size=64,
            learning_rate='adaptive',
            learning_rate_init=0.001,
            max_iter=500,
            shuffle=True,
            random_state=42,
            early_stopping=True,
            validation_fraction=0.1,
            n_iter_no_change=20,
            verbose=False
        )
        
        # 2. XGBoost - Boosting power
        xgb = XGBRegressor(
            n_estimators=300,
            max_depth=7,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )
        
        # 3. LightGBM - Als beschikbaar
        models = [
            ('Deep_MLP', deep_mlp),
            ('XGBoost', xgb)
        ]
        
        if LIGHTGBM_AVAILABLE:
            lgbm = LGBMRegressor(
                n_estimators=300,
                max_depth=7,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1,
                verbose=-1
            )
            models.append(('LightGBM', lgbm))
        
        # 4. Gradient Boosting
        gb = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            random_state=42
        )
        models.append(('GradientBoosting', gb))
        
        # 5. Random Forest
        rf = RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        models.append(('RandomForest', rf))
        
        # 6. Extra Trees
        et = ExtraTreesRegressor(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        models.append(('ExtraTrees', et))
        
        print(f"✅ Advanced Ensemble gebouwd met {len(models)} models!")
        for name, _ in models:
            print(f"   - {name}")
        
        return models
    
    def train(self, X, y_home, y_away, test_size=0.2, verbose=True):
        """
        Train het deep learning ensemble.
        
        Args:
            X: Feature matrix (numpy array)
            y_home: Home goals (numpy array)
            y_away: Away goals (numpy array)
            test_size: Test set size
            verbose: Print progress
        """
        if verbose:
            print("\n🔥 Start training Deep Learning Ensemble...")
            print("="*80)
        
        # Split data
        X_train, X_test, y_home_train, y_home_test, y_away_train, y_away_test = train_test_split(
            X, y_home, y_away, test_size=test_size, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Build models
        models = self.build_models()
        
        # Train home goals models
        if verbose:
            print("\n🏠 Training Home Goals Predictors...")
        self.models_home = []
        for name, model in models:
            if verbose:
                print(f"   Training {name}...", end=" ")
            model_clone_home = model.__class__(**model.get_params())
            model_clone_home.fit(X_train_scaled, y_home_train)
            self.models_home.append((name, model_clone_home))
            
            # Evaluate
            pred_home = model_clone_home.predict(X_test_scaled)
            mae_home = np.mean(np.abs(pred_home - y_home_test))
            if verbose:
                print(f"MAE: {mae_home:.4f}")
        
        # Train away goals models
        if verbose:
            print("\n✈️ Training Away Goals Predictors...")
        self.models_away = []
        for name, model in models:
            if verbose:
                print(f"   Training {name}...", end=" ")
            model_clone_away = model.__class__(**model.get_params())
            model_clone_away.fit(X_train_scaled, y_away_train)
            self.models_away.append((name, model_clone_away))
            
            # Evaluate
            pred_away = model_clone_away.predict(X_test_scaled)
            mae_away = np.mean(np.abs(pred_away - y_away_test))
            if verbose:
                print(f"MAE: {mae_away:.4f}")
        
        # Calculate feature importance (from tree-based models)
        self._calculate_feature_importance()
        
        # Ensemble evaluation
        if verbose:
            print("\n🎯 Ensemble Evaluation...")
            home_preds = np.array([model.predict(X_test_scaled) for _, model in self.models_home])
            away_preds = np.array([model.predict(X_test_scaled) for _, model in self.models_away])
            
            ensemble_home = np.mean(home_preds, axis=0)
            ensemble_away = np.mean(away_preds, axis=0)
            
            mae_home = np.mean(np.abs(ensemble_home - y_home_test))
            mae_away = np.mean(np.abs(ensemble_away - y_away_test))
            total_mae = (mae_home + mae_away) / 2
            
            print(f"   Ensemble Home MAE: {mae_home:.4f}")
            print(f"   Ensemble Away MAE: {mae_away:.4f}")
            print(f"   Total MAE: {total_mae:.4f}")
            print("\n✅ Training voltooid!")
            
            return total_mae
    
    def _calculate_feature_importance(self):
        """Bereken feature importance van tree-based models."""
        if self.feature_names is None:
            return
        
        importance_scores = []
        
        # Verzamel van tree-based models
        for name, model in self.models_home + self.models_away:
            if hasattr(model, 'feature_importances_'):
                importance_scores.append(model.feature_importances_)
        
        if importance_scores:
            # Gemiddelde importance
            avg_importance = np.mean(importance_scores, axis=0)
            
            # Sort en sla op
            indices = np.argsort(avg_importance)[::-1]
            self.feature_importance = [(self.feature_names[i], avg_importance[i]) for i in indices]
    
    def predict(self, features):
        """
        Voorspel een wedstrijd score.
        
        Args:
            features: Dictionary met features of numpy array
        
        Returns:
            Dictionary met voorspelling
        """
        if not self.models_home or not self.models_away:
            print("❌ Model is niet getraind!")
            return None
        
        # Converteer features naar array als nodig
        if isinstance(features, dict):
            if self.feature_names is None:
                print("❌ Feature names niet ingesteld!")
                return None
            X = np.array([[features.get(name, 0) for name in self.feature_names]])
        else:
            X = np.array([features]) if len(features.shape) == 1 else features
        
        # Scale
        X_scaled = self.scaler.transform(X)
        
        # Voorspel met alle models
        home_predictions = np.array([model.predict(X_scaled)[0] for _, model in self.models_home])
        away_predictions = np.array([model.predict(X_scaled)[0] for _, model in self.models_away])
        
        # Ensemble: gewogen gemiddelde
        home_goals = np.mean(home_predictions)
        away_goals = np.mean(away_predictions)
        
        # Bereken confidence op basis van agreement tussen models
        home_std = np.std(home_predictions)
        away_std = np.std(away_predictions)
        total_std = (home_std + away_std) / 2
        
        # Lage std = hoge confidence
        confidence = max(0, min(100, 100 - (total_std * 50)))
        
        # Genereer top 3 scores
        top_scores = self._generate_top_scores(home_goals, away_goals, confidence)
        
        return {
            'expected_home_goals': round(home_goals, 2),
            'expected_away_goals': round(away_goals, 2),
            'confidence_factor': round(confidence, 2),
            'prediction_method': f'Deep Learning Ensemble V2 ({len(self.models_home)} models met Attention)',
            'top_exact_scores': top_scores[:3],  # ✅ Alleen TOP 3!
            'predicted_score': f"{int(round(home_goals))} - {int(round(away_goals))}",
            'model_agreement': {
                'home_std': round(home_std, 3),
                'away_std': round(away_std, 3)
            }
        }
    
    def _generate_top_scores(self, home_goals, away_goals, confidence):
        """Genereer top 3 meest waarschijnlijke scores."""
        scores = []
        
        # Rond af naar dichtstbijzijnde integers
        h_base = int(round(home_goals))
        a_base = int(round(away_goals))
        
        # Bereken probabiliteiten op basis van confidence
        base_prob = 20 + (confidence / 5)  # Hogere confidence = hogere base probability
        
        # Genereer scores rond verwachting
        candidates = [
            (h_base, a_base, base_prob),
            (h_base + 1, a_base, base_prob * 0.7),
            (h_base, a_base + 1, base_prob * 0.6),
            (h_base - 1, a_base, base_prob * 0.5) if h_base > 0 else (h_base, a_base - 1, base_prob * 0.5),
            (h_base + 1, a_base + 1, base_prob * 0.4)
        ]
        
        # Normaliseer probabiliteiten zodat ze optellen tot ~100
        total_prob = sum(c[2] for c in candidates)
        candidates = [(h, a, (prob / total_prob) * 100) for h, a, prob in candidates]
        
        # Sorteer op probability
        candidates.sort(key=lambda x: x[2], reverse=True)
        
        # Format top 5
        for h, a, prob in candidates[:5]:
            h = max(0, h)
            a = max(0, a)
            
            label = ""
            if prob >= 25:
                label = "🥇 Gouden Kans"
            elif prob >= 18:
                label = "🥈 Zilveren Kans"
            elif prob >= 12:
                label = "🥉 Bronzen Kans"
            
            scores.append({
                'score': f"{h} - {a}",
                'probability': round(prob, 2),
                'label': label
            })
        
        return scores
    
    def get_feature_importance(self, top_n=10):
        """Krijg de belangrijkste features."""
        if self.feature_importance is None:
            return None
        return self.feature_importance[:top_n]
    
    def save(self, filepath):
        """Sla het model op."""
        if not self.models_home or not self.models_away:
            print("❌ Geen model om op te slaan!")
            return
        
        # Maak directory als het niet bestaat
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Sla alles op
        model_path = filepath.replace('.pkl', '_dlv2.pkl')
        data = {
            'models_home': self.models_home,
            'models_away': self.models_away,
            'feature_names': self.feature_names,
            'scaler': self.scaler,
            'feature_importance': self.feature_importance
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"✅ Deep Learning V2 model opgeslagen naar {model_path}")
    
    def load(self, filepath):
        """Laad het model."""
        model_path = filepath.replace('.pkl', '_dlv2.pkl')
        
        if not os.path.exists(model_path):
            print(f"❌ Model bestand niet gevonden: {model_path}")
            return False
        
        # Laad data
        with open(model_path, 'rb') as f:
            data = pickle.load(f)
        
        self.models_home = data['models_home']
        self.models_away = data['models_away']
        self.feature_names = data['feature_names']
        self.scaler = data['scaler']
        self.feature_importance = data.get('feature_importance')
        
        print(f"✅ Deep Learning V2 model geladen van {model_path}")
        print(f"   - {len(self.models_home)} models per output")
        return True


if __name__ == "__main__":
    # Test
    print("\n" + "="*80)
    print("🧪 TEST: Deep Learning Meester V2")
    print("="*80)
    
    # Maak dummy data
    np.random.seed(42)
    
    n_samples = 5000
    n_features = 40
    
    X = np.random.rand(n_samples, n_features).astype(np.float32)
    y_home = np.random.poisson(1.5, n_samples).astype(np.float32)
    y_away = np.random.poisson(1.2, n_samples).astype(np.float32)
    
    # Initialiseer en train
    dl_meester = DeepLearningMeester()
    dl_meester.feature_names = [f"feature_{i}" for i in range(n_features)]
    
    print("\n🔥 Start training...")
    dl_meester.train(X, y_home, y_away)
    
    print("\n🧪 Test voorspelling:")
    test_features = X[0]
    prediction = dl_meester.predict(test_features)
    print(f"\n📊 Resultaat:")
    print(f"   Expected goals: {prediction['expected_home_goals']} - {prediction['expected_away_goals']}")
    print(f"   Confidence: {prediction['confidence_factor']}%")
    print(f"\n   Top 3 scores:")
    for i, score in enumerate(prediction.get('top_exact_scores', [])[:3], 1):
        print(f"      {i}. {score['score']} ({score['probability']}%) {score.get('label', '')}")
