from flask import Flask, render_template, request, jsonify, session
import os
from dotenv import load_dotenv
load_dotenv()

import requests
import json
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = "medical_ai_secret_2024"

# ─── Load API Key from .env (add GROQ_API_KEY=your_key to .env file) ─────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# ──────────────────────────────────────────────────────────────────────────────

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = GROQ_MODEL = "llama-3.1-8b-instant"  # Free & Fast!

# ─── In-memory stores ────────────────────────────────────────────────────────
patients_db    = {}
chat_histories = {}

# ─── Groq helper ─────────────────────────────────────────────────────────────
def ask_groq(prompt: str, system: str = "") -> str:
    try:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": GROQ_MODEL,
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.7
        }
        r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except requests.exceptions.ConnectionError:
        return "❌ Internet connection error. Please check your connection."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def ask_groq_chat(messages: list) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": GROQ_MODEL,
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.7
        }
        r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ─── Routes ──────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

# 1. Symptom Checker
@app.route("/symptom-checker")
def symptom_checker():
    return render_template("symptom_checker.html")

@app.route("/api/analyze-symptoms", methods=["POST"])
def analyze_symptoms():
    data     = request.json
    symptoms = data.get("symptoms", "")
    age      = data.get("age", "unknown")
    gender   = data.get("gender", "unknown")
    duration = data.get("duration", "unknown")

    system = """You are an expert medical AI assistant. Analyze symptoms and provide:
1. Possible conditions (list 3-5)
2. Severity level (Low/Medium/High/Emergency)
3. Recommended actions
4. Warning signs to watch for
5. Suggested specialist type
Format clearly with headings. Add disclaimer: consult a real doctor."""

    prompt = f"Patient: {age} year old {gender}. Symptoms: {symptoms}. Duration: {duration}."
    result = ask_groq(prompt, system)
    return jsonify({"result": result, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")})

# 2. Medicine Suggester
@app.route("/medicine-suggester")
def medicine_suggester():
    return render_template("medicine_suggester.html")

@app.route("/api/suggest-medicine", methods=["POST"])
def suggest_medicine():
    data      = request.json
    condition = data.get("condition", "")
    allergies = data.get("allergies", "none")
    age       = data.get("age", "adult")

    system = """You are a pharmacology expert AI. Suggest medicines and provide:
1. Common OTC medicines for this condition
2. Dosage guidelines (general)
3. Side effects to watch
4. Drug interactions to avoid
5. When to see a doctor immediately
6. Natural/home remedies as alternatives
IMPORTANT DISCLAIMER: Always recommend consulting a licensed pharmacist or doctor."""

    prompt = f"Condition: {condition}. Patient age: {age}. Known allergies: {allergies}."
    result = ask_groq(prompt, system)
    return jsonify({"result": result})

# 3. Injury Analyzer
@app.route("/injury-analyzer")
def injury_analyzer():
    return render_template("injury_analyzer.html")

@app.route("/api/analyze-injury", methods=["POST"])
def analyze_injury():
    description = request.form.get("description", "")
    location    = request.form.get("location", "")
    pain_level  = request.form.get("pain_level", "5")

    system = """You are an emergency medicine AI expert. Based on injury description:
1. Assess injury severity (Minor/Moderate/Severe/Critical)
2. Immediate first aid steps
3. What NOT to do
4. Whether ER visit is needed (Yes/No/Maybe)
5. Expected recovery timeline
6. Follow-up care tips"""

    prompt = f"Injury location: {location}. Pain level: {pain_level}/10. Description: {description}"
    result = ask_groq(prompt, system)
    return jsonify({"result": result})

# 4. Patient Profile
@app.route("/patient-profile")
def patient_profile():
    return render_template("patient_profile.html")

@app.route("/api/save-patient", methods=["POST"])
def save_patient():
    data = request.json
    pid  = data.get("id") or str(uuid.uuid4())[:8]
    patients_db[pid] = {**data, "id": pid, "updated": datetime.now().isoformat()}
    return jsonify({"success": True, "id": pid, "message": "Patient profile saved!"})

@app.route("/api/get-patient/<pid>")
def get_patient(pid):
    p = patients_db.get(pid)
    if p:
        return jsonify(p)
    return jsonify({"error": "Patient not found"}), 404

@app.route("/api/list-patients")
def list_patients():
    return jsonify(list(patients_db.values()))

# 5. AI Chat Doctor
@app.route("/chat-doctor")
def chat_doctor():
    return render_template("chat_doctor.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data       = request.json
    user_msg   = data.get("message", "")
    session_id = data.get("session_id", "default")

    if session_id not in chat_histories:
        chat_histories[session_id] = [
            {"role": "system", "content": """You are Dr. MedAI, a helpful virtual medical assistant.
You provide clear, empathetic medical information and guidance.
Always recommend consulting a real doctor for diagnosis and treatment.
Be concise but thorough. Use simple language."""}
        ]

    chat_histories[session_id].append({"role": "user", "content": user_msg})
    reply = ask_groq_chat(chat_histories[session_id])
    chat_histories[session_id].append({"role": "assistant", "content": reply})

    if len(chat_histories[session_id]) > 22:
        chat_histories[session_id] = chat_histories[session_id][:1] + chat_histories[session_id][-20:]

    return jsonify({"reply": reply, "session_id": session_id})

# 6. Health Risk Assessment
@app.route("/health-risk")
def health_risk():
    return render_template("health_risk.html")

@app.route("/api/assess-risk", methods=["POST"])
def assess_risk():
    data = request.json
    system = """You are a preventive medicine specialist AI. Assess health risks and provide:
1. Overall Risk Score (1-10) for: Heart Disease, Diabetes, Hypertension, Cancer
2. Key risk factors identified
3. Lifestyle recommendations (top 5)
4. Recommended medical screenings
5. Diet & exercise suggestions
6. 3-month health improvement plan
Be specific and actionable."""

    prompt = f"""Patient data:
Age: {data.get('age')}, Gender: {data.get('gender')}, Height: {data.get('height')}cm, Weight: {data.get('weight')}kg
Smoking: {data.get('smoking')}, Alcohol: {data.get('alcohol')}, Exercise: {data.get('exercise')} days/week
Family history: {data.get('family_history')}, Existing conditions: {data.get('conditions')}
Sleep hours: {data.get('sleep')}, Stress level: {data.get('stress')}/10"""

    result = ask_groq(prompt, system)
    return jsonify({"result": result})

# 7. Nearby Hospitals
@app.route("/nearby-hospitals")
def nearby_hospitals():
    return render_template("nearby_hospitals.html")

# 8. Medical History
@app.route("/medical-history")
def medical_history():
    return render_template("medical_history.html")

@app.route("/api/save-history", methods=["POST"])
def save_history():
    data = request.json
    pid  = data.get("patient_id", "guest")
    if pid not in patients_db:
        patients_db[pid] = {"id": pid, "name": "Guest", "history": []}
    if "history" not in patients_db[pid]:
        patients_db[pid]["history"] = []
    entry = {**data, "id": str(uuid.uuid4())[:8], "date": datetime.now().isoformat()}
    patients_db[pid]["history"].append(entry)
    return jsonify({"success": True, "entry": entry})

@app.route("/api/get-history/<pid>")
def get_history(pid):
    p = patients_db.get(pid, {})
    return jsonify(p.get("history", []))

# 9. Drug Interaction Checker
@app.route("/drug-interaction")
def drug_interaction():
    return render_template("drug_interaction.html")

@app.route("/api/check-interaction", methods=["POST"])
def check_interaction():
    data  = request.json
    drugs = data.get("drugs", [])

    system = """You are a clinical pharmacist AI. Check drug interactions and provide:
1. Interaction severity for each pair (None/Minor/Moderate/Major/Contraindicated)
2. What the interaction causes
3. Symptoms to watch for
4. Management recommendations
5. Safe alternatives if needed"""

    prompt = f"Check interactions between these medications: {', '.join(drugs)}"
    result = ask_groq(prompt, system)
    return jsonify({"result": result})

# 10. Nutrition Advisor
@app.route("/nutrition")
def nutrition():
    return render_template("nutrition.html")

@app.route("/api/nutrition-advice", methods=["POST"])
def nutrition_advice():
    data = request.json
    system = """You are a certified nutritionist and dietitian AI. Provide:
1. Personalized daily calorie target
2. Macro breakdown (protein/carbs/fats in grams)
3. Foods to EAT MORE (with reasons)
4. Foods to AVOID (with reasons)
5. 3-day sample meal plan
6. Key vitamins/minerals to focus on
7. Hydration recommendations"""

    prompt = f"""Patient: Age {data.get('age')}, {data.get('gender')}, {data.get('weight')}kg, {data.get('height')}cm
Goal: {data.get('goal')}, Activity: {data.get('activity')}, Conditions: {data.get('conditions')}
Dietary restrictions: {data.get('restrictions')}"""

    result = ask_groq(prompt, system)
    return jsonify({"result": result})

# 11. Mental Health Check
@app.route("/mental-health")
def mental_health():
    return render_template("mental_health.html")

@app.route("/api/mental-health-check", methods=["POST"])
def mental_health_check():
    data = request.json
    system = """You are a compassionate mental health AI counselor. Based on responses:
1. Identify potential mental health concerns (not diagnosis)
2. Stress & anxiety level assessment
3. Coping strategies (5 practical tips)
4. Daily habits for better mental health
5. When to seek professional help
6. Crisis resources if needed
Be empathetic, supportive, and non-judgmental."""

    prompt = f"""Mood assessment:
Sleep quality: {data.get('sleep')}/10, Energy: {data.get('energy')}/10
Anxiety: {data.get('anxiety')}/10, Mood: {data.get('mood')}/10
Main concerns: {data.get('concerns')}
Recent events: {data.get('events')}"""

    result = ask_groq(prompt, system)
    return jsonify({"result": result})

# 12. Status check
@app.route("/api/status")
def status():
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        r = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=5)
        if r.status_code == 200:
            return jsonify({"status": "online", "provider": "Groq"})
        return jsonify({"status": "offline"})
    except:
        return jsonify({"status": "offline"})

if __name__ == "__main__":
    print("🏥 Medical AI Assistant Starting...")
    print("📍 Open: http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)