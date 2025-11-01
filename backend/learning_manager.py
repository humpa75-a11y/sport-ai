"""
🧠 AI LEARNING MANAGER - Het geheugen van de Ultimate Meester 🧠

Deze module is verantwoordelijk voor het beheren van het leerproces van de AI.
Het slaat elke voorspelling en het werkelijke resultaat op, en berekent
continu de performance metrics van het model.

Functies:
- Logt elke voorspelling en resultaat.
- Berekent en update MAE (Mean Absolute Error) en Exact Score Accuracy.
- Slaat de leergeschiedenis op in een gestructureerd JSON-bestand.
- Biedt functies om de prestaties van de AI te analyseren.
"""

import json
import os
from datetime import datetime
import numpy as np

LEARNING_LOG_FILE = os.path.join(os.path.dirname(__file__), '../data/learning_log.json')

class LearningManager:
    def __init__(self):
        """Initialiseer de Learning Manager."""
        self.log_data = self._load_log()
        print("🧠 Learning Manager geïnitialiseerd.")

    def _load_log(self):
        """Laad de learning log uit het JSON-bestand."""
        try:
            if os.path.exists(LEARNING_LOG_FILE):
                with open(LEARNING_LOG_FILE, 'r') as f:
                    data = json.load(f)
                    # Zorg ervoor dat de basisstructuur aanwezig is
                    if 'predictions' not in data: data['predictions'] = []
                    if 'performance' not in data: data['performance'] = {}
                    return data
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️ Kon learning log niet laden, begin met een nieuwe. Fout: {e}")
        
        # Start met een schone lei als er iets misgaat
        return {
            "predictions": [],
            "performance": {
                "total_predictions": 0,
                "exact_matches": 0,
                "exact_score_accuracy": 0.0,
                "mae_home": 0.0,
                "mae_away": 0.0,
                "combined_mae": 0.0,
                "last_updated": None
            }
        }

    def _save_log(self):
        """Sla de learning log op naar het JSON-bestand."""
        try:
            os.makedirs(os.path.dirname(LEARNING_LOG_FILE), exist_ok=True)
            with open(LEARNING_LOG_FILE, 'w') as f:
                json.dump(self.log_data, f, indent=4)
        except IOError as e:
            print(f"🔥 Kritieke Fout: Kon learning log niet opslaan! Fout: {e}")

    def log_prediction(self, home_team, away_team, prediction_result, actual_home_goals, actual_away_goals):
        """
        Log een nieuwe voorspelling en het werkelijke resultaat.
        Dit is de kern van het leerproces.
        """
        # 1. Extraheer de meest waarschijnlijke voorspelling
        top_prediction = prediction_result['top_exact_scores'][0]['score']
        pred_home, pred_away = map(int, top_prediction.split(' - '))

        # 2. Bepaal of de voorspelling exact correct was
        is_exact_match = (pred_home == actual_home_goals and pred_away == actual_away_goals)

        # 3. Creëer een log entry
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "home_team": home_team,
            "away_team": away_team,
            "predicted_score": f"{pred_home} - {pred_away}",
            "actual_score": f"{actual_home_goals} - {actual_away_goals}",
            "predicted_home_goals": pred_home,
            "predicted_away_goals": pred_away,
            "actual_home_goals": actual_home_goals,
            "actual_away_goals": actual_away_goals,
            "is_exact_match": is_exact_match,
            "confidence": prediction_result.get('confidence_factor', 0),
            "engine": prediction_result.get('prediction_method', 'N/A')
        }

        # 4. Voeg toe aan de log en update de performance
        self.log_data['predictions'].append(log_entry)
        self._update_performance()
        
        # 5. Sla de wijzigingen op
        self._save_log()
        
        print(f"🧠 Nieuwe kennis opgeslagen: {home_team} vs {away_team}. Exacte match: {'✅' if is_exact_match else '❌'}")
        return log_entry

    def _update_performance(self):
        """Herbereken de performance metrics op basis van de volledige log."""
        predictions = self.log_data['predictions']
        total_predictions = len(predictions)

        if total_predictions == 0:
            return

        # Bereken Exact Score Accuracy
        exact_matches = sum(1 for p in predictions if p['is_exact_match'])
        exact_score_accuracy = (exact_matches / total_predictions) * 100

        # Bereken Mean Absolute Error (MAE)
        errors_home = [abs(p['predicted_home_goals'] - p['actual_home_goals']) for p in predictions]
        errors_away = [abs(p['predicted_away_goals'] - p['actual_away_goals']) for p in predictions]
        
        mae_home = np.mean(errors_home)
        mae_away = np.mean(errors_away)
        combined_mae = (mae_home + mae_away) / 2

        # Update de performance data
        self.log_data['performance'] = {
            "total_predictions": total_predictions,
            "exact_matches": exact_matches,
            "exact_score_accuracy": round(exact_score_accuracy, 2),
            "mae_home": round(mae_home, 4),
            "mae_away": round(mae_away, 4),
            "combined_mae": round(combined_mae, 4),
            "last_updated": datetime.now().isoformat()
        }
        print("📈 AI performance metrics geüpdatet.")

    def get_performance_report(self):
        """Haal het meest recente performance rapport op."""
        return self.log_data.get('performance', {})

    def get_learning_history(self, limit=100):
        """Haal de laatste N voorspellingen op."""
        return self.log_data['predictions'][-limit:]

    def get_analytical_summary(self):
        """
        Genereert een 'Llama-stijl' kwalitatieve analyse van de AI's performance.
        Dit is de AI-assistent die zijn eigen prestaties analyseert.
        """
        perf = self.get_performance_report()
        if perf['total_predictions'] < 10:
            return {
                "title": "Analyse niet mogelijk",
                "summary": "Onvoldoende data. Er zijn minimaal 10 voorspellingen nodig voor een betrouwbare analyse.",
                "recommendations": ["Maak meer voorspellingen om de analyse te starten."]
            }

        # Analyseer de performance
        accuracy = perf['exact_score_accuracy']
        mae = perf['combined_mae']
        
        # Titel
        title = "AI Performance Analyse: "
        if accuracy > 15:
            title += "🏆 Uitstekend!"
        elif accuracy > 10:
            title += "📈 Goed en Stabiel"
        else:
            title += "⚠️ Ruimte voor Verbetering"

        # Samenvatting
        summary = (
            f"Na {perf['total_predictions']} voorspellingen, heeft de AI een exacte score nauwkeurigheid van {accuracy}%. "
            f"Dit is {'boven' if accuracy > 12 else 'rond' if accuracy > 8 else 'onder'} de industriestandaard van 10-12%. "
            f"De gemiddelde goal-afwijking (MAE) is {mae:.2f} goals per wedstrijd, wat duidt op een "
            f"{'zeer hoge' if mae < 0.8 else 'goede' if mae < 1.0 else 'redelijke'} precisie in het voorspellen van het aantal goals."
        )

        # Aanbevelingen
        recommendations = []
        if accuracy < 10:
            recommendations.append("De exacte score nauwkeurigheid is een aandachtspunt. Overweeg het model te hertrainen met meer data of de feature engineering te verfijnen.")
        if mae > 1.0:
            recommendations.append("De MAE is relatief hoog. Analyseer de 'feature importance' om te zien welke data de meeste ruis veroorzaakt.")
        if accuracy > 15 and mae < 0.8:
            recommendations.append("De prestaties zijn uitstekend. Focus op het verder uitbreiden van de team database om deze hoge kwaliteit te behouden.")
        else:
            recommendations.append("De prestaties zijn solide. Blijf het model voeden met nieuwe wedstrijdresultaten om de nauwkeurigheid verder te verhogen via autonoom leren.")

        return {
            "title": title,
            "summary": summary,
            "recommendations": recommendations,
            "metrics": perf
        }
