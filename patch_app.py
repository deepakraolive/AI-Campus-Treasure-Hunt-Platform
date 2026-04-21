import re

with open('app.py', 'r') as f:
    content = f.read()

new_clues = """CLUES = [
    {"id": "loc_1", "name": "Main Gate", "question": "I stand tall at the entrance, welcoming all who come to learn.", "answer": "main gate", "hint": "Look for the grand entrance.", "image": "Main Gate.jpeg", "lat": 31.2536, "lng": 75.7036},
    {"id": "loc_2", "name": "Main Gate", "question": "Security checks your ID here before you step into the campus universe.", "answer": "main gate", "hint": "Where do you first show your ID?", "image": "Main Gate.jpeg", "lat": 31.2536, "lng": 75.7036},
    {"id": "loc_3", "name": "Main Gate", "question": "The very first landmark you cross when arriving from the highway.", "answer": "main gate", "hint": "The starting point of the campus.", "image": "Main Gate.jpeg", "lat": 31.2536, "lng": 75.7036},
    {"id": "loc_4", "name": "Admissions Block", "question": "The place where your journey at LPU officially began.", "answer": "admissions", "hint": "Where did you submit your forms?", "image": "Admission.jpeg", "lat": 31.2540, "lng": 75.7040},
    {"id": "loc_5", "name": "Admissions Block", "question": "Got questions about fees or courses? This is the building to visit.", "answer": "admissions", "hint": "Admissions happen here.", "image": "Admission.jpeg", "lat": 31.2540, "lng": 75.7040},
    
    {"id": "loc_6", "name": "Mittal School of Business", "question": "Entrepreneurs and managers are forged in this specific block.", "answer": "mittal school of business", "hint": "Also known as Block 32.", "image": "Mittal School of Business.jpeg", "lat": 31.2530, "lng": 75.7020},
    {"id": "loc_7", "name": "Mittal School of Business", "question": "This building sounds like a corporation, but it's a school inside LPU.", "answer": "mittal school of business", "hint": "Business students study here.", "image": "Mittal School of Business.jpeg", "lat": 31.2530, "lng": 75.7020},
    {"id": "loc_8", "name": "Mittal School of Business", "question": "Block 32's formal name honors a prominent family.", "answer": "mittal school of business", "hint": "Mittal is the name.", "image": "Mittal School of Business.jpeg", "lat": 31.2530, "lng": 75.7020},
    
    {"id": "loc_9", "name": "Unipolis", "question": "The massive open ground where mega events and concerts happen.", "answer": "unipolis", "hint": "Baldev Raj Mittal Unipolis.", "image": "Uni Polis.jpeg", "lat": 31.2465, "lng": 75.7010},
    {"id": "loc_10", "name": "Unipolis", "question": "Where thousands gather to celebrate festivals and watch celebrity performances.", "answer": "unipolis", "hint": "It's the central open stage area.", "image": "Uni Polis.jpeg", "lat": 31.2465, "lng": 75.7010},
    {"id": "loc_11", "name": "Unipolis", "question": "A semi-covered arena that is the heart of cultural activities.", "answer": "unipolis", "hint": "Sounds like 'University Metropolis'.", "image": "Uni Polis.jpeg", "lat": 31.2465, "lng": 75.7010},
    {"id": "loc_12", "name": "Student Welfare Wing", "question": "Need to resolve a grievance or join a club? Head here.", "answer": "student welfare", "hint": "They care for your welfare.", "image": "Student Welfare wing.jpeg", "lat": 31.2470, "lng": 75.7015},
    {"id": "loc_13", "name": "Student Welfare Wing", "question": "The department dedicated to student affairs and extracurriculars.", "answer": "student welfare", "hint": "SWW is the acronym.", "image": "Student Welfare wing.jpeg", "lat": 31.2470, "lng": 75.7015},
    {"id": "loc_14", "name": "Student Welfare Wing", "question": "Where student organizations and event permissions are managed.", "answer": "student welfare", "hint": "Welfare is their middle name.", "image": "Student Welfare wing.jpeg", "lat": 31.2470, "lng": 75.7015},
    
    {"id": "loc_15", "name": "Design (Fashion) Block", "question": "Where creativity flows and fabrics turn into masterpieces.", "answer": "design block", "hint": "Fashion students are found here.", "image": "Design(Fashion) Block.jpeg", "lat": 31.2485, "lng": 75.6990},
    {"id": "loc_16", "name": "Design (Fashion) Block", "question": "Mannequins and sewing machines are common sights in this building.", "answer": "design block", "hint": "It's the fashion hub.", "image": "Design(Fashion) Block.jpeg", "lat": 31.2485, "lng": 75.6990},
    {"id": "loc_17", "name": "Robo Park", "question": "A park where technology meets nature, filled with metallic structures.", "answer": "robo park", "hint": "Robots in a park.", "image": "Robo Park.jpeg", "lat": 31.2490, "lng": 75.6980},
    
    {"id": "loc_18", "name": "Gyan Joti", "question": "A place of light and knowledge, providing spiritual and mental peace.", "answer": "gyan joti", "hint": "Gyan means knowledge.", "image": "Gyan Joti.jpeg", "lat": 31.2500, "lng": 75.6970},
    {"id": "loc_19", "name": "Gyan Joti", "question": "This structure is symbolic of enlightenment on campus.", "answer": "gyan joti", "hint": "Look for the light.", "image": "Gyan Joti.jpeg", "lat": 31.2500, "lng": 75.6970},
    {"id": "loc_20", "name": "Uni Hospital", "question": "Where you go when you're feeling under the weather on campus.", "answer": "uni hospital", "hint": "The medical facility.", "image": "Uni Hospital.jpeg", "lat": 31.2510, "lng": 75.6960}
]"""

# Replace CLUES
content = re.sub(r'CLUES = \[.*?\]\n', new_clues + '\n', content, flags=re.DOTALL)

# Default user initialization: Add registered flag and team details
user_data_func = """def get_user_data(user_id):
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
            "hints_used": 0
        }
        save_db(db)
    return db[user_id]"""

content = re.sub(r'def get_user_data\(user_id\):.*?return db\[user_id\]', user_data_func, content, flags=re.DOTALL)

# Add /register route
register_route = """@app.route("/register", methods=["POST"])
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
    return jsonify({"success": True})"""

content = content.replace('@app.route("/")', register_route + '\n\n@app.route("/")')

# modify map_data to return registered state
map_data_patch = """@app.route("/map_data", methods=["POST"])
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
    })"""

content = re.sub(r'@app.route\("/map_data", methods=\["POST"\]\).*?return jsonify\(\{[^}]+\}\)', map_data_patch, content, flags=re.DOTALL)

# modify /guess to return image
guess_patch = """@app.route("/guess", methods=["POST"])
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
        return jsonify({"success": True, "image": current_clue["image"], "name": current_clue["name"]})
    else:
        # Wrong answer triggers hint logic via frontend chatbot
        return jsonify({"success": False, "trigger_hint": True})"""

content = re.sub(r'@app.route\("/guess", methods=\["POST"\]\).*?return jsonify\(\{"success": False, "trigger_hint": True\}\)', guess_patch, content, flags=re.DOTALL)

with open('app.py', 'w') as f:
    f.write(content)
