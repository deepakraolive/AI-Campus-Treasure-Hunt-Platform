import os
import json
import time
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

DB_FILE = 'database.json'

# Attempt to import google-generativeai for AI Engine feature
try:
    import google.generativeai as genai
    if "GEMINI_API_KEY" in os.environ:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        GEMINI_AVAILABLE = True
    else:
        GEMINI_AVAILABLE = False
except ImportError:
    GEMINI_AVAILABLE = False

# Hardcoded LPU Specific Clues with Coordinates (Sequential path)
CLUES = [
    {
        "id": "loc_1",
        "name": "Main Gate",
        "question": "The main entry point with heavy security.", 
        "answer": "main gate",
        "hint": "It's the gateway to the universe... I mean, university.",
        "lat": 31.2536,
        "lng": 75.7036
    },
    {
        "id": "loc_2",
        "name": "Block 32",
        "question": "Where indoor sports and grand events take place.", 
        "answer": "shanti devi mittal auditorium",
        "hint": "Often called SDMA, located right near Block 32.",
        "lat": 31.2530,
        "lng": 75.7020
    },
    {
        "id": "loc_3",
        "name": "Uni Mall",
        "question": "The bustling hub where students shop and eat together.", 
        "answer": "uni mall",
        "hint": "It has Dominos, stationery shops, and lots of food!",
        "lat": 31.2505,
        "lng": 75.7015
    },
    {
        "id": "loc_4",
        "name": "Central Library",
        "question": "The place with thousands of books, where knowledge sleeps.", 
        "answer": "library",
        "hint": "It's the Central Library! Look for the large building with silence inside.",
        "lat": 31.2480,
        "lng": 75.7000
    },
    {
        "id": "loc_5",
        "name": "Unipolis",
        "question": "The massive open ground where mega events and concerts happen.", 
        "answer": "unipolis",
        "hint": "Baldev Raj Mittal Unipolis. Ask anyone where the stage is!",
        "lat": 31.2465,
        "lng": 75.7010
    }
]

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

import re

def normalize_string(s):
    # Remove all non-alphanumeric characters (spaces, punctuation, etc.)
    return re.sub(r'[^a-z0-9]', '', s.lower())

def is_correct_guess(guess, correct_answer):
    norm_guess = normalize_string(guess)
    norm_correct = normalize_string(correct_answer)
    
    # Direct match after removing spaces/punctuation (e.g. "uni mall" == "unimall")
    if norm_guess == norm_correct:
        return True
        
    # Check if user typed a substantial substring (e.g. "mittal" inside "shanti devi mittal auditorium")
    if len(norm_guess) > 3 and norm_guess in norm_correct:
        return True
        
    return False

def get_user_data(user_id):
    db = load_db()
    if user_id not in db:
        db[user_id] = {
            "level": 0,
            "team_name": f"Team-{os.urandom(2).hex()}",
            "start_time": time.time(),
            "end_time": None,
            "completed": False,
            "hints_used": 0
        }
        save_db(db)
    return db[user_id]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/leaderboard")
def leaderboard():
    db = load_db()
    completed_teams = []
    for user_id, data in db.items():
        if data.get("completed", False):
            total_duration = data.get("end_time", 0) - data.get("start_time", 0)
            penalty = data.get("hints_used", 0) * 300
            final_score = total_duration + penalty
            mins, secs = divmod(int(final_score), 60)
            
            completed_teams.append({
                "team": data.get("team_name", "Anonymous"),
                "duration_raw": final_score,
                "time_str": f"{mins}m {secs}s",
                "hints": data.get("hints_used", 0)
            })
    
    completed_teams.sort(key=lambda x: x["duration_raw"])
    return render_template("leaderboard.html", leaderboard=completed_teams)

@app.route("/map_data", methods=["POST"])
def get_map_data():
    data = request.json
    user_id = data.get("user_id", "default_user")
    user_data = get_user_data(user_id)
    level = user_data["level"]
    
    locations = []
    for i, clue in enumerate(CLUES):
        loc = {
            "id": clue["id"],
            "lat": clue["lat"],
            "lng": clue["lng"],
            "status": "locked",
            "question": None
        }
        if i < level:
            loc["status"] = "solved"
            loc["name"] = clue["name"]
        elif i == level:
            loc["status"] = "active"
            loc["question"] = clue["question"]
            
        locations.append(loc)
        
    return jsonify({
        "level": level,
        "completed": user_data.get("completed", False),
        "locations": locations
    })

