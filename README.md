# 🏆 DE MEESTER - Ultimate AI Football Prediction System

## 🚀 Quick Start - Server blijft ALTIJD draaien!

### 1️⃣ Start de Server (EENMALIG)
Dubbelklik op: **`start_server.bat`**

✅ De server draait nu op: **http://localhost:5000**  
✅ De server blijft ALTIJD draaien in de achtergrond  
✅ Je kunt voorspellingen maken via je browser!

### 2️⃣ Train de AI (Optioneel - Server blijft draaien!)
Dubbelklik op: **`train_ai.bat`**

✅ De AI wordt opnieuw getraind met de laatste data  
✅ De server blijft gewoon draaien!  
✅ Na training zijn de verbeteringen automatisch actief

---

## 📊 Wat kan De Meester?

- 🎯 **Voorspel wedstrijduitslagen** met 12.55% exact score accuracy
- 🎲 **Monte Carlo Simulatie** - Simuleer wedstrijden 1000x
- 📈 **Real-time Analytics** - Zie de prestaties van de AI
- 🧠 **Self-Learning AI** - Leert van echte resultaten
- 🏆 **Feature Importance** - Begrijp waarom de AI bepaalde voorspellingen doet

---

## 🔧 Technische Details

### Training Data
- **35,585 wedstrijden** uit 6 seizoenen
- **40+ geavanceerde features** per wedstrijd
- **5 machine learning modellen** in ensemble

### AI Models
1. Deep Neural Network (10 layers)
2. Gradient Boosting
3. Random Forest
4. XGBoost
5. Extra Trees

### Performance
- **Exact Score Accuracy**: 12.55%
- **Mean Absolute Error**: 0.912
- **Combined MAE**: Home 0.961, Away 0.863

---

## 📁 Project Structuur

```
sport_ai_sync/
├── start_server.bat        ← Start de server (GEBRUIK DIT!)
├── train_ai.bat           ← Train de AI (server blijft draaien)
├── backend/               ← Flask API & AI Engine
│   ├── app.py            ← Main server
│   ├── prediction_engine.py
│   ├── deep_learning_engine.py
│   └── live_feature_generator.py
├── frontend/             ← Web Interface
│   └── index.html        ← Dashboard
├── scripts/              ← Utility scripts
│   └── train_model.py    ← Training script
└── data/                 ← Models & Data
    └── de_meester.pkl    ← Trained AI model
```

---

## 🌐 API Endpoints

- `GET /` - Web Dashboard
- `POST /api/predict` - Voorspel wedstrijd
- `POST /api/simulate` - Monte Carlo simulatie
- `GET /api/status` - AI status
- `GET /api/analytics` - Performance analytics
- `POST /api/learn` - Leer van resultaat
- `GET /api/feature-importance` - Belangrijkste features

---

## 💡 Tips

1. **Server is down?** → Dubbelklik op `start_server.bat`
2. **Slechte voorspellingen?** → Dubbelklik op `train_ai.bat` om opnieuw te trainen
3. **Nieuwe competities toevoegen?** → Bewerk `scripts/train_model.py`
4. **Browser cache problemen?** → Druk op Ctrl+F5 om te verversen

---

## 🏆 Gemaakt door: humpa75-a11y
**De Meester** - Van student tot master! 🎓➡️👑