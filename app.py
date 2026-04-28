import os
import json
import time
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Attempt to import google-generativeai for AI Engine feature
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from groq import Groq
    if "GROQ_API_KEY" in os.environ:
        client = Groq(api_key=os.environ["GROQ_API_KEY"])
        GROQ_AVAILABLE = True
    else:
        GROQ_AVAILABLE = False
except ImportError:
    GROQ_AVAILABLE = False

if os.environ.get("VERCEL"):
    DB_FILE = '/tmp/database.json'
else:
    DB_FILE = 'database.json'

# Hardcoded LPU Specific Clues with Coordinates (Shuffled for variety)
CLUES = [
    {'id': 'loc_1', 'name': 'Main Gate', 'question': 'I stand tall at the entrance, welcoming all who come to learn.', 'answer': 'main gate', 'hint': 'Look for the grand entrance.', 'image': 'main_gate.jpeg', 'lat': 31.2585, 'lng': 75.7065},
    {'id': 'loc_4', 'name': 'Admissions Block', 'question': 'The place where your journey at LPU officially began.', 'answer': 'admissions', 'hint': 'Where did you submit your forms?', 'image': 'admission.jpeg', 'lat': 31.254, 'lng': 75.704},
    {'id': 'loc_6', 'name': 'Mittal School of Business', 'question': 'Entrepreneurs and managers are forged in this specific block.', 'answer': 'mittal school of business', 'hint': 'Also known as Block 14.', 'image': 'mittal_school.jpeg', 'lat': 31.253, 'lng': 75.702},
    {'id': 'loc_9', 'name': 'Unipolis', 'question': 'The massive open ground where mega events and concerts happen.', 'answer': 'unipolis', 'hint': 'Baldev Raj Mittal Unipolis.', 'image': 'unipolis.jpeg', 'lat': 31.2465, 'lng': 75.701},
    {'id': 'loc_12', 'name': 'Student Welfare Wing', 'question': 'Need to resolve a grievance or join a club? Head here.', 'answer': 'student welfare', 'hint': 'They care for your welfare.', 'image': 'student_welfare.jpeg', 'lat': 31.247, 'lng': 75.7015},
    {'id': 'loc_15', 'name': 'Design (Fashion) Block', 'question': 'Where creativity flows and fabrics turn into masterpieces.', 'answer': 'design block', 'hint': 'Fashion students are found here.', 'image': 'design_block.jpeg', 'lat': 31.2485, 'lng': 75.699},
    {'id': 'loc_17', 'name': 'Robo Park', 'question': 'A park where technology meets nature, filled with metallic structures.', 'answer': 'robo park', 'hint': 'Robots in a park.', 'image': 'robo_park.jpeg', 'lat': 31.249, 'lng': 75.698},
    {'id': 'loc_18', 'name': 'Gyan Joti', 'question': 'A place of light and knowledge, providing spiritual and mental peace.', 'answer': 'gyan joti', 'hint': 'Gyan means knowledge.', 'image': 'gyan_joti.jpeg', 'lat': 31.25, 'lng': 75.697},
    {'id': 'loc_2', 'name': 'Main Gate', 'question': 'Security checks your ID here before you step into the campus universe.', 'answer': 'main gate', 'hint': 'Where do you first show your ID?', 'image': 'main_gate.jpeg', 'lat': 31.2582, 'lng': 75.7067},
    {'id': 'loc_7', 'name': 'Mittal School of Business', 'question': "This building sounds like a corporation, but it's a school inside LPU.", 'answer': 'mittal school of business', 'hint': 'Business students study here.', 'image': 'mittal_school.jpeg', 'lat': 31.2527, 'lng': 75.7022},
    {'id': 'loc_10', 'name': 'Unipolis', 'question': 'Where thousands gather to celebrate festivals and watch celebrity performances.', 'answer': 'unipolis', 'hint': "It's the central open stage area.", 'image': 'unipolis.jpeg', 'lat': 31.2462, 'lng': 75.7012},
    {'id': 'loc_13', 'name': 'Student Welfare Wing', 'question': 'The department dedicated to student affairs and extracurriculars.', 'answer': 'student welfare', 'hint': 'SWW is the acronym.', 'image': 'student_welfare.jpeg', 'lat': 31.2467, 'lng': 75.7017},
    {'id': 'loc_20', 'name': 'Uni Hospital', 'question': "Where you go when you're feeling under the weather on campus.", 'answer': 'uni hospital', 'hint': 'The medical facility.', 'image': 'uni_hospital.jpeg', 'lat': 31.251, 'lng': 75.696},
    {'id': 'loc_5', 'name': 'Admissions Block', 'question': 'Got questions about fees or courses? This is the building to visit.', 'answer': 'admissions', 'hint': 'Admissions happen here.', 'image': 'admission.jpeg', 'lat': 31.2537, 'lng': 75.7042},
    {'id': 'loc_3', 'name': 'Main Gate', 'question': 'The very first landmark you cross when arriving from the highway.', 'answer': 'main gate', 'hint': 'The starting point of the campus.', 'image': 'main_gate.jpeg', 'lat': 31.2579, 'lng': 75.7069},
    {'id': 'loc_8', 'name': 'Mittal School of Business', 'question': "Block 14's formal name honors a prominent family.", 'answer': 'mittal school of business', 'hint': 'Mittal is the name.', 'image': 'mittal_school.jpeg', 'lat': 31.2524, 'lng': 75.7024},
    {'id': 'loc_11', 'name': 'Unipolis', 'question': 'A semi-covered arena that is the heart of cultural activities.', 'answer': 'unipolis', 'hint': "Sounds like 'University Metropolis'.", 'image': 'unipolis.jpeg', 'lat': 31.2459, 'lng': 75.7014},
    {'id': 'loc_14', 'name': 'Student Welfare Wing', 'question': 'Where student organizations and event permissions are managed.', 'answer': 'student welfare', 'hint': 'Welfare is their middle name.', 'image': 'student_welfare.jpeg', 'lat': 31.2464, 'lng': 75.7019},
    {'id': 'loc_16', 'name': 'Design (Fashion) Block', 'question': 'Mannequins and sewing machines are common sights in this building.', 'answer': 'design block', 'hint': "It's the fashion hub.", 'image': 'design_block.jpeg', 'lat': 31.2482, 'lng': 75.6992},
    {'id': 'loc_19', 'name': 'Gyan Joti', 'question': 'This structure is symbolic of enlightenment on campus.', 'answer': 'gyan joti', 'hint': 'Look for the light.', 'image': 'gyan_joti.jpeg', 'lat': 31.2497, 'lng': 75.6972},
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

def evaluate_guess_with_ai(guess, location_name):
    if not GROQ_AVAILABLE:
        return False
    try:
        sys_prompt = f"You are validating answers for a university treasure hunt. The correct location is '{location_name}'. The user guessed '{guess}'. Is this guess correct? It might be an alternate name or abbreviation (like 'Block 14' for 'Mittal School of Business', or 'Admissions' for 'Admissions Block'). Reply strictly with exactly 'YES' if it is reasonably correct or 'NO' if it is incorrect."
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": sys_prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.1,
            max_tokens=5
        )
        return "YES" in chat_completion.choices[0].message.content.strip().upper()
    except Exception as e:
        print(f"AI evaluation error: {e}")
        return False

