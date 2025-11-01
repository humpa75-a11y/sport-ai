// static/script.js

document.addEventListener('DOMContentLoaded', () => {
    const predictForm = document.getElementById('predict-form');
    const predictButton = document.getElementById('predict-button');
    const predictionResultDiv = document.getElementById('prediction-result');
    const statusReportPre = document.getElementById('status-report');

    // Functie om de AI-status op te halen en weer te geven
    const fetchStatus = async () => {
        try {
            const response = await fetch('http://127.0.0.1:5000/api/status');
            const data = await response.json();
            statusReportPre.textContent = data.status_report;
        } catch (error) {
            statusReportPre.textContent = 'Kon de status van de AI niet laden. Is de backend server gestart?';
            console.error('Fout bij ophalen status:', error);
        }
    };

    // Functie om een voorspelling aan te vragen
    predictForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const homeTeam = document.getElementById('home-team').value;
        const awayTeam = document.getElementById('away-team').value;

        if (!homeTeam || !awayTeam) {
            alert('Vul alstublieft beide teamnamen in.');
            return;
        }

        predictButton.disabled = true;
        predictButton.textContent = 'Voorspellen...';
        predictionResultDiv.classList.add('hidden');

        try {
            const response = await fetch('http://127.0.0.1:5000/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ home_team: homeTeam, away_team: awayTeam }),
            });

            const data = await response.json();

            if (response.ok) {
                displayPrediction(data);
            } else {
                alert(`Fout: ${data.error}`);
            }
        } catch (error) {
            alert('Er is een fout opgetreden bij het verbinden met de server.');
            console.error('Fout bij voorspellen:', error);
        } finally {
            predictButton.disabled = false;
            predictButton.textContent = 'Voorspel Score';
        }
    });

    // Functie om het voorspellingsresultaat weer te geven
    const displayPrediction = (data) => {
        const { home_team, away_team, prediction } = data;

        let top5Html = '';
        prediction.top_5_scores.forEach(item => {
            const label = item.label || '';
            let cardClass = 'bronze'; // Default
            if (label.includes('GOUDEN')) cardClass = 'gold';
            else if (label.includes('Zilveren')) cardClass = 'silver';

            top5Html += `
                <div class="score-card ${cardClass}">
                    <div class="score-card-header">${label}</div>
                    <div class="score">${item.score}</div>
                    <div class="probability">
                        <div class="progress-bar" style="width: ${item.probability}%;"></div>
                        <span>${item.probability}%</span>
                    </div>
                </div>
            `;
        });

        predictionResultDiv.innerHTML = `
            <div class="result-header">
                <h2>Voorspelling voor: <span>${home_team}</span> vs <span>${away_team}</span></h2>
                <p class="confidence">Model Zekerheid: <strong>${prediction.confidence_factor}%</strong></p>
            </div>
            <div class="scores-container">
                ${top5Html}
            </div>
            <div class="prediction-meta">
                <p>Verwachte goals: Thuis (<strong>${prediction.expected_home_goals}</strong>) - Uit (<strong>${prediction.expected_away_goals}</strong>)</p>
                <p>Methode: <em>${prediction.prediction_method}</em></p>
            </div>
        `;
        predictionResultDiv.classList.remove('hidden');
    };

    // Laad de status bij het opstarten
    fetchStatus();
});
