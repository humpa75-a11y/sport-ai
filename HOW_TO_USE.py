"""
🚨 BELANGRIJK: Server Management Script 🚨

Dit script zorgt ervoor dat je weet hoe je de server moet beheren.
"""

print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║           🏆 DE MEESTER - SERVER MANAGEMENT INSTRUCTIES 🏆            ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

📖 HOE WERKT HET SYSTEEM?

1️⃣  START DE SERVER (Eenmalig):
    Windows: Dubbelklik op "start_server.bat"
    Mac/Linux: Voer uit: python backend/app.py
    
    ✅ De server draait nu op: http://localhost:5000
    ✅ Laat deze terminal OPEN!

2️⃣  TRAIN DE AI (In een NIEUWE terminal):
    Windows: Dubbelklik op "train_ai.bat"
    Mac/Linux: Open een NIEUWE terminal en voer uit: python scripts/train_model.py
    
    ✅ De training start
    ✅ De server blijft gewoon draaien!
    ✅ Na training: verbeteringen zijn automatisch actief

⚠️  BELANGRIJK:
    - Start de server in ÉÉN terminal
    - Laat die terminal OPEN
    - Train de AI in een ANDERE terminal
    - Zo blijft alles live en werkend!

🌐 Links:
    - Dashboard: http://localhost:5000
    - Status: http://localhost:5000/api/status
    - Analytics: http://localhost:5000/api/analytics

╔══════════════════════════════════════════════════════════════════════╗
║                         VEEL SUCCES! 🚀                               ║
╚══════════════════════════════════════════════════════════════════════╝
""")