@app.route("/guess", methods=["POST"])
def make_guess():
    data = request.json
    user_id = data.get("user_id")
    location_id = data.get("location_id")
    answer = data.get("answer", "").lower().strip()
    
    db = load_db()
    user_data = db.get(user_id)
    if not user_data:
        return jsonify({"success": False, "error": "Invalid user"})
        
    level = user_data["level"]
    
    if level >= len(CLUES):
        return jsonify({"success": False, "error": "Already finished"})
        
    current_clue = CLUES[level]
    
    if location_id != current_clue["id"]:
        return jsonify({"success": False, "error": "Wrong pin! Try the active pin."})
        
    if is_correct_guess(answer, current_clue["answer"]):
        user_data["level"] += 1
        level = user_data["level"]
        
        if level >= len(CLUES):
            user_data["completed"] = True
            user_data["end_time"] = time.time()
        
        save_db(db)
        return jsonify({"success": True})
    else:
        # Wrong answer triggers hint logic via frontend chatbot
        return jsonify({"success": False, "trigger_hint": True})

@app.route("/chat", methods=["POST"])
def chat():
    """ Handles strictly chatbot actions (like explicit hints or setup) """
    data = request.json
    user_id = data.get("user_id", "default_user")
    user_message = data.get("message", "").lower().strip()
    
    db = load_db()
    if user_id not in db:
        get_user_data(user_id) # initializes
    user_data = db[user_id]
    level = user_data["level"]

    if user_message == "/hint":
        if user_data.get("completed", False):
            return jsonify({"reply": "You've finished! No hints needed."})
            
        user_data["hints_used"] = user_data.get("hints_used", 0) + 1
        save_db(db)
        
        target_name = CLUES[level]["name"]
        hint_text = CLUES[level]["hint"]
        
        if GEMINI_AVAILABLE:
            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                # Domain-Specific Prompting & Model Configuration (Assessment Requirement)
                prompt = f"System Instruction: You are an expert guide for the Lovely Professional University (LPU) campus. Generate a short 1-sentence cryptic hint for a university location named '{target_name}'. Do not say the name directly.\n\n"
                
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.8, # Higher for creative, cryptic hints
                        top_p=0.9,
                    )
                )
                if response.text:
                    hint_text = response.text.replace('\n', '<br>')
            except Exception as e:
                print(f"Gemini API Error: {e}")
                
        return jsonify({"reply": f"<b>💡 AI Hint ({user_data['hints_used']} used - 5m penalty):</b><br>{hint_text}"})

    if user_message.startswith("/team "):
        team_name = user_message.split("/team ", 1)[1].strip()
        user_data["team_name"] = team_name
        save_db(db)
        return jsonify({"reply": f"Team name set to <b>{team_name}</b>! 🎉 Good luck!"})

    # If Gemini is configured, use it for generic chat!
    if GEMINI_AVAILABLE:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            # Strict Domain Constraint & Model Configuration (Assessment Requirement)
            domain_prompt = (
                "System Instruction: You are a helpful and mysterious tour guide for the LPU (Lovely Professional University) Campus Treasure Hunt. "
                "Your role is 'Domain Expert'. You must ONLY answer questions related to LPU, the campus, locations, or the treasure hunt game. "
                "If the user asks something outside of this domain, politely refuse and remind them of your purpose. "
                f"\n\nUser Question: {user_message}"
            )
            
            response = model.generate_content(
                domain_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4, # Lower for factual, domain-constrained answers
                    top_p=0.8,
                    max_output_tokens=150
                )
            )
            if response.text:
                return jsonify({"reply": f"{response.text.replace('\n', '<br>')}"})
        except Exception as e:
            pass
            
    # Default chatbot response if API key is not present
    return jsonify({"reply": "I am your Campus Guide interface! Ask for a <b>/hint</b> if you are stuck at your current location!"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
