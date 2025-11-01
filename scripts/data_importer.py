"""
Data Importer for football.json

This script is responsible for loading, parsing, and transforming data
from the openfootball/football.json repository into a format
compatible with our AI's training pipeline.
"""

import os
import json
import pandas as pd
from difflib import get_close_matches

class DataImporter:
    def __init__(self, repo_path, name_mapping_path='../data/team_name_mapping.json'):
        self.repo_path = repo_path
        self.name_mapping = self._load_json(name_mapping_path)
        if self.name_mapping:
            self.canonical_names = list(self.name_mapping.values())
        else:
            self.canonical_names = []
            print("⚠️ Team name mapping is empty. Name matching will be limited.")

    def _load_json(self, file_path):
        """Loads a JSON file."""
        if not os.path.exists(file_path):
            print(f"⚠️ Warning: File not found at {file_path}")
            return {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️ Error decoding JSON from {file_path}")
            return {}

    def _find_canonical_name(self, team_name):
        """Finds the canonical name for a given team name."""
        if not team_name:
            return None
        if team_name in self.canonical_names:
            return team_name
        
        if team_name in self.name_mapping:
            return self.name_mapping[team_name]
        
        # Fuzzy match as a fallback
        matches = get_close_matches(team_name, self.canonical_names, n=1, cutoff=0.8)
        if matches:
            return matches[0]
            
        return None

    def load_and_transform_data(self, start_year=2015):
        """
        Loads and transforms data from all available leagues and years.
        """
        all_matches = []
        print(f"🔍 Scanning for all league data from {start_year} onwards in {self.repo_path}...")

        for root, dirs, files in os.walk(self.repo_path):
            # Sort dirs to process seasons chronologically, helps with debugging
            dirs.sort()
            for file in sorted(files):
                if file.endswith('.json'):
                    try:
                        # Extract year from directory path like './2022-23'
                        year_str_match = [part for part in root.split(os.sep) if part.startswith(str(start_year)[:2])]
                        if not year_str_match:
                            continue
                        
                        year_str = year_str_match[-1]
                        year = int(year_str.split('-')[0])

                        if year >= start_year:
                            file_path = os.path.join(root, file)
                            # print(f"  -> Found and processing: {file_path}")
                            season_data = self._load_json(file_path)
                            if not season_data:
                                continue

                            league_name = season_data.get('name', 'Unknown League')
                            
                            for match in season_data.get('matches', []):
                                home_team = self._find_canonical_name(match.get('team1'))
                                away_team = self._find_canonical_name(match.get('team2'))
                                
                                if home_team and away_team and 'score' in match and match['score'] and 'ft' in match['score'] and isinstance(match['score']['ft'], list) and len(match['score']['ft']) == 2:
                                    transformed_match = {
                                        'date': match.get('date'),
                                        'team1': home_team,
                                        'team2': away_team,
                                        'score1': match['score']['ft'][0],
                                        'score2': match['score']['ft'][1],
                                        'League': league_name
                                    }
                                    all_matches.append(transformed_match)
                                # else:
                                #     if not home_team: print(f"      ⚠️ Unmatched team: {match.get('team1')} in {league_name}")
                                #     if not away_team: print(f"      ⚠️ Unmatched team: {match.get('team2')} in {league_name}")
                    
                    except (ValueError, IndexError):
                        # Ignore directories that don't match the expected year format
                        pass
                    except Exception as e:
                        print(f"   - Error processing file {file}: {e}")

        if not all_matches:
            print("❌ No data could be loaded. Please check the repository path and file structure.")
            return pd.DataFrame()

        df = pd.DataFrame(all_matches)
        df = df.dropna(subset=['score1', 'score2', 'date'])
        df['score1'] = df['score1'].astype(int)
        df['score2'] = df['score2'].astype(int)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date'])
        
        print(f"✅ Successfully loaded and transformed {len(df)} matches from football.json.")
        return df

if __name__ == '__main__':
    # This is a test run to demonstrate the importer's functionality.
    
    dummy_repo_path = '../temp_football_json'
    dummy_mapping_path = '../data/team_name_mapping.json'

    # Ensure dummy mapping exists for test
    if not os.path.exists(dummy_mapping_path):
         os.makedirs(os.path.dirname(dummy_mapping_path), exist_ok=True)
         dummy_mapping = {
             "Man United": "Manchester United", "Man Utd": "Manchester United",
             "Arsenal": "Arsenal", "Arsenal FC": "Arsenal",
             "Crystal Palace": "Crystal Palace", "Crystal Palace FC": "Crystal Palace",
             "Brighton": "Brighton & Hove Albion", "Brighton & Hove": "Brighton & Hove Albion",
             "Spurs": "Tottenham Hotspur", "Tottenham": "Tottenham Hotspur",
         }
         with open(dummy_mapping_path, 'w', encoding='utf-8') as f:
            json.dump(dummy_mapping, f)

    print("\n--- Running Importer Test ---")
    importer = DataImporter(repo_path=dummy_repo_path, name_mapping_path=dummy_mapping_path)
    df = importer.load_and_transform_data(start_year=2020)
    
    print("\n--- Transformed DataFrame ---")
    if not df.empty:
        print(df.head())
        print(f"\nLoaded {len(df)} matches.")
        print("\n--- DataFrame Info ---")
        df.info()
    else:
        print("No data was loaded.")
    
    print("\n--- Test Complete ---")
