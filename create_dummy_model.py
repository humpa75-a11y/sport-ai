import pickle

# Create a dummy object to act as the model
dummy_model = {
    'models': {},
    'scaler': None,
    'feature_names': [],
    'learning_history': {
        'exact_score_accuracy': [0],
        'mae_home': [0],
        'mae_away': [0],
        'matches_learned_from': 0,
        'training_iterations': 0
    },
    'competition_performance': {},
    'timestamp': '20240101_000000',
    'version': 'DUMMY_v0.1'
}

# Save the dummy model to the path the application expects
with open('data/de_meester.pkl', 'wb') as f:
    pickle.dump(dummy_model, f)

print("Dummy model 'de_meester.pkl' created in 'data/' directory.")
