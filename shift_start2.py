import re
import ast

with open('app.py', 'r') as f:
    content = f.read()

match = re.search(r'CLUES = (\[.*?\])\n\n', content, re.DOTALL)
if match:
    clues_str = match.group(1)
    clues = ast.literal_eval(clues_str)
    
    # User says Main Gate is near Bismillah Biryani (Law Gate area).
    # Approximate coordinates for Law Gate food area: 31.2585, 75.7065
    for i, clue in enumerate(clues[:3]):
        clue["lat"] = round(31.2585 - (0.0003 * i), 4)
        clue["lng"] = round(75.7065 + (0.0002 * i), 4)
        
    new_clues_str = "CLUES = [\n"
    for c in clues:
        new_clues_str += f'    {repr(c)},\n'
    new_clues_str += "]\n\n"
    
    content = content[:match.start()] + new_clues_str + content[match.end():]
    
    with open('app.py', 'w') as f:
        f.write(content)
        
    print("Main Gate shifted to Bismillah Biryani / Law Gate area.")
