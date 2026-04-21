import re

with open('app.py', 'r') as f:
    content = f.read()

# We will just parse the CLUES list and modify the coords slightly
# A simpler way is to just do a regex replace
import ast

match = re.search(r'CLUES = (\[.*?\])\n\n', content, re.DOTALL)
if match:
    clues_str = match.group(1)
    clues = ast.literal_eval(clues_str)
    
    # Add offset
    seen_coords = {}
    for clue in clues:
        coord = (clue["lat"], clue["lng"])
        if coord in seen_coords:
            count = seen_coords[coord]
            clue["lat"] = round(clue["lat"] - (0.0003 * count), 4)
            clue["lng"] = round(clue["lng"] + (0.0002 * count), 4)
            seen_coords[coord] = count + 1
        else:
            seen_coords[coord] = 1
            
    # Format back
    new_clues_str = "CLUES = [\n"
    for c in clues:
        new_clues_str += f'    {repr(c)},\n'
    new_clues_str += "]\n\n"
    
    content = content[:match.start()] + new_clues_str + content[match.end():]
    
    with open('app.py', 'w') as f:
        f.write(content)
        
    print("Coordinates fixed.")
else:
    print("Could not find CLUES")
