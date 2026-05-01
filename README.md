<<<<<<< 

```
cd medical_ai
pip install -r requirements.txt
```

### Step 2 — Start Ollama with TinyLlama
Open a NEW terminal and run:
```
ollama run tinyllama
```
Keep this terminal OPEN. Wait until you see the model loaded.

### Step 3 — Start the Flask Server
In your original terminal (inside the medical_ai folder):
```
python app.py
```

### Step 4 — Open in Browser
```
http://localhost:5000
```

---

## 📁 Project Folder Structure
```
medical_ai/
├── app.py                    ← Main Flask server (ALL API routes here)
├── requirements.txt          ← Python packages to install
├── templates/
│   ├── base.html             ← Main layout (sidebar, navbar)
│   ├── index.html            ← Home dashboard
│   ├── symptom_checker.html  ← Symptom analysis
│   ├── medicine_suggester.html ← Medicine suggestions
│   ├── injury_analyzer.html  ← Injury first aid
│   ├── health_risk.html      ← Health risk assessment
│   ├── drug_interaction.html ← Drug interaction checker
│   ├── nutrition.html        ← Diet & nutrition advisor
│   ├── mental_health.html    ← Mental wellness check
│   ├── patient_profile.html  ← Patient data management
│   ├── medical_history.html  ← Medical record timeline
│   ├── nearby_hospitals.html ← Hospital finder (GPS)
│   └── chat_doctor.html      ← AI chat doctor
├── static/                   ← (for custom CSS/JS/images if needed)
└── uploads/                  ← File uploads folder
```

---

## ✨ Features
1. 🩺 **Symptom Checker** — AI analysis of symptoms with possible conditions
2. 💊 **Medicine Suggester** — OTC medicine recommendations
3. 🩹 **Injury Analyzer** — First aid guidance and severity assessment
4. ❤️ **Health Risk Assessment** — Heart, diabetes, hypertension risk scores
5. ⚗️ **Drug Interaction Checker** — Dangerous medication combinations
6. 🥗 **Diet & Nutrition** — Personalized meal plans and calorie targets
7. 🧠 **Mental Health Check** — Wellness assessment and coping strategies
8. 👤 **Patient Profile** — Save and manage patient data
9. 📋 **Medical History** — Track diagnoses, visits, medications
10. 🏥 **Nearby Hospitals** — GPS-based hospital finder with emergency numbers
11. 🤖 **Chat with Dr. AI** — Full conversation medical chatbot

---

## 🔧 Troubleshooting
- **Ollama not running?** → Open terminal, run: `ollama run tinyllama`
- **Slow responses?** → TinyLlama is small, responses take 10-30 seconds
- **Port in use?** → Change port in app.py: `app.run(port=5001)`
- **Model not found?** → Run: `ollama pull tinyllama`

---

## 💡 Want Better AI Responses?
Try a bigger model (if your PC has more RAM):
```
ollama run llama3.2    ← Better quality, needs 4GB RAM
ollama run mistral     ← Great for medical, needs 4GB RAM
ollama run phi3        ← Good balance of speed + quality
```
Then change `model="tinyllama"` to `model="llama3.2"` in app.py

---

⚠️ **Disclaimer**: This is an educational project. Not for actual medical diagnosis or treatment.
=======

>>>>>>> 
