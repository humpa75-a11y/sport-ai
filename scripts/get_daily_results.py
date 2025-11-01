"""
⚽ GET DAILY RESULTS - De Ogen en Oren van de Meester ⚽

Dit script wordt dagelijks aangeroepen door de learning_scheduler.
Het heeft één taak: de meest recente data downloaden en filteren
zodat alleen de wedstrijden van gisteren overblijven.

Output: Een CSV-geformatteerde string naar stdout als er resultaten zijn.
"""

import pandas as pd
import requests
import io
from datetime import datetime, timedelta
import sys

# Definieer de competities en hun codes (alleen voor het huidige seizoen)
LEAGUES = {
    "Premier League (ENG)": "E0",
    "Championship (ENG)": "E1",
    "La Liga (ESP)": "SP1",
    "La Liga 2 (ESP)": "SP2",
    "Bundesliga (GER)": "D1",
    "Bundesliga 2 (GER)": "D2",
    "Serie A (ITA)": "I1",
    "Serie B (ITA)": "I2",
    "Ligue 1 (FRA)": "F1",
    "Ligue 2 (FRA)": "F2",
    "Eredivisie (NED)": "N1",
    "Jupiler Pro League (BEL)": "B1",
    "Primeira Liga (POR)": "P1",
    "Süper Lig (TUR)": "T1",
    "Super League (GRE)": "G1",
    "Premiership (SCO)": "SC0",
    "Women's Super League (ENG)": "E0", # Gebruikt dezelfde code, maar andere URL-structuur
    "Liga Profesional (ARG)": "ARG",
    "Serie A (BRA)": "BRA",
    "Liga MX (MEX)": "MEX",
    "MLS (USA)": "USA",
}

def get_yesterdays_matches():
    """
    Download data voor het huidige seizoen en filtert op wedstrijden van gisteren.
    Retourneert een pandas DataFrame met de resultaten.
    """
    # Bepaal het huidige seizoen (bv. 2526 voor oktober 2025)
    now = datetime.now()
    current_year = now.year
    season_start_year = current_year if now.month >= 7 else current_year - 1
    season_str = str(season_start_year)[-2:] + str(season_start_year + 1)[-2:]

    yesterday = now.date() - timedelta(days=1)
    all_results = []

    print(f"🔍 Scraper gestart: Zoeken naar resultaten van {yesterday.strftime('%d-%m-%Y')}...")

    for league_name, league_code in LEAGUES.items():
        # Speciale URL voor Engelse vrouwencompetitie
        if "Women" in league_name:
            url = f"https://www.football-data.co.uk/mmz4281/{season_str}/E0_womens.csv"
        else:
            url = f"https://www.football-data.co.uk/mmz4281/{season_str}/{league_code}.csv"
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Genereert een error bij slechte statuscodes (404, 500 etc.)
            
            # Gebruik 'latin-1' encoding voor bredere compatibiliteit
            df = pd.read_csv(io.StringIO(response.content.decode('latin-1')))
            
            # Converteer datum en filter
            df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.date
            
            # Filter op wedstrijden van gisteren
            yesterdays_games = df[df['Date'] == yesterday]
            
            if not yesterdays_games.empty:
                print(f"  ✅ {len(yesterdays_games)} resultaat(en) gevonden in {league_name}")
                all_results.append(yesterdays_games)

        except requests.exceptions.HTTPError as e:
            # Negeer 404-fouten, dit betekent dat de data voor dat seizoen/competitie nog niet beschikbaar is
            if e.response.status_code != 404:
                print(f"  ⚠️ Kon {league_name} niet downloaden. Fout: {e}")
        except Exception as e:
            print(f"  ❌ Onverwachte fout bij verwerken van {league_name}: {e}")

    if not all_results:
        print("✅ Geen wedstrijden gevonden voor gisteren.")
        return pd.DataFrame()

    # Combineer alle gevonden resultaten
    final_df = pd.concat(all_results, ignore_index=True)
    print(f"📈 Totaal {len(final_df)} resultaten gevonden voor de leersessie.")
    return final_df

if __name__ == "__main__":
    results_df = get_yesterdays_matches()
    
    # Als er resultaten zijn, print ze naar stdout in CSV-formaat
    # De scheduler kan deze output dan opvangen en verwerken.
    if not results_df.empty:
        print("\n--- DAILY RESULTS CSV START ---")
        print(results_df.to_csv(index=False))
        print("--- DAILY RESULTS CSV END ---")
        sys.exit(0) # Succesvolle exit code
    
    sys.exit(1) # Exit code die aangeeft dat er geen data is
