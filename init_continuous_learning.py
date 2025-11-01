"""
🔄 INITIALISEER CONTINUOUS LEARNING met bestaande data
"""
import json
import pickle
import os

print("\n" + "="*80)
print("🔄 INITIALISEREN CONTINUOUS LEARNING SYSTEEM")
print("="*80)

# Check existing model
model_file = 'data/de_meester.pkl'
if os.path.exists(model_file):
    with open(model_file, 'rb') as f:
        model_data = pickle.load(f)
    
    accuracy_info = model_data.get('accuracy', {})
    history_info = model_data.get('learning_history', {})
    
    print(f"\n✅ MODEL GEVONDEN:")
    print(f"   Training samples: {accuracy_info.get('training_samples', 0)}")
    print(f"   Accuracy: {accuracy_info.get('exact_score_accuracy', 0):.1f}%")
    print(f"   MAE Thuis: {accuracy_info.get('mae_home', 0):.3f}")
    print(f"   MAE Uit: {accuracy_info.get('mae_away', 0):.3f}")
    
    # Create stats file
    stats = {
        'last_update': history_info.get('trained_at', '2025-10-16T17:42:31'),
        'total_trainings': 1,
        'accuracy': accuracy_info.get('exact_score_accuracy', 8.5),
        'total_matches': history_info.get('total_matches', 1756),
        'improvements': [
            {
                'date': history_info.get('trained_at', '2025-10-16T17:42:31'),
                'accuracy': accuracy_info.get('exact_score_accuracy', 8.5),
                'improvement': 0.0
            }
        ]
    }
    
    stats_file = 'data/learning_stats.json'
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"\n💾 STATS AANGEMAAKT:")
    print(f"   Bestand: {stats_file}")
    print(f"   Accuracy: {stats['accuracy']:.1f}%")
    print(f"   Totaal matches: {stats['total_matches']}")
    
    print("\n✅ CONTINUOUS LEARNING KLAAR!")
    print("   Run nu: python check_learning_progress.py")
    print("="*80)

else:
    print("\n❌ Geen model gevonden! Run eerst: python ultra_train_massive.py")
