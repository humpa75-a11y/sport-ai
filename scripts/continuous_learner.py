"""
🧠 CONTINUOUS LEARNING SYSTEM
=============================

Automatic learning cycle:
1. Hunt new data from web
2. Validate & clean data
3. Merge with existing training set
4. Retrain models automatically
5. Compare performance
6. Keep best model

BLIJF LEREN MEESTER! 🚀
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import glob
import pickle
from scripts.web_data_hunter import WebDataHunter
from scripts.train_score_predictor import AdvancedScorePredictor
import shutil

class ContinuousLearner:
    """Automatically learn from new web data"""
    
    def __init__(self):
        self.training_history = []
        self.best_model_accuracy = 0.0
        self.learning_log = []
        
    def hunt_new_data(self):
        """Step 1: Hunt fresh data from web"""
        print("\n" + "="*80)
        print("🦈 STEP 1: HUNTING NEW DATA")
        print("="*80)
        
        hunter = WebDataHunter()
        
        # Hunt from all sources
        hunter.scrape_flashscore_results('eredivisie')
        hunter.scrape_flashscore_results('premier-league')
        hunter.scrape_soccerway_results('eredivisie')
        hunter.scrape_soccerway_results('premier-league')
        hunter.scrape_card_statistics('eredivisie')
        hunter.scrape_card_statistics('premier-league')
        
        # Save
        summary = hunter.save_all_data()
        
        self.learning_log.append({
            'step': 'data_hunt',
            'timestamp': datetime.now().isoformat(),
            'matches_found': summary['matches'],
            'sources': summary['sources']
        })
        
        return hunter.collected_data
    
    def validate_and_clean(self, new_data):
        """Step 2: Validate and clean scraped data"""
        print("\n" + "="*80)
        print("🧹 STEP 2: VALIDATING & CLEANING DATA")
        print("="*80)
        
        if not new_data['matches']:
            print("[WARN] No matches found in new data!")
            return pd.DataFrame()
        
        df = pd.DataFrame(new_data['matches'])
        
        print(f"[DATA] Initial rows: {len(df)}")
        
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates(subset=['home_team', 'away_team', 'home_score', 'away_score'])
        print(f"[CLEAN] Removed {initial_count - len(df)} duplicates")
        
        # Validate scores (must be numeric and reasonable)
        df = df[df['home_score'].notna() & df['away_score'].notna()]
        df = df[df['home_score'] >= 0]
        df = df[df['away_score'] >= 0]
        df = df[df['home_score'] < 15]  # Unrealistic if > 15 goals
        df = df[df['away_score'] < 15]
        print(f"[CLEAN] Valid matches: {len(df)}")
        
        # Add missing columns with defaults
        if 'home_odds' not in df.columns:
            # Estimate odds based on score (simple heuristic)
            def estimate_odds(row):
                home_score = row['home_score']
                away_score = row['away_score']
                
                if home_score > away_score:
                    home_odds = 1.5 + (away_score * 0.3)
                    away_odds = 3.0 + (home_score * 0.5)
                elif away_score > home_score:
                    home_odds = 3.0 + (away_score * 0.5)
                    away_odds = 1.5 + (home_score * 0.3)
                else:
                    home_odds = 2.8
                    away_odds = 2.8
                
                draw_odds = 3.2
                
                return pd.Series({
                    'home_odds': round(home_odds, 2),
                    'away_odds': round(away_odds, 2),
                    'draw_odds': draw_odds
                })
            
            df[['home_odds', 'away_odds', 'draw_odds']] = df.apply(estimate_odds, axis=1)
            print(f"[GENERATE] Added estimated odds for {len(df)} matches")
        
        # Ensure date column
        if 'date' not in df.columns:
            df['date'] = datetime.now().strftime('%Y-%m-%d')
        
        print(f"[SUCCESS] Clean dataset: {len(df)} matches")
        
        self.learning_log.append({
            'step': 'validation',
            'timestamp': datetime.now().isoformat(),
            'valid_matches': len(df),
            'columns': list(df.columns)
        })
        
        return df
    
    def merge_with_existing(self, new_df):
        """Step 3: Merge with existing training data"""
        print("\n" + "="*80)
        print("🔄 STEP 3: MERGING WITH EXISTING DATA")
        print("="*80)
        
        # Find existing training data
        existing_files = glob.glob('data/training_dataset_*.csv')
        
        if existing_files:
            latest_file = max(existing_files, key=os.path.getctime)
            print(f"[LOAD] Existing data: {latest_file}")
            
            existing_df = pd.read_csv(latest_file)
            print(f"[LOAD] Existing rows: {len(existing_df)}")
            
            # Combine
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            
            # Remove duplicates again
            initial = len(combined_df)
            combined_df = combined_df.drop_duplicates(
                subset=['home_team', 'away_team', 'home_score', 'away_score'],
                keep='last'  # Keep newest
            )
            print(f"[MERGE] Removed {initial - len(combined_df)} duplicates")
            
        else:
            print("[INFO] No existing data found, using only new data")
            combined_df = new_df
        
        print(f"[SUCCESS] Combined dataset: {len(combined_df)} matches")
        
        # Save merged dataset
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        merged_file = f'data/training_dataset_{timestamp}.csv'
        combined_df.to_csv(merged_file, index=False)
        print(f"[SAVE] Merged data: {merged_file}")
        
        self.learning_log.append({
            'step': 'merge',
            'timestamp': datetime.now().isoformat(),
            'total_matches': len(combined_df),
            'new_matches': len(new_df),
            'file': merged_file
        })
        
        return combined_df, merged_file
    
    def retrain_model(self):
        """Step 4: Retrain model with new data"""
        print("\n" + "="*80)
        print("🧠 STEP 4: RETRAINING MODEL")
        print("="*80)
        
        predictor = AdvancedScorePredictor()
        
        # Load latest data
        df = predictor.load_training_data()
        
        if df is None or len(df) < 100:
            print("[ERROR] Not enough data to train (need at least 100 matches)")
            return None
        
        # Engineer features
        df, feature_cols = predictor.engineer_features(df)
        
        # Train models
        metrics = predictor.train_models(df, feature_cols)
        
        # Save new model
        predictor.save_model()
        
        self.learning_log.append({
            'step': 'training',
            'timestamp': datetime.now().isoformat(),
            'training_samples': len(df),
            'metrics': metrics
        })
        
        return metrics
    
    def compare_models(self, new_metrics):
        """Step 5: Compare new model with previous best"""
        print("\n" + "="*80)
        print("📊 STEP 5: MODEL COMPARISON")
        print("="*80)
        
        # Load previous best accuracy
        history_file = 'data/learning_history.json'
        
        if os.path.exists(history_file):
            import json
            with open(history_file, 'r') as f:
                history = json.load(f)
                self.best_model_accuracy = history.get('best_accuracy', 0.0)
        
        new_accuracy = new_metrics['combined_accuracy']
        
        print(f"[COMPARE] Previous best: {self.best_model_accuracy:.3f}")
        print(f"[COMPARE] New model:     {new_accuracy:.3f}")
        
        if new_accuracy > self.best_model_accuracy:
            improvement = new_accuracy - self.best_model_accuracy
            print(f"\n✅ IMPROVEMENT: +{improvement:.3f} ({improvement/self.best_model_accuracy*100:.1f}%)")
            print("[ACTION] Keeping new model as best!")
            
            self.best_model_accuracy = new_accuracy
            
            # Backup best model
            shutil.copy(
                'data/score_predictor.pkl',
                'data/score_predictor_BEST.pkl'
            )
            
            self.learning_log.append({
                'step': 'improvement',
                'timestamp': datetime.now().isoformat(),
                'new_best': new_accuracy,
                'improvement': improvement
            })
            
            return 'IMPROVED'
        
        else:
            decline = self.best_model_accuracy - new_accuracy
            print(f"\n⚠️  DECLINE: -{decline:.3f} ({decline/self.best_model_accuracy*100:.1f}%)")
            print("[ACTION] Restoring previous best model")
            
            # Restore best model
            if os.path.exists('data/score_predictor_BEST.pkl'):
                shutil.copy(
                    'data/score_predictor_BEST.pkl',
                    'data/score_predictor.pkl'
                )
                print("[RESTORE] Best model restored")
            
            self.learning_log.append({
                'step': 'no_improvement',
                'timestamp': datetime.now().isoformat(),
                'new_accuracy': new_accuracy,
                'kept_best': self.best_model_accuracy
            })
            
            return 'NO_IMPROVEMENT'
    
    def save_learning_history(self):
        """Save complete learning history"""
        history_file = 'data/learning_history.json'
        
        import json
        history = {
            'best_accuracy': self.best_model_accuracy,
            'total_learning_cycles': len([l for l in self.learning_log if l['step'] == 'training']),
            'last_update': datetime.now().isoformat(),
            'log': self.learning_log
        }
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        print(f"\n[SAVE] Learning history: {history_file}")
    
    def run_learning_cycle(self):
        """Execute complete learning cycle"""
        print("\n" + "="*80)
        print("🧠 CONTINUOUS LEARNING CYCLE - START")
        print("="*80)
        print(f"Time: {datetime.now()}")
        print("="*80 + "\n")
        
        cycle_start = datetime.now()
        
        try:
            # Step 1: Hunt new data
            new_data = self.hunt_new_data()
            
            # Step 2: Validate & clean
            clean_df = self.validate_and_clean(new_data)
            
            if len(clean_df) == 0:
                print("\n⚠️  No valid new data found. Skipping training.")
                return
            
            # Step 3: Merge with existing
            merged_df, merged_file = self.merge_with_existing(clean_df)
            
            # Step 4: Retrain model
            new_metrics = self.retrain_model()
            
            if new_metrics is None:
                print("\n⚠️  Training failed. Keeping existing model.")
                return
            
            # Step 5: Compare models
            result = self.compare_models(new_metrics)
            
            # Save history
            self.save_learning_history()
            
            # Summary
            cycle_duration = (datetime.now() - cycle_start).total_seconds()
            
            print("\n" + "="*80)
            print("✅ LEARNING CYCLE COMPLETE")
            print("="*80)
            print(f"Duration: {cycle_duration:.1f} seconds")
            print(f"New matches: {len(clean_df)}")
            print(f"Total dataset: {len(merged_df)}")
            print(f"Best accuracy: {self.best_model_accuracy:.3f}")
            print(f"Result: {result}")
            print("="*80 + "\n")
            
        except Exception as e:
            print(f"\n❌ ERROR in learning cycle: {e}")
            import traceback
            traceback.print_exc()


def run_continuous_learning():
    """Main entry point"""
    learner = ContinuousLearner()
    learner.run_learning_cycle()


if __name__ == '__main__':
    run_continuous_learning()