def is_correct_guess(guess, correct_answer):
    norm_guess = normalize_string(guess)
    norm_correct = normalize_string(correct_answer)
    
    # Basic stemming (remove trailing 's')
    stem_guess = norm_guess[:-1] if norm_guess.endswith('s') else norm_guess
    stem_correct = norm_correct[:-1] if norm_correct.endswith('s') else norm_correct
    
    if stem_guess == stem_correct:
        return True
        
    if len(stem_guess) > 3 and stem_guess in stem_correct:
        return True
        
    if len(stem_correct) > 3 and stem_correct in stem_guess:
        return True
        
    return False

def get_user_data(user_id):
    db = load_db()
    if user_id not in db:
        db[user_id] = {
            "level": 0,
            "team_name": f"Team-{os.urandom(2).hex()}",
            "registered": False,
            "members": "",
            "start_time": time.time(),
            "end_time": None,
            "completed": False,
            "hints_used": 0,
            "failed_attempts_current_level": 0
        }
        save_db(db)
    return db[user_id]

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    user_id = data.get("user_id")
    team_name = data.get("team_name")
    members = data.get("members")
    
    db = load_db()
    if user_id not in db:
        get_user_data(user_id)
        db = load_db()
        
    user_data = db[user_id]
    user_data["team_name"] = team_name
    user_data["members"] = members
    user_data["registered"] = True
    save_db(db)
    return jsonify({"success": True})

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
            "question": None,
            "game_level": 1 if i < 5 else 2 if i < 8 else 3 if i < 14 else 4 if i < 17 else 5
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
        "registered": user_data.get("registered", False),
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
        
    # Try basic string match first
    is_correct = is_correct_guess(answer, current_clue["answer"])
    
    # If basic match fails, fallback to AI logic (if plausible length)
    if not is_correct and len(answer) > 2:
        is_correct = evaluate_guess_with_ai(answer, current_clue["name"])

    if is_correct:
        user_data["level"] += 1
        user_data["failed_attempts_current_level"] = 0
        level = user_data["level"]
        
        if level >= len(CLUES):
            user_data["completed"] = True
            user_data["end_time"] = time.time()
        
        save_db(db)
        return jsonify({"success": True, "image": current_clue["image"], "name": current_clue["name"]})
    else:
        # Wrong answer logic
        failed = user_data.get("failed_attempts_current_level", 0) + 1
        user_data["failed_attempts_current_level"] = failed
        
        if failed >= 3:
            # Auto-solve after 3 failed attempts
            user_data["level"] += 1
            user_data["failed_attempts_current_level"] = 0
            level = user_data["level"]
            
            if level >= len(CLUES):
                user_data["completed"] = True
                user_data["end_time"] = time.time()
                
            save_db(db)
            return jsonify({
                "success": True,
                "auto_solved": True,
                "image": current_clue["image"],
                "name": current_clue["name"]
            })
            
        save_db(db)
        return jsonify({
            "success": False, 
            "trigger_hint": True, 
            "error": f"Incorrect! ({3 - failed} attempts left)"
        })

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
        
        if GROQ_AVAILABLE:
            try:
                # Domain-Specific Prompting & Model Configuration (Assessment Requirement)
                sys_prompt = f"You are an expert guide for the Lovely Professional University (LPU) campus. Generate a short 1-sentence cryptic hint for a university location named '{target_name}'. Do not say the name directly."
                
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "system", "content": sys_prompt}],
                    model="llama-3.1-8b-instant",
                    temperature=0.8, # Higher for creative, cryptic hints
                    top_p=0.9,
                )
                if chat_completion.choices[0].message.content:
                    hint_text = chat_completion.choices[0].message.content.replace('\n', '<br>')
            except Exception as e:
                print(f"Groq API Error: {e}")
                
        return jsonify({"reply": f"<b>💡 AI Hint ({user_data['hints_used']} used - 5m penalty):</b><br>{hint_text}"})

    if user_message.startswith("/team "):
        team_name = user_message.split("/team ", 1)[1].strip()
        user_data["team_name"] = team_name
        save_db(db)
        return jsonify({"reply": f"Team name set to <b>{team_name}</b>! 🎉 Good luck!"})

    # If Groq is configured, use it for generic chat!
    if GROQ_AVAILABLE:
        try:
            # Strict Domain Constraint & Model Configuration (Assessment Requirement)
            sys_prompt = (
                "You are a helpful and mysterious tour guide for the LPU (Lovely Professional University) Campus Treasure Hunt. "
                "Your role is 'Domain Expert'. You must ONLY answer questions related to LPU, the campus, locations, or the treasure hunt game. "
                "If the user asks something outside of this domain, politely refuse and remind them of your purpose."
            )
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": user_message}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.4, # Lower for factual, domain-constrained answers
                top_p=0.8,
                max_tokens=150
            )
            if chat_completion.choices[0].message.content:
                return jsonify({"reply": f"{chat_completion.choices[0].message.content.replace('\n', '<br>')}"})
        except Exception as e:
            pass
            
    # Default chatbot response if API key is not present
    return jsonify({"reply": "I am your Campus Guide interface! Ask for a <b>/hint</b> if you are stuck at your current location!"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
