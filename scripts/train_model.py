import pandas as pd
from backend.prediction_engine import DeMeester
import os

def train_model():
    """
    This script trains the DeMeester AI model using historical data.
    """
    print("Starting model training...")

    # Find the latest CSV file with historical data
    data_files = [f for f in os.listdir('.') if f.endswith('.csv') and 'odds' in f]
    if not data_files:
        print("No data files found. Please make sure you have a csv file with odds data in the root directory.")
        return

    latest_file = max(data_files, key=lambda f: os.path.getmtime(f))
    print(f"Using data from: {latest_file}")

    # Load the data
    try:
        data = pd.read_csv(latest_file)
        # Drop rows with missing essential data
        data.dropna(subset=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG'], inplace=True)
    except Exception as e:
        print(f"Error loading data file: {e}")
        return

    # Initialize the AI
    meester = DeMeester(model_path='data/de_meester.pkl')

    # Engineer features
    X, y_home, y_away = meester.engineer_advanced_features(data)

    # Train the model
    meester.train_meester_ensemble(X, y_home, y_away)

    print("Model training completed.")

if __name__ == '__main__':
    train_model()
