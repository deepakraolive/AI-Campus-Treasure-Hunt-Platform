import re
import ast

with open('app.py', 'r') as f:
    content = f.read()

match = re.search(r'CLUES = (\[.*?\])\n\n', content, re.DOTALL)
if match:
    clues_str = match.group(1)
    clues = ast.literal_eval(clues_str)
    
    # Adjust loc_1 to loc_3 to 31.2554, 75.7058 (with slight offset)
    for i, clue in enumerate(clues[:3]):
        clue["lat"] = round(31.2554 - (0.0003 * i), 4)
        clue["lng"] = round(75.7058 + (0.0002 * i), 4)
        
    new_clues_str = "CLUES = [\n"
    for c in clues:
        new_clues_str += f'    {repr(c)},\n'
    new_clues_str += "]\n\n"
    
    content = content[:match.start()] + new_clues_str + content[match.end():]
    
    with open('app.py', 'w') as f:
        f.write(content)
        
    print("Main Gate shifted.")
